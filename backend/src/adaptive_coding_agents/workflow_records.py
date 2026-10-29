"""Private single-turn integration records; no prompt text or raw tool output."""

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .records import PromptRecord
from .run_records import _write_json


class WorkflowRecordError(RuntimeError):
    def __init__(self, path: Path, observed_result: dict):
        super().__init__("Could not save the workflow record. Preserve the observed result and inspect the record before retrying.")
        self.path = path
        self.observed_result = observed_result


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkflowRecord:
    def __init__(self, root: Path, prompt: PromptRecord, cwd: Path, timeout_seconds: float):
        self.path = root / str(uuid4()) / "workflow.json"
        self.data = {
            "schema_version": "coding-workflow-2",
            "status": "pending",
            "stage": "preflight",
            "started_at": now(),
            "finished_at": None,
            **asdict(prompt),
            "cwd": str(cwd),
            "timeout_seconds": timeout_seconds,
            "classifier_record_path": None,
            "route": None,
            "thread_id": None,
            "turn_id": None,
            "coding_request_attempted": False,
            "requested_configuration": None,
            "accepted_thread_configuration": None,
            "turn_start_acknowledged": False,
            "observed_execution_configuration": None,
            "coding_usage": None,
            "coding_turn_usage": None,
            "coding_admission_estimate": None,
            "turn_completion_observed": False,
            "coding_billed_cost_usd": None,
            "coding_internal_call_count": None,
            "coding_internal_retry_count": None,
            "task_success": None,
        }
        try:
            self.path.parent.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.path.parent.mkdir(mode=0o700)
        except OSError:
            raise WorkflowRecordError(self.path, self.data.copy()) from None
        self.update()

    def update(self, **changes) -> None:
        self.data.update(changes)
        try:
            _write_json(self.path, self.data)
        except OSError:
            raise WorkflowRecordError(self.path, self.data.copy()) from None

    def finish(self, status: str, **changes) -> dict:
        self.update(status=status, finished_at=now(), **changes)
        return {**self.data, "record_path": str(self.path)}
