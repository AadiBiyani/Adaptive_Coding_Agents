"""Private local chat transcripts. Provider audit records remain separate."""

from copy import deepcopy
import json
from pathlib import Path
import threading
from uuid import UUID, uuid4

from .records import ContractError
from .run_records import _write_json
from .workflow_records import now


def identifier(value: str) -> str:
    try:
        if not isinstance(value, str) or str(UUID(value)) != value:
            raise ValueError
    except (ValueError, TypeError):
        raise ContractError("invalid_identifier", "The conversation or request ID is invalid.") from None
    return value


class ChatStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        self.chats = {}
        for path in self.root.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                identifier(data["id"])
                if data.get("schema_version") != "local-chat-1" or not isinstance(data["turns"], list):
                    continue
                if data["turns"] and data["turns"][-1]["status"] in ("running", "stopping"):
                    data["turns"][-1].update(status="interrupted", error="The local server stopped. Review spending before another prompt.")
                    data["revision"] += 1
                    _write_json(path, data)
                self.chats[data["id"]] = data
            except (OSError, ValueError, TypeError, KeyError):
                continue

    def _save(self, chat):
        chat["revision"] += 1
        chat["updated_at"] = now()
        _write_json(self.root / f"{chat['id']}.json", chat)

    def create(self, workspace: Path) -> dict:
        with self.lock:
            chat = {"schema_version": "local-chat-1", "id": str(uuid4()), "title": "New conversation",
                    "workspace": str(workspace), "session_id": None, "turns": [], "revision": 0,
                    "created_at": now(), "updated_at": now()}
            self._save(chat)
            self.chats[chat["id"]] = chat
            return deepcopy(chat)

    def get(self, chat_id: str) -> dict:
        with self.lock:
            identifier(chat_id)
            if chat_id not in self.chats:
                raise ContractError("chat_missing", "This conversation is not available.")
            return deepcopy(self.chats[chat_id])

    def update(self, chat_id: str, change) -> dict:
        with self.lock:
            chat = self.chats[identifier(chat_id)]
            change(chat)
            self._save(chat)
            return deepcopy(chat)

    def list(self) -> list[dict]:
        with self.lock:
            return [{key: chat[key] for key in ("id", "title", "workspace", "updated_at")}
                    for chat in sorted(self.chats.values(), key=lambda c: c["updated_at"], reverse=True)]
