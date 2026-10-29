"""Loopback-only browser UI over the existing coding workflow. No hosted service."""

from copy import deepcopy
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import parse_qs, unquote, urlsplit
from uuid import uuid4

from .budget import BudgetLedger, JEV_RESERVATION, coding_reservation, read_budget
from .credentials import Credentials
from .evaluations import EvaluationManager
from .price_comparison import compare_record
from .records import ContractError, PromptRecord
from .routing import CONFIGURATIONS
from .ui_store import ChatStore, identifier
from .workflow import run_prompt, validate_run
from .workflow_records import now

ASSETS = Path(__file__).parent / "web"
MAX_TEXT = 240_000
IGNORED_DIRS = {"node_modules", "__pycache__", "venv", "dist", "build"}


def read_json(path: Path):
    if path.stat().st_size > 8_000_000:
        raise ValueError("Record too large")
    return json.loads(path.read_text())


class LocalApp:
    def __init__(self, *, workspace: Path, run_dir: Path, chat_dir: Path, budget_file: Path,
                 credentials: Credentials, timeout_seconds: float = 180, workflow=run_prompt,
                 project_root: Path | None = None):
        self.workspace = validate_run(workspace, timeout_seconds)
        self.run_dir = run_dir.resolve()
        self.budget_file = budget_file.resolve()
        self.credentials = credentials
        self.timeout = timeout_seconds
        self.workflow = workflow
        self.store = ChatStore(chat_dir)
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.active = None
        self.evaluations = EvaluationManager(project_root=project_root or Path(__file__).resolve().parents[3],
            output_root=self.run_dir.parent / "evaluations", scrub=self.scrub)

    def scrub(self, value):
        if isinstance(value, str):
            for key in (self.credentials.typesafe, self.credentials.openai):
                if key:
                    value = value.replace(key, "[credential removed]")
            return value
        if isinstance(value, dict):
            return {k: self.scrub(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.scrub(v) for v in value]
        return value

    def budget(self):
        try:
            ledger = BudgetLedger(self.budget_file)
            ledger.data = read_budget(self.budget_file)  # Atomic read; never wait on a running turn's lock.
            result = ledger.summary()
            entries = result["entries"].values()
            used = {p: sum(e["provider"] == p and e["attempted"] is not False for e in entries)
                    for p in ("jev", "openai")}
            return {"available": True, "caps_usd": result["caps_usd"], "remaining_usd": result["remaining_usd"],
                    "attempt_limits": result["attempt_limits"], "attempts_used": used,
                    "uncertain": any(e["status"] in ("pending", "uncertain") for e in entries)}
        except (ContractError, OSError):
            return {"available": False, "error": "Initialize or inspect the existing budget from the terminal."}

    def bootstrap(self):
        with self.lock:
            active_chat = self.active["chat_id"] if self.active else None
        return {"token": self.token, "workspace": str(self.workspace), "chats": self.store.list(),
                "credentials_ready": bool(self.credentials.typesafe and self.credentials.openai),
                "configurations": [asdict(c) for c in CONFIGURATIONS], "budget": self.budget(),
                "active_chat": active_chat}

    def chat(self, chat_id):
        chat = self.store.get(chat_id)
        with self.lock:
            chat["approval"] = deepcopy(self.active.get("request")) if self.active and self.active["chat_id"] == chat_id else None
        return chat

    def submit(self, chat_id: str, prompt: str, submission_id: str):
        PromptRecord.capture(prompt)
        identifier(submission_id)
        with self.lock:
            chat = self.store.get(chat_id)
            if any(t["id"] == submission_id for t in chat["turns"]):
                return self.chat(chat_id)  # Duplicate HTTP submission never repeats paid work.
            if self.active is not None or self.evaluations.active is not None:
                raise ContractError("already_running", "Wait for the current response or test run to finish before sending another prompt.")
            if not self.credentials.typesafe or not self.credentials.openai:
                raise ContractError("missing_credentials", "Add both API keys to your local .env file and restart the UI server.")
            with BudgetLedger(self.budget_file) as ledger:
                ledger.check("jev", JEV_RESERVATION)
                ledger.check("openai", min(coding_reservation(c.model) for c in CONFIGURATIONS))
            cancel = threading.Event()
            job = {"chat_id": chat_id, "id": submission_id, "cancel": cancel,
                   "answer_ready": threading.Event(), "request": None, "answer": None,
                   "deadline": time.monotonic() + self.timeout}
            def begin(c):
                if not c["turns"]:
                    c["title"] = self.scrub(" ".join(prompt.split())[:64])
                c["turns"].append({"id": submission_id, "prompt": self.scrub(prompt), "status": "running",
                    "stage": "Classifying your prompt", "started_at": now(), "messages": [],
                    "activity": [], "files": [], "route": None, "error": None, "record_path": None})
            self.store.update(chat_id, begin)
            self.active = job
            threading.Thread(target=self._work, args=(job, chat, prompt), daemon=True).start()
            return self.chat(chat_id)

    def _emit(self, job, method, raw):
        data = self.scrub(raw)
        def update(c):
            turn = c["turns"][-1]
            if method == "session/opened":
                c["session_id"] = data["session_id"]
            elif method == "routing/selected":
                turn.update(route=data, stage="Starting coding agent")
            elif method == "configuration/accepted":
                turn.update(accepted=data, stage="Working")
            elif method in ("item/agentMessage/delta", "item/completed"):
                item = data.get("item", {})
                if method == "item/completed" and item.get("type") != "agentMessage":
                    self._activity(turn, method, data)
                    return
                item_id = data.get("itemId") or item.get("id") or "response"
                message = next((m for m in turn["messages"] if m["id"] == item_id), None)
                if message is None:
                    message = {"id": item_id, "text": ""}
                    turn["messages"].append(message)
                message["text"] = self.scrub((message["text"] + data.get("delta", "")) if method.endswith("/delta")
                                   else item.get("text", message["text"]))[:MAX_TEXT]
            elif method in ("item/started", "item/commandExecution/outputDelta", "item/fileChange/outputDelta"):
                self._activity(turn, method, data)
        if method in ("session/opened", "routing/selected", "configuration/accepted", "item/agentMessage/delta",
                      "item/completed", "item/started", "item/commandExecution/outputDelta", "item/fileChange/outputDelta"):
            self.store.update(job["chat_id"], update)

    def _activity(self, turn, method, data):
        item = data.get("item", {})
        if item.get("type") == "fileChange":
            for change in item.get("changes", []):
                path = change.get("path")
                if path and path not in turn["files"]:
                    turn["files"].append(path)
        if item.get("type") == "commandExecution" or method.endswith("/outputDelta"):
            item_id = data.get("itemId") or item.get("id")
            action = next((a for a in turn["activity"] if a["id"] == item_id), None)
            if action is None and len(turn["activity"]) < 100:
                action = {"id": item_id, "command": item.get("command", "Tool output"), "output": "", "status": "running"}
                turn["activity"].append(action)
            if action is not None:
                action["command"] = item.get("command", action["command"])
                action["output"] = self.scrub(item.get("aggregatedOutput") or (action["output"] + data.get("delta", "")))[:MAX_TEXT]
                action["status"] = item.get("status", action["status"])

    def _approve(self, job, method, params):
        allowed = ("item/commandExecution/requestApproval", "item/fileChange/requestApproval",
                   "item/permissions/requestApproval", "item/tool/requestUserInput", "tool/requestUserInput")
        if method == "mcpServer/elicitation/request":
            return {"action": "decline", "content": None}
        if method not in allowed:
            raise ContractError("unsupported_approval", "This approval type is not supported; nothing was approved.")
        params = params or {}
        with self.lock:
            job["answer_ready"].clear()
            job["request"] = {"id": str(uuid4()), "method": method, "params": self.scrub(params)}
            job["answer"] = None
        while time.monotonic() < job["deadline"] and not job["cancel"].is_set():
            if job["answer_ready"].wait(0.2):
                break
        with self.lock:
            answer = job["answer"] or {}
            job["request"] = None
        accepted = answer.get("decision") == "accept" and not job["cancel"].is_set()
        if method == "item/permissions/requestApproval":
            return {"permissions": params.get("permissions", {}) if accepted else {}, "scope": "turn"}
        if method.endswith("requestUserInput"):
            supplied = answer.get("answers", {})
            return {"answers": {q["id"]: {"answers": [supplied[q["id"]]]}
                    for q in params.get("questions", []) if isinstance(supplied.get(q["id"]), str)
                    and 0 < len(supplied[q["id"]]) <= 16000}}
        options = params.get("availableDecisions")
        accepted = accepted and (options is None or "accept" in options)
        return {"decision": "accept" if accepted else "decline"}

    def approve(self, chat_id, request_id, answer):
        with self.lock:
            job = self.active
            if not job or job["chat_id"] != chat_id or not job["request"] or job["request"]["id"] != request_id:
                raise ContractError("approval_expired", "This request is no longer waiting for an answer.")
            if job["answer_ready"].is_set():
                raise ContractError("approval_answered", "This request has already been answered.")
            job["answer"] = answer
            job["answer_ready"].set()

    def stop(self, chat_id):
        with self.lock:
            if self.active is None or self.active["chat_id"] != chat_id:
                return
            self.active["cancel"].set()
            self.active["answer_ready"].set()
            self.store.update(chat_id, lambda c: c["turns"][-1].update(status="stopping", stage="Stopping; final usage may be uncertain"))

    def _work(self, job, chat, prompt):
        try:
            result = self.workflow(prompt, cwd=Path(chat["workspace"]), api_key=self.credentials.typesafe,
                openai_api_key=self.credentials.openai, run_dir=self.run_dir, budget_file=self.budget_file,
                timeout_seconds=self.timeout, session_id=chat["session_id"], cancel_event=job["cancel"],
                approval_handler=lambda method, params: self._approve(job, method, params),
                emit=lambda method, data: self._emit(job, method, data))
            result = self.scrub(result)
            def finish(c):
                turn = c["turns"][-1]
                turn.update(status=result["status"], finished_at=now(), stage="Finished",
                    record_path=result.get("record_path"), error=(result.get("error") or {}).get("message"),
                    continuation_allowed=result.get("continuation_allowed", False))
                if result.get("accounting_status") == "uncertain":
                    turn["error"] = "Final spending is uncertain. Further calls are blocked until the records are reviewed."
            self.store.update(chat["id"], finish)
        except Exception as exc:
            message = str(exc) if isinstance(exc, ContractError) else "The local run stopped unexpectedly. Review the budget before another prompt."
            self.store.update(chat["id"], lambda c: c["turns"][-1].update(status="error", finished_at=now(), error=self.scrub(message)))
        finally:
            with self.lock:
                self.active = None

    def spending(self, baseline, cache):
        # Validate even when there are no saved runs. Invalid choices must not silently hide data.
        compare_record({}, None, baseline_id=baseline, cache_lifetime=cache)
        results = []
        for path in sorted(self.run_dir.glob("*/workflow.json"), reverse=True)[:1000]:
            try:
                record = read_json(path)
                if not record.get("route"):
                    continue
                classifier = None
                try:
                    classifier_path = Path(record["classifier_record_path"]).resolve()
                    classifier_path.relative_to(self.run_dir)
                    classifier = read_json(classifier_path)
                except (OSError, ValueError, TypeError, KeyError):
                    pass  # Keep the run visible with an unavailable classifier cost.
                comparison = compare_record(record, classifier, baseline_id=baseline, cache_lifetime=cache)
                results.append({"id": path.parent.name, "started_at": record.get("started_at"),
                    "workspace": record.get("cwd"), "status": record.get("status"),
                    "route": record["route"], "comparison": comparison})
            except (OSError, ValueError, TypeError, KeyError):
                continue
        results.sort(key=lambda r: r["started_at"] or "", reverse=True)
        return {"runs": results, "budget": self.budget(), "baseline_inference_requested": False}

    def start_evaluation(self, data):
        with self.lock:
            if self.active is not None:
                raise ContractError("already_running", "Finish or stop the coding response before running tests.")
            chat_id = data.get("chat_id")
            workspace = self.store.get(chat_id)["workspace"] if chat_id else data.get("workspace", str(self.workspace))
            return self.evaluations.start(kind=data["kind"], run_id=data["request_id"],
                workspace=workspace, directory=data.get("directory", "."), chat_id=chat_id)

    def files(self, chat_id):
        workspace = Path(self.store.get(chat_id)["workspace"]).resolve()
        paths = []
        for parent, dirs, files in os.walk(workspace, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORED_DIRS
                       and not (Path(parent) / d).is_symlink()]
            for name in sorted(files):
                path = Path(parent) / name
                if not name.startswith(".") and path.suffix not in (".pem", ".key") and not path.is_symlink():
                    paths.append(str(path.relative_to(workspace)))
                if len(paths) >= 500:
                    return {"workspace": str(workspace), "files": paths, "truncated": True}
        return {"workspace": str(workspace), "files": sorted(paths), "truncated": False}

    def file(self, chat_id, relative):
        workspace = Path(self.store.get(chat_id)["workspace"]).resolve()
        supplied = Path(relative)
        path = (workspace / supplied).resolve()
        try:
            resolved_relative = path.relative_to(workspace)
            if (supplied.is_absolute() or any(p.startswith(".") for p in (*supplied.parts, *resolved_relative.parts))
                    or path.suffix.lower() in (".pem", ".key")):
                raise ValueError
            if path.stat().st_size > MAX_TEXT:
                raise ContractError("file_too_large", "Open this file in your editor; it exceeds the browser preview limit.")
            content = path.read_text(encoding="utf-8")
            if "\x00" in content:
                raise ValueError
            return {"path": str(path), "content": self.scrub(content)}
        except (OSError, ValueError):
            raise ContractError("file_unavailable", "Only readable text files inside this conversation's workspace can be previewed.") from None


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int, app: LocalApp):
        self.app = app
        super().__init__(("127.0.0.1", port), Handler)
        self.allowed_hosts = {f"127.0.0.1:{self.server_port}", f"localhost:{self.server_port}"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Do not log private prompts, approval data, or file paths.

    def _send(self, status, body, kind="application/json; charset=utf-8"):
        encoded = json.dumps(body, ensure_ascii=True).encode() if isinstance(body, (dict, list)) else body
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        try:
            self.wfile.write(encoded)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _guard(self, *, private=False):
        host = self.headers.get("Host", "")
        if host not in self.server.allowed_hosts:
            raise ContractError("invalid_host", "This server accepts localhost requests only.")
        origin = self.headers.get("Origin")
        if origin is not None and origin != f"http://{host}":
            raise ContractError("invalid_origin", "Cross-origin requests are not accepted.")
        if private and not secrets.compare_digest(self.headers.get("X-ACA-Token", ""), self.server.app.token):
            raise ContractError("invalid_request_token", "Reload this local page before continuing.")

    def do_GET(self):
        try:
            self._guard()
            parsed = urlsplit(self.path)
            if parsed.path == "/" or parsed.path.startswith("/assets/"):
                name = "index.html" if parsed.path == "/" else unquote(parsed.path[1:])
                asset = (ASSETS / name).resolve()
                if not asset.is_relative_to(ASSETS.resolve()) or not asset.is_file():
                    return self._send(404, {"error": "Build the React frontend with: npm run build --prefix frontend"})
                kind = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
                return self._send(200, asset.read_bytes(), kind)
            if parsed.path == "/api/bootstrap":
                return self._send(200, self.server.app.bootstrap())
            self._guard(private=True)
            pieces = parsed.path.strip("/").split("/")
            query = parse_qs(parsed.query)
            app = self.server.app
            if parsed.path == "/api/chats":
                return self._send(200, {"chats": app.store.list()})
            if parsed.path == "/api/spending":
                return self._send(200, app.spending(query.get("baseline", ["sol-high"])[0], query.get("cache", ["30m"])[0]))
            if parsed.path == "/api/evaluations":
                with app.evaluations.lock:
                    active_id = app.evaluations.active["id"] if app.evaluations.active else None
                return self._send(200, {"suites": app.evaluations.catalog(), "runs": app.evaluations.list(), "active_id": active_id})
            if len(pieces) == 3 and pieces[:2] == ["api", "evaluations"]:
                return self._send(200, app.evaluations.get(pieces[2]))
            if len(pieces) in (3, 4) and pieces[:2] == ["api", "chats"]:
                chat_id = identifier(pieces[2])
                if len(pieces) == 3:
                    return self._send(200, app.chat(chat_id))
                if pieces[3] == "files":
                    return self._send(200, app.files(chat_id))
                if pieces[3] == "file":
                    return self._send(200, app.file(chat_id, query.get("path", [""])[0]))
            self._send(404, {"error": "This page is not available."})
        except ContractError as exc:
            self._send(400, {"error": str(exc), "code": exc.code})
        except Exception:
            self._send(500, {"error": "Could not read local data. Check the server terminal and budget records."})

    def do_POST(self):
        try:
            self._guard(private=True)
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ContractError("invalid_content_type", "Expected a JSON request.")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 100_000:
                raise ContractError("invalid_request_size", "The request is empty or too large.")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
            app = self.server.app
            pieces = urlsplit(self.path).path.strip("/").split("/")
            if pieces == ["api", "evaluations"]:
                return self._send(202, app.start_evaluation(data))
            if len(pieces) == 4 and pieces[:2] == ["api", "evaluations"] and pieces[3] == "stop":
                app.evaluations.stop(pieces[2])
                return self._send(200, {"status": "stopping"})
            if pieces == ["api", "chats"]:
                workspace = validate_run(Path(data.get("workspace") or app.workspace), app.timeout)
                return self._send(201, app.store.create(workspace))
            if len(pieces) == 4 and pieces[:2] == ["api", "chats"]:
                chat_id = identifier(pieces[2])
                if pieces[3] == "messages":
                    return self._send(202, app.submit(chat_id, data["prompt"], data["submission_id"]))
                if pieces[3] == "stop":
                    app.stop(chat_id)
                    return self._send(200, {"status": "stopping"})
                if pieces[3] == "approval":
                    app.approve(chat_id, data["request_id"], data)
                    return self._send(200, {"status": "answered"})
            self._send(404, {"error": "This action is not available."})
        except ContractError as exc:
            self._send(409 if exc.code in ("already_running", "budget_busy", "evaluation_busy") else 400, {"error": str(exc), "code": exc.code})
        except (ValueError, KeyError, TypeError):
            self._send(400, {"error": "The request is invalid."})
        except Exception:
            self._send(500, {"error": "A local operation failed. Inspect the budget before submitting again."})


def serve(*, port, workspace, run_dir, chat_dir, budget_file, credentials, timeout_seconds):
    if not 1024 <= port <= 65535:
        raise ContractError("invalid_port", "Choose a local port between 1024 and 65535.")
    app = LocalApp(workspace=workspace, run_dir=run_dir, chat_dir=chat_dir, budget_file=budget_file,
                   credentials=credentials, timeout_seconds=timeout_seconds)
    server = LocalServer(port, app)
    print(f"Adaptive Coding Agents: http://127.0.0.1:{server.server_port}", flush=True)
    print(f"Default code workspace: {app.workspace}", flush=True)
    print("Starting the UI makes no model calls. Sending a message uses your existing API budget.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if app.active:
            app.stop(app.active["chat_id"])
        if app.evaluations.active:
            app.evaluations.stop(app.evaluations.active["id"])
        server.server_close()
