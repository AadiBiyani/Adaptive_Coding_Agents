"""Orchestrate prompt-only classification, routing, and one Codex user turn."""

import math
from pathlib import Path

from .codex_session import CodexSession
from .jev import JevClient, JevError
from .records import ContractError, Labels, PromptRecord
from .routing import select_route
from .run_records import RunRecordError, classify_recorded
from .taxonomy import TAXONOMY_VERSION
from .workflow_records import WorkflowRecord, WorkflowRecordError


def run_prompt(prompt: str, *, cwd: Path, api_key: str, run_dir: Path,
               timeout_seconds: float, approval_handler, emit) -> dict:
    """One explicit invocation, no retries, no fabricated model predictions.

    This is the shared execution boundary for the terminal and later benchmarks.
    Do not put repository/history information into the classifier call below.
    """
    captured = PromptRecord.capture(prompt)
    cwd = cwd.resolve()
    if not cwd.is_dir():
        raise ContractError("invalid_workspace", "The coding workspace must be an existing directory.")
    if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 600:
        raise ContractError("invalid_timeout", "The integration timeout must be greater than zero and at most 600 seconds.")
    record = WorkflowRecord(run_dir, captured, cwd, timeout_seconds)
    session = None
    try:
        JevClient(api_key)  # Validate locally before starting Codex or contacting either provider.
        session = CodexSession(cwd, timeout_seconds=timeout_seconds,
                               approval_handler=approval_handler, emit=emit, record=record)
        with session:
            eligible = session.eligible_configurations()
            record.update(stage="classification")
            classified = classify_recorded(prompt, api_key=api_key, run_dir=record.path.parent / "jev")
            record.update(classifier_record_path=classified["record_path"])
            if classified["status"] != "ok":
                return record.finish(classified["status"], error={
                    "code": "classification_failed",
                    "message": "Jev did not return usable labels. Inspect its attempt record; no coding turn was started.",
                    "classifier_error_code": classified.get("error", {}).get("code"),
                })
            if (classified.get("prompt_sha256") != captured.prompt_sha256 or
                    classified.get("taxonomy_version") != TAXONOMY_VERSION):
                raise ContractError("classification_mismatch", "The classification does not match this prompt and taxonomy.")
            route = select_route(Labels.from_dict(classified["labels"]), eligible)
            record.update(stage="routing", route=route.to_dict())
            emit("routing/selected", route.to_dict())
            status = session.execute(prompt, route.configuration)
            return record.finish(status)
    except WorkflowRecordError:
        raise  # Includes the in-memory outcome; do not overwrite it with a new error.
    except RunRecordError as exc:
        return record.finish("error", classifier_record_path=str(exc.path),
                             classifier_observed_result=exc.observed_result,
                             error={"code": "classifier_recording_error", "message": str(exc)})
    except (ContractError, JevError) as exc:
        return record.finish("error", error={"code": exc.code, "message": str(exc)})
    except KeyboardInterrupt:
        return record.finish("interrupted", error={
            "code": "interrupted", "message": "The local workflow stopped. Inspect the saved attempt before retrying; provider work or usage may be uncertain.",
        })
    except Exception:
        # Transport errors can embed prompts, stderr, or account information.
        timed_out = session is not None and session.expired.is_set()
        return record.finish("error", error={
            "code": "coding_timeout" if timed_out else "codex_error",
            "message": "Codex stopped before a complete result was captured. No retry was made; inspect the record before another invocation.",
        })
