"""One new user prompt on a new or resumed Codex thread, with persistent budgets."""

import math
from pathlib import Path
import threading

from .budget import BudgetLedger, JEV_RESERVATION, coding_reservation
from .classification import classify_with_budget
from .codex_session import CodexSession
from .credentials import validate_openai_key
from .jev import JevClient, JevError
from .records import ContractError, Labels, PromptRecord
from .routing import CONFIGURATIONS, DEFAULT_FALLBACK, select_route
from .run_records import RunRecordError
from .sessions import SessionState
from .taxonomy import TAXONOMY_VERSION
from .workflow_records import WorkflowRecord, WorkflowRecordError


def validate_run(cwd: Path, timeout_seconds: float) -> Path:
    cwd = cwd.resolve()
    if not cwd.is_dir():
        raise ContractError("invalid_workspace", "The coding workspace must be an existing directory.")
    if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 600:
        raise ContractError("invalid_timeout", "The integration timeout must be greater than zero and at most 600 seconds.")
    return cwd


def check_codex(*, cwd: Path, openai_api_key: str, run_dir: Path,
                timeout_seconds: float, approval_handler, emit) -> dict:
    """Explicit authentication/catalog preflight; no classification or coding."""
    cwd = validate_run(cwd, timeout_seconds)
    validate_openai_key(openai_api_key)
    record = WorkflowRecord(run_dir, PromptRecord.capture("Codex preflight; no inference"), cwd, timeout_seconds)
    try:
        with CodexSession(cwd, timeout_seconds=timeout_seconds, openai_api_key=openai_api_key,
                          approval_handler=approval_handler, emit=emit, record=record) as client:
            client.eligible_configurations()
        return record.finish("completed", kind="preflight", inference_requested=False)
    except ContractError as exc:
        return record.finish("error", error={"code": exc.code, "message": str(exc)})
    except Exception:
        return record.finish("error", error={"code": "codex_preflight_failed", "message": "Codex preflight failed; no inference was requested. Provider details are withheld to protect credentials."})


