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
from openai_codex.generated.v2_all import ModelListResponse
from openai_codex.models import UnknownNotification

from .records import ContractError
from .routing import CONFIGURATIONS, Configuration
from .workflow_records import WorkflowRecord

SDK_VERSION = "0.163.0"


class CodexSession:
    def __init__(self, cwd: Path, *, timeout_seconds: float,
                 approval_handler: Callable, emit: Callable,
                 record: WorkflowRecord, client: CodexClient | None = None):
        self.record = record
        self.emit = emit
        self.cwd = cwd
        self.thread_id: str | None = None
        self.turn_id: str | None = None
        self.expired = threading.Event()
        self._closed = False
        self._close_lock = threading.Lock()
        self._timer = threading.Timer(timeout_seconds, self._expire)
        self._timer.daemon = True
        self.client = client or CodexClient(
            CodexConfig(
                cwd=str(cwd), client_name="adaptive_coding_agents",
                client_title="Adaptive Coding Agents", experimental_api=False,
                # SDK env values overlay the inherited environment. Blank this
                # key so Codex's tools cannot inherit the classifier credential.
                env={"TYPESAFE_API_KEY": ""},
            ),
            approval_handler=approval_handler,
        )

    def _expire(self) -> None:
        self.expired.set()
        self.close()

    def close(self) -> None:
        with self._close_lock:
            if not self._closed:
                self._closed = True
                self.client.close()

    def __enter__(self):
        for distribution in ("openai-codex", "openai-codex-cli-bin"):
            if version(distribution) != SDK_VERSION:
                raise ContractError("runtime_version_mismatch", "Run uv sync to restore the pinned Codex SDK and runtime.")
        try:
            self.client.start()
            self._timer.start()
            self.client.initialize()
            self.record.update(codex_sdk_version=SDK_VERSION, codex_runtime_version=SDK_VERSION)
            return self
        except BaseException:
            self._timer.cancel()
            self.close()
            raise

    def __exit__(self, *_):
        self._timer.cancel()
        self.close()

    def eligible_configurations(self) -> set[str]:
        """Read all catalog pages, without assuming API docs imply access."""
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

    def execute(self, prompt: str, configuration: Configuration) -> str:
        """Execute exactly one new user turn, with explicit model and effort.

        A completed turn is not a claim of task correctness. Codex's internal
        calls/retries and billed cost may not be exposed by the protocol.
        """
        self.record.update(stage="thread_start", requested_configuration=asdict(configuration))
        response = self.client.thread_start({
            "cwd": str(self.cwd), "model": configuration.model, "modelProvider": "openai",
            "config": {"model_reasoning_effort": configuration.effort},
            "approvalPolicy": "on-request", "approvalsReviewer": "user",
            "sandbox": "workspace-write",
        })
        self.thread_id = response.thread.id
        accepted = {
            "model": response.model,
            "effort": response.reasoning_effort.value if response.reasoning_effort else None,
            "provider": response.model_provider,
            "service_tier": response.service_tier,
        }
        self.record.update(thread_id=self.thread_id, accepted_thread_configuration=accepted)
        if (response.approval_policy.model_dump(mode="json") != "on-request" or
                response.approvals_reviewer.value != "user" or
                response.sandbox.model_dump(mode="json").get("type") != "workspaceWrite"):
            raise ContractError("permission_mismatch", "Codex did not confirm interactive approvals and the workspace sandbox. No coding turn was started.")
        if response.service_tier not in (None, "default", "standard"):
            raise ContractError("unexpected_service_tier", "Codex selected a nonstandard service tier. Review its pricing before a coding turn.")
        if (accepted["model"], accepted["effort"], accepted["provider"]) != (
                configuration.model, configuration.effort, "openai"):
            raise ContractError("configuration_mismatch", "Codex did not confirm the requested model, effort, and provider. No coding turn was started.")
        self.emit("configuration/accepted", accepted)
        # Persist the uncertain intent BEFORE dispatch. A transport failure can
        # occur after acceptance; never automatically replay turn/start.
        self.record.update(stage="turn_start", coding_request_attempted=None)
        started = time.monotonic()
        response = self.client.turn_start(self.thread_id, prompt, {
            "model": configuration.model, "effort": configuration.effort,
            "approvalPolicy": "on-request", "approvalsReviewer": "user",
        })
        self.turn_id = response.turn.id
        self.record.update(turn_id=self.turn_id, coding_request_attempted=True,
                           turn_start_acknowledged=True, stage="coding")
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
                    # One fresh thread here: total is cumulative for this run.
                    # Replace it, never sum cumulative notifications.
                    self.record.update(coding_usage={"source": "codex_thread_total", **usage})
                elif notification.method == "model/rerouted":
                    self.record.update(observed_reroute={key: data.get(key) for key in ("fromModel", "toModel", "reason")})
                    self.client.turn_interrupt(self.thread_id, self.turn_id)
                    raise ContractError("model_rerouted", "Codex reported a model change; the turn was interrupted and is not a matched configuration run.")
                self.emit(notification.method, data)
                if notification.method == "turn/completed":
                    turn = data["turn"]
                    if turn["id"] != self.turn_id:
                        raise ContractError("unexpected_codex_event", "The completion belongs to another turn.")
                    self.record.update(coding_elapsed_ms=round((time.monotonic() - started) * 1000))
                    return turn["status"]
        finally:
            self.client.unregister_turn_notifications(self.turn_id)
