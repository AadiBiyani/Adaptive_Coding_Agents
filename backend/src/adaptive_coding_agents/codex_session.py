"""One coding execution path using the pinned official Python app-server SDK.

Creating the adapter makes no calls. Only entering it starts Codex. The terminal
and future benchmark runner use this adapter; it does not implement agent tools.
"""

from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
import threading
import time
from typing import Callable

from openai_codex.client import CodexClient, CodexConfig
from openai_codex.generated.v2_all import ConfigReadResponse, ModelListResponse
from openai_codex.models import UnknownNotification

from .budget import coding_estimate, money
from .credentials import validate_openai_key
from .records import ContractError
from .routing import CONFIGURATIONS, Configuration
from .workflow_records import WorkflowRecord

SDK_VERSION = "0.163.0"
CODEX_PROVIDER = "adaptive-openai"


class CodexSession:
    def __init__(self, cwd: Path, *, timeout_seconds: float,
                 approval_handler: Callable, emit: Callable,
                 record: WorkflowRecord, openai_api_key: str,
                 client: CodexClient | None = None, cancel_event: threading.Event | None = None):
        self.record = record
        self.emit = emit
        self.cwd = cwd
        self.thread_id: str | None = None
        self.turn_id: str | None = None
        self._openai_api_key = openai_api_key
        self.expired = threading.Event()
        self.cancel_event = cancel_event
        self._watch_done = threading.Event()
        self._closed = False
        self._close_lock = threading.Lock()
        self._timer = threading.Timer(timeout_seconds, self._expire)
        self._timer.daemon = True
        self.client = client or CodexClient(
            CodexConfig(
                cwd=str(cwd), client_name="adaptive_coding_agents",
                client_title="Adaptive Coding Agents", experimental_api=False,
                config_overrides=(
                    'cli_auth_credentials_store="ephemeral"', 'forced_login_method="api"',
                    'model_provider="adaptive-openai"',
                    'model_providers.adaptive-openai.name="OpenAI"',
                    'model_providers.adaptive-openai.wire_api="responses"',
                    'model_providers.adaptive-openai.requires_openai_auth=true',
                    'model_providers.adaptive-openai.base_url="https://api.openai.com/v1"',
                    'service_tier="default"', 'features.multi_agent=false', 'web_search="disabled"',
                    'model_providers.adaptive-openai.request_max_retries=0',
                    'model_providers.adaptive-openai.stream_max_retries=0',
                    'shell_environment_policy.exclude=["*KEY*", "*TOKEN*", "*SECRET*"]',
                ),
                # SDK env values overlay the inherited environment. Blank this
                # key so Codex's tools cannot inherit the classifier credential.
                env={"TYPESAFE_API_KEY": "", "OPENAI_API_KEY": "", "CODEX_API_KEY": ""},
            ),
            approval_handler=approval_handler,
        )

    def _expire(self) -> None:
        self.expired.set()
        self.close()

    def _watch_cancel(self) -> None:
        while not self._watch_done.wait(0.1):
            if self.cancel_event is not None and self.cancel_event.is_set():
                self.close()  # Billing remains uncertain; workflow never replays.
                return

    def close(self) -> None:
        with self._close_lock:
            if not self._closed:
                self._closed = True
                self.client.close()

    def __enter__(self):
        validate_openai_key(self._openai_api_key)
        for distribution in ("openai-codex", "openai-codex-cli-bin"):
            if version(distribution) != SDK_VERSION:
                raise ContractError("runtime_version_mismatch", "Run uv sync to restore the pinned Codex SDK and runtime.")
        try:
            self.record.update(stage="codex_start")
            self.client.start()
            self._timer.start()
            if self.cancel_event is not None:
                threading.Thread(target=self._watch_cancel, daemon=True).start()
            self.record.update(stage="codex_initialize")
            self.client.initialize()
            self.record.update(codex_sdk_version=SDK_VERSION, codex_runtime_version=SDK_VERSION)
            self.record.update(stage="codex_config")
            effective = self.client.request("config/read", {"cwd": str(self.cwd), "includeLayers": False},
                                            response_model=ConfigReadResponse).config.model_dump(mode="json")
            if effective.get("cli_auth_credentials_store") != "ephemeral":
                raise ContractError("credential_store_mismatch", "Codex did not confirm in-memory credential storage. The API key was not sent.")
            # Explicit API authentication for this process. Never silently use
            # the owner's ChatGPT subscription or overwrite stored login state.
            self.record.update(stage="codex_authentication")
            self.client.account_login_start({"type": "apiKey", "apiKey": self._openai_api_key})
            account = self.client.account_read({"refreshToken": False})
            if account.account is None or account.account.model_dump(mode="json").get("type") != "apiKey":
                raise ContractError("authentication_mismatch", "Codex did not confirm API-key authentication; no inference was started.")
            self.record.update(authentication="apiKey", billing_path="openai_api",
                               credentials_store="ephemeral", requested_provider_retries=0)
            return self
        except BaseException:
            self._watch_done.set()
            self._timer.cancel()
            self.close()
            raise

    def __exit__(self, *_):
        self._watch_done.set()
        self._timer.cancel()
        self.close()

    def eligible_configurations(self) -> set[str]:
        """Read all catalog pages, without assuming API docs imply access."""
        self.record.update(stage="model_catalog")
        cursor = None
        seen = set()
        supported = set()
        for _ in range(100):
            params = {"limit": 100, "includeHidden": False}
            if cursor is not None:
                params["cursor"] = cursor
            page = self.client.request("model/list", params, response_model=ModelListResponse)
            for model in page.data:
                if model.hidden or (model.input_modalities is not None and
                                    "text" not in [item.value for item in model.input_modalities]):
                    continue
                for option in model.supported_reasoning_efforts:
                    supported.add((model.model, option.reasoning_effort.value))
            cursor = page.next_cursor
            if cursor is None:
                eligible = {config.id for config in CONFIGURATIONS
                            if (config.model, config.effort) in supported}
                self.record.update(eligible_configurations=sorted(eligible))
                if not eligible:
                    raise ContractError("no_eligible_configurations", "Codex lists none of the configured GPT model/effort pairs. No Jev request was sent.")
                return eligible
            if cursor in seen:
                break
            seen.add(cursor)
        raise ContractError("invalid_model_catalog", "Codex model pagination did not complete; no Jev request was sent.")

    def execute(self, prompt: str, configuration: Configuration, *,
                resume_thread_id: str | None = None, reservation_usd=None,
                before_dispatch: Callable = lambda: None) -> str:
        """Execute exactly one new user turn, with explicit model and effort.

        A completed turn is not a claim of task correctness. Codex's internal
        calls/retries and billed cost may not be exposed by the protocol.
        """
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise ContractError("cancelled", "Stopped before starting the coding turn.")
        stage = "thread_resume" if resume_thread_id else "thread_start"
        self.record.update(stage=stage, requested_configuration=asdict(configuration))
        params = {
            "cwd": str(self.cwd), "model": configuration.model, "modelProvider": CODEX_PROVIDER,
            "config": {"model_reasoning_effort": configuration.effort},
            "approvalPolicy": "on-request", "approvalsReviewer": "user",
            "sandbox": "workspace-write",
            "serviceTier": "default",
        }
        response = (self.client.thread_resume(resume_thread_id, {**params, "excludeTurns": True})
                    if resume_thread_id else self.client.thread_start(params))
        self.thread_id = response.thread.id
        accepted = {
            "model": response.model,
            "effort": response.reasoning_effort.value if response.reasoning_effort else None,
            "provider": response.model_provider,
            "service_tier": response.service_tier,
        }
        self.record.update(thread_id=self.thread_id, accepted_thread_configuration=accepted)
        if ((resume_thread_id is not None and self.thread_id != resume_thread_id) or
                Path(response.cwd.model_dump(mode="json")).resolve() != self.cwd or
                Path(response.thread.cwd.model_dump(mode="json")).resolve() != self.cwd):
            raise ContractError("thread_mismatch", "Codex returned a different thread or workspace; no turn was started.")
        if response.thread.status.model_dump(mode="json").get("type") != "idle":
            raise ContractError("thread_busy", "The Codex thread is not idle. No prompt was steered into an active turn.")
        if (response.approval_policy.model_dump(mode="json") != "on-request" or
                response.approvals_reviewer.value != "user" or
                response.sandbox.model_dump(mode="json").get("type") != "workspaceWrite"):
            raise ContractError("permission_mismatch", "Codex did not confirm interactive approvals and the workspace sandbox. No coding turn was started.")
        if response.service_tier not in (None, "default", "standard"):
            raise ContractError("unexpected_service_tier", "Codex selected a nonstandard service tier. Review its pricing before a coding turn.")
        if (accepted["model"], accepted["effort"], accepted["provider"]) != (
                configuration.model, configuration.effort, CODEX_PROVIDER):
            raise ContractError("configuration_mismatch", "Codex did not confirm the requested model, effort, and provider. No coding turn was started.")
        self.emit("configuration/accepted", accepted)
        if self.expired.is_set():
            raise ContractError("coding_timeout", "The local deadline expired before turn dispatch.")
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise ContractError("cancelled", "Stopped before turn dispatch.")
        # Persist the uncertain intent BEFORE dispatch. A transport failure can
        # occur after acceptance; never automatically replay turn/start.
        self.record.update(stage="turn_start", coding_request_attempted=None)
        before_dispatch()
        started = time.monotonic()
        response = self.client.turn_start(self.thread_id, prompt, {
            "model": configuration.model, "effort": configuration.effort,
            "approvalPolicy": "on-request", "approvalsReviewer": "user",
            "serviceTier": "default",
        })
        self.turn_id = response.turn.id
        self.record.update(turn_id=self.turn_id, coding_request_attempted=True,
                           turn_start_acknowledged=True, stage="coding")
        previous_usage = None
        try:
            while True:
                notification = self.client.next_turn_notification(self.turn_id)
                if isinstance(notification.payload, UnknownNotification):
                    # Silently accepting malformed completion/usage would turn
                    # unknown outcomes into apparently successful records.
                    if notification.method in ("turn/completed", "thread/tokenUsage/updated", "model/rerouted"):
                        raise ContractError("invalid_codex_event", "Codex returned an invalid completion or usage event.")
                    continue
                # Preserve absent telemetry instead of serializing SDK defaults
                # (e.g. an omitted cache-write count must not become zero).
                data = notification.payload.model_dump(by_alias=True, mode="json", exclude_unset=True)
                if data.get("threadId") != self.thread_id or data.get("turnId", self.turn_id) != self.turn_id:
                    raise ContractError("unexpected_codex_event", "A coding event belongs to a different thread or turn.")
                if notification.method == "thread/tokenUsage/updated":
                    usage = data["tokenUsage"]["total"]
                    if any(type(value) is not int or value < 0 for value in usage.values() if value is not None):
                        raise ContractError("invalid_codex_usage", "Codex returned invalid token counts.")
                    if previous_usage is not None and any(usage[k] < previous_usage[k] for k in ("inputTokens", "outputTokens")):
                        self.client.turn_interrupt(self.thread_id, self.turn_id)
                        raise ContractError("usage_reset", "Usage counters decreased during execution; accounting is uncertain.")
                    previous_usage = usage
                    # Never sum repeated cumulative events. On resume, we cannot
                    # assume whether the server restored or reset its counters.
                    # Charge full observed totals conservatively for admission,
                    # and leave actual per-turn experimental usage unavailable.
                    estimate = coding_estimate(usage, configuration.model)
                    self.record.update(coding_usage={"source": "codex_thread_total", **usage},
                        coding_turn_usage=None if resume_thread_id else usage,
                        coding_admission_estimate=estimate)
                    if estimate["amount_usd"] is None or (reservation_usd is not None and
                            money(estimate["amount_usd"]) >= money(reservation_usd)):
                        self.record.update(budget_interrupted=True)
                        self.client.turn_interrupt(self.thread_id, self.turn_id)
                        raise ContractError("turn_budget_reached", "Observed usage reached the turn reservation. Interrupted; final provider usage may still be pending.")
                elif notification.method == "model/rerouted":
                    self.record.update(observed_reroute={key: data.get(key) for key in ("fromModel", "toModel", "reason")})
                    self.client.turn_interrupt(self.thread_id, self.turn_id)
                    raise ContractError("model_rerouted", "Codex reported a model change; the turn was interrupted and is not a matched configuration run.")
                self.emit(notification.method, data)
                if notification.method == "turn/completed":
                    turn = data["turn"]
                    if turn["id"] != self.turn_id:
                        raise ContractError("unexpected_codex_event", "The completion belongs to another turn.")
                    self.record.update(coding_elapsed_ms=round((time.monotonic() - started) * 1000),
                                       turn_completion_observed=True)
                    return turn["status"]
        finally:
            self.client.unregister_turn_notifications(self.turn_id)
