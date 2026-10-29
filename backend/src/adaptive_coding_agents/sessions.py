"""Local session handles; coding history stays in the Codex thread, never Jev."""

import json
from pathlib import Path
from uuid import UUID, uuid4

from .records import ContractError
from .run_records import _write_json
from .workflow_records import now


class SessionState:
    def __init__(self, root: Path, cwd: Path, budget_file: Path, session_id: str | None):
        if session_id is not None:
            try:
                if str(UUID(session_id)) != session_id:
                    raise ValueError
            except ValueError:
                raise ContractError("invalid_session", "Use the session_id printed by a previous run.") from None
        self.id = session_id or str(uuid4())
        self.path = root.resolve() / "sessions" / self.id / "session.json"
        if session_id:
            try:
                self.data = json.loads(self.path.read_text())
                if self.data["schema_version"] != "coding-session-1" or self.data["session_id"] != session_id:
                    raise ValueError
                if (not isinstance(self.data["turns"], list) or
                        (self.data["thread_id"] is not None and not isinstance(self.data["thread_id"], str)) or
                        (self.data["last_configuration"] is not None and not isinstance(self.data["last_configuration"], dict))):
                    raise ValueError
                if self.data["cwd"] != str(cwd) or self.data["budget_file"] != str(budget_file.resolve()):
                    raise ContractError("session_mismatch", "Resume with the original workspace and budget file.")
                if self.data["status"] != "ready":
                    raise ContractError("session_uncertain", "The previous turn is pending or uncertain. Inspect its record before resuming; no replay will occur.")
            except (OSError, KeyError, ValueError) as exc:
                if isinstance(exc, ContractError):
                    raise
                raise ContractError("invalid_session", "The session is missing or invalid.") from None
        else:
            self.data = {"schema_version": "coding-session-1", "session_id": self.id,
                "cwd": str(cwd), "budget_file": str(budget_file.resolve()), "created_at": now(),
                "thread_id": None, "status": "ready", "turns": [], "last_configuration": None}
            self.path.parent.mkdir(parents=True, mode=0o700)
            self.save()

    def save(self):
        try:
            _write_json(self.path, self.data)
        except OSError:
            raise ContractError("session_storage_error", "Unable to save session state. Inspect the workflow record before resuming.") from None

    def begin(self, record_path: Path):
        self.data.update(status="pending", active_record_path=str(record_path))
        self.save()

    def finish(self, record: dict, *, uncertain: bool):
        self.data["thread_id"] = record.get("thread_id") or self.data["thread_id"]
        self.data["status"] = "blocked" if uncertain else "ready"
        self.data["turns"].append({"record_path": self.data["active_record_path"],
            "turn_id": record.get("turn_id"), "status": record["status"], "prompt_sha256": record["prompt_sha256"]})
        if record.get("route"):
            self.data["last_configuration"] = record["route"]["configuration"]
        self.save()