def run_prompt(prompt: str, *, cwd: Path, api_key: str, openai_api_key: str,
               run_dir: Path, budget_file: Path, timeout_seconds: float, approval_handler, emit,
               session_id: str | None = None, fallback_id: str = DEFAULT_FALLBACK,
               cancel_event: threading.Event | None = None) -> dict:
    """Shared execution path for the terminal and future benchmark controller.

    Each invocation submits one user turn. Only the exact current prompt and fixed
    taxonomy reach Jev; Codex resumes its own history by the stored thread ID.
    """
    captured = PromptRecord.capture(prompt)
    cwd = validate_run(cwd, timeout_seconds)
    record = WorkflowRecord(run_dir, captured, cwd, timeout_seconds)
    client = state = None
    coding_entry = None
    with BudgetLedger(budget_file) as ledger:
        try:
            if cancel_event is not None and cancel_event.is_set():
                raise ContractError("cancelled", "Stopped before provider dispatch.")
            ledger.require()
            JevClient(api_key)
            validate_openai_key(openai_api_key)
            if fallback_id not in {c.id for c in CONFIGURATIONS}:
                raise ContractError("invalid_fallback", "Choose a registry configuration as fallback.")
            ledger.check("jev", JEV_RESERVATION)
            ledger.check("openai", min(coding_reservation(c.model) for c in CONFIGURATIONS))
            state = SessionState(run_dir, cwd, budget_file, session_id)
            state.begin(record.path)
            record.update(session_id=state.id, session_path=str(state.path),
                resumed=state.data["thread_id"] is not None, budget_file=str(ledger.path),
                previous_configuration=state.data["last_configuration"])
            emit("session/opened", {"session_id": state.id, "resumed": record.data["resumed"]})
            client = CodexSession(cwd, timeout_seconds=timeout_seconds, openai_api_key=openai_api_key,
                                 approval_handler=approval_handler, emit=emit, record=record, cancel_event=cancel_event)
            with client:
                supported = client.eligible_configurations()
                eligible = {c.id for c in CONFIGURATIONS if c.id in supported and
                            coding_reservation(c.model) <= ledger.remaining("openai")}
                if not eligible:
                    raise ContractError("budget_exhausted", "No supported configuration fits the remaining coding budget.")
                record.update(stage="classification", budget_eligible_configurations=sorted(eligible))
                if cancel_event is not None and cancel_event.is_set():
                    raise ContractError("cancelled", "Stopped before classification.")
                classified = classify_with_budget(prompt, api_key=api_key, ledger=ledger,
                                                   run_dir=record.path.parent / "jev")
                record.update(classifier_record_path=classified["record_path"])
                if cancel_event is not None and cancel_event.is_set():
                    raise ContractError("cancelled", "Stopped after classification; no coding turn was submitted.")
                if classified["status"] != "ok":
                    raise ContractError("classification_failed", "Jev did not return usable labels. Inspect its attempt record; no coding turn was started.")
                if (classified.get("prompt_sha256") != captured.prompt_sha256 or
                        classified.get("taxonomy_version") != TAXONOMY_VERSION):
                    raise ContractError("classification_mismatch", "The classification does not match this prompt and taxonomy.")
                route = select_route(Labels.from_dict(classified["labels"]), eligible, fallback_id)
                reservation = coding_reservation(route.configuration.model)
                coding_entry = "coding-" + record.path.parent.name
                ledger.reserve(coding_entry, "openai", reservation)
                decision = route.to_dict()
                record.update(stage="routing", route=decision, coding_reservation_usd=str(reservation),
                    configuration_changed=(None if state.data["last_configuration"] is None else
                                           state.data["last_configuration"] != decision["configuration"]))
                emit("routing/selected", decision)
                status = client.execute(prompt, route.configuration, resume_thread_id=state.data["thread_id"],
                    reservation_usd=reservation, before_dispatch=lambda: ledger.dispatch(coding_entry))
                record.finish(status)
        except WorkflowRecordError:
            raise  # Leave pending reservations/session intact for manual recovery.
        except RunRecordError as exc:
            record.finish("error", classifier_record_path=str(exc.path), classifier_observed_result=exc.observed_result,
                          error={"code": "classifier_recording_error", "message": str(exc)})
        except (ContractError, JevError) as exc:
            record.finish("interrupted" if exc.code == "cancelled" else "error",
                          error={"code": exc.code, "message": str(exc)})
        except KeyboardInterrupt:
            record.finish("interrupted", error={"code": "interrupted", "message": "Stopped locally. In-flight usage may be uncertain; no replay was made."})
        except Exception:
            cancelled = cancel_event is not None and cancel_event.is_set()
            record.finish("interrupted" if cancelled else "error",
                error={"code": "cancelled" if cancelled else "coding_timeout" if client is not None and client.expired.is_set() else "codex_error",
                "message": "Codex stopped before a complete result was captured. No retry was made; inspect the record before another invocation."})

        if coding_entry is not None and coding_entry in ledger.data["entries"]:
            attempted = record.data["coding_request_attempted"]
            amount = "0" if attempted is False else None
            if record.data["status"] == "completed" and record.data.get("turn_completion_observed"):
                amount = (record.data.get("coding_admission_estimate") or {}).get("amount_usd")
            ledger.settle(coding_entry, amount=amount, attempted=attempted, record_path=str(record.path),
                observed_estimate=(record.data.get("coding_admission_estimate") or {}).get("amount_usd"))
        if ledger.data is not None:
            record.update(budget=ledger.summary())
            uncertain = any(e["status"] in ("pending", "uncertain") for e in ledger.data["entries"].values())
            record.update(accounting_status="uncertain" if uncertain else "estimated", continuation_allowed=not uncertain)
            if state is not None:
                state.finish(record.data, uncertain=uncertain)
        return {**record.data, "record_path": str(record.path)}
