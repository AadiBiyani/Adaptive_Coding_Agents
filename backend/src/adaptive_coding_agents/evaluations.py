"""Local evaluation jobs and records, independent of the coding model loop.

Only named adapters run: project unittest checks, frontend rendering checks, and
trusted workspace unittest checks. SWE-bench needs a separate isolated adapter.
"""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import threading
import time

from .records import ContractError
from .run_records import _write_json
from .ui_store import identifier
from .workflow_records import now

MAX_OUTPUT = 160_000
KINDS = {
    "project": ("Project checks", "software_checks"),
    "frontend": ("Frontend checks", "software_checks"),
    "workspace": ("Workspace tests", "workspace_checks"),
}


def clean_environment():
    allowed = {"PATH", "HOME", "TMPDIR", "TEMP", "TMP", "LANG", "LC_ALL", "SYSTEMROOT"}
    return {**{k: v for k, v in os.environ.items() if k in allowed},
            "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1", "NO_COLOR": "1"}


def source_fingerprint(roots):
    """Hash bounded source inputs, never hidden configuration or generated runs."""
    digest, count = hashlib.sha256(), 0
    for label, root in roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else []
        if root.is_dir():
            for parent, dirs, files in os.walk(root, followlinks=False):
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and
                    d not in {"node_modules", "__pycache__", "web", "runs", "venv", "build", "dist"}
                    and not (Path(parent) / d).is_symlink())
                paths.extend(Path(parent) / name for name in sorted(files))
        for path in paths:
            relative = path.name if root.is_file() else str(path.relative_to(root))
            if (path.is_symlink() or any(p.startswith(".") or p in {"node_modules", "__pycache__", "web", "runs"}
                                        for p in Path(relative).parts)
                    or path.suffix not in {".py", ".jsx", ".js", ".mjs", ".json", ".toml", ".lock"}):
                continue
            if not path.is_file():
                continue
            if count >= 2000 or path.stat().st_size > 2_000_000:
                raise ContractError("source_too_large", "Use a smaller local test workspace; large repositories need an isolated benchmark runner.")
            digest.update(f"{label}/{relative}\0".encode())
            digest.update(hashlib.sha256(path.read_bytes()).digest())
            count += 1
    return {"sha256": digest.hexdigest(), "files": count}


class EvaluationManager:
    def __init__(self, *, project_root: Path, output_root: Path, scrub=lambda value: value, timeout=180):
        self.project_root = project_root.resolve()
        self.output_root = output_root.resolve()
        self.output_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.scrub, self.timeout = scrub, timeout
        self.lock = threading.RLock()
        self.active = None
        self.records = {}
        for path in self.output_root.glob("*/run.json"):
            try:
                if path.stat().st_size > 12_000_000:
                    continue
                record = json.loads(path.read_text())
                identifier(record["id"])
                if record.get("schema_version") != "evaluation-run-1":
                    continue
                if record["status"] in {"running", "stopping"}:
                    record.update(status="interrupted", finished_at=now(), error="The server stopped. This run was not replayed.")
                    _write_json(path, record)
                self.records[record["id"]] = record
            except (OSError, ValueError, TypeError, KeyError):
                continue

    def catalog(self):
        root = self.project_root
        return [
            {"id": "project", "name": "Project checks", "available": (root / "tests/test_jev.py").is_file(),
             "description": "Run the local Python suite for classification, routing, budgets, sessions, and the UI backend.", "model_calls": False},
            {"id": "frontend", "name": "Frontend checks", "available": (root / "tests/ui-render.mjs").is_file() and shutil.which("node") is not None,
             "description": "Render and check the React components without making model requests.", "model_calls": False},
            {"id": "workspace", "name": "Workspace tests", "available": True,
             "description": "Run existing Python unittest files in your selected coding workspace.", "model_calls": False},
        ]

    def list(self):
        with self.lock:
            keys = ("id", "kind", "name", "scope", "status", "workspace", "started_at", "finished_at", "elapsed_ms", "summary")
            return [{k: deepcopy(r.get(k)) for k in keys} for r in
                    sorted(self.records.values(), key=lambda r: r["started_at"], reverse=True)]

    def get(self, run_id):
        with self.lock:
            if identifier(run_id) not in self.records:
                raise ContractError("evaluation_missing", "This test run is not available.")
            return deepcopy(self.records[run_id])

    def _save(self, record):
        record["revision"] += 1
        _write_json(self.output_root / record["id"] / "run.json", self.scrub(record))

    def start(self, *, kind, run_id, workspace=None, directory=".", chat_id=None):
        identifier(run_id)
        with self.lock:
            if run_id in self.records:
                return self.get(run_id)
            if self.active is not None:
                raise ContractError("evaluation_busy", "Wait for the running checks or stop them before starting another run.")
            if kind not in KINDS or not next(s["available"] for s in self.catalog() if s["id"] == kind):
                raise ContractError("suite_unavailable", "This suite is unavailable. Local test files are not included in fresh clones.")
            root = self.project_root
            if kind == "workspace" and not workspace:
                raise ContractError("invalid_workspace", "Select a workspace for its tests.")
            cwd = Path(workspace).resolve() if kind == "workspace" and workspace else root
            if not cwd.is_dir():
                raise ContractError("invalid_workspace", "Select an existing workspace folder.")
            folder = self.output_root / run_id
            result_file = folder / "results.json"
            if kind == "workspace":
                relative = Path(directory)
                target = (cwd / relative).resolve()
                if (relative.is_absolute() or not target.is_relative_to(cwd) or not target.is_dir()
                        or any(p.startswith(".") and p != "." for p in relative.parts)
                        or any(p.startswith(".") for p in target.relative_to(cwd).parts)):
                    raise ContractError("invalid_test_directory", "Choose a test folder inside the selected workspace.")
                roots = [("workspace", cwd)]
            else:
                target = root / "tests"
                roots = [("tests", target), ("backend", root / "backend/src"),
                         ("frontend", root / "frontend/src"), ("package", root / "pyproject.toml"),
                         ("python_lock", root / "uv.lock"), ("js_lock", root / "frontend/package-lock.json")]
            if kind == "frontend":
                command = [shutil.which("node"), str(root / "tests/ui-render.mjs")]
            else:
                command = [sys.executable, "-I", "-m", "adaptive_coding_agents.evaluation_worker",
                           "--directory", str(target), "--output", str(result_file)]
                if kind == "workspace":
                    command.append("--workspace")
            before = source_fingerprint(roots)
            folder.mkdir(mode=0o700)
            record = {"schema_version": "evaluation-run-1", "id": run_id, "revision": 0,
                "kind": kind, "name": KINDS[kind][0], "scope": KINDS[kind][1], "status": "running",
                "workspace": str(cwd), "test_directory": str(target), "chat_id": chat_id,
                "command": command, "started_at": now(), "finished_at": None, "elapsed_ms": None,
                "summary": None, "cases": [], "output": "", "output_truncated": False, "error": None,
                "source_before": before, "source_after": None, "source_changed": None,
                "python_version": platform.python_version(), "platform": platform.platform(),
                "model_inference_requested": False, "api_cost_usd": "0", "benchmark_result": False,
                "record_path": str(folder / "run.json")}
            self._save(record)
            self.records[run_id] = record
            job = {"id": run_id, "cancel": threading.Event(), "process": None}
            self.active = job
            threading.Thread(target=self._run, args=(job, roots, result_file), daemon=True).start()
            return self.get(run_id)

    def stop(self, run_id):
        with self.lock:
            identifier(run_id)
            if self.active and self.active["id"] == run_id:
                self.active["cancel"].set()
                self.records[run_id]["status"] = "stopping"
                self._save(self.records[run_id])

    @staticmethod
    def _terminate(process):
        if process is None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)
        except ProcessLookupError:
            pass
        finally:
            # A child can outlive its parent; clear the owned process group too.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def _read_output(self, job, stream):
        import codecs
        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        while chunk := stream.read1(4096):
            text = decoder.decode(chunk)
            with self.lock:
                record = self.records[job["id"]]
                combined = record["output"] + text
                record["output_truncated"] |= len(combined) > MAX_OUTPUT
                record["output"] = self.scrub(combined[-MAX_OUTPUT:])
                record["revision"] += 1

    def _progress(self, record, result_file):
        try:
            if result_file.stat().st_size > 10_000_000:
                return None
            progress = json.loads(result_file.read_text())
            if progress.get("schema_version") != "local-test-result-1":
                return None
            record.update(summary=progress.get("summary"), cases=self.scrub(progress.get("cases", [])),
                          cases_truncated=progress.get("cases_truncated", False))
            if progress.get("error"):
                record["error"] = self.scrub(progress["error"])
            return progress.get("status")
        except (OSError, ValueError, TypeError):
            return None

    def _run(self, job, roots, result_file):
        started, process, reader = time.monotonic(), None, None
        record = self.records[job["id"]]
        try:
            if job["cancel"].is_set():
                record["status"] = "cancelled"
                return
            process = subprocess.Popen(record["command"], cwd=record["workspace"], env=clean_environment(),
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
            job["process"] = process
            reader = threading.Thread(target=self._read_output, args=(job, process.stdout), daemon=True)
            reader.start()
            while process.poll() is None:
                if job["cancel"].wait(.15) or time.monotonic() - started > self.timeout:
                    record["status"] = "cancelled" if job["cancel"].is_set() else "timed_out"
                    self._terminate(process)
                    break
                with self.lock:
                    self._progress(record, result_file)
                    self._save(record)
            reader.join(timeout=2)
            with self.lock:
                final = self._progress(record, result_file)
                record["exit_code"] = process.returncode
                if record["status"] in {"running", "stopping"}:
                    if record["kind"] == "frontend":
                        record["status"] = "passed" if process.returncode == 0 else "failed"
                        record["summary"] = {"checks_run": 1, "passed": int(process.returncode == 0), "failures": int(process.returncode != 0), "errors": 0, "skipped": 0}
                    else:
                        record["status"] = final if final in {"passed", "failed", "error", "no_tests", "skipped"} else "error"
                        if process.returncode != 0 and record["status"] == "passed":
                            record["status"] = "error"
                        if final is None:
                            record["error"] = "The test process did not produce a structured result. See its output."
                record["source_after"] = source_fingerprint(roots)
                record["source_changed"] = record["source_before"] != record["source_after"]
        except Exception:
            self._terminate(process)
            with self.lock:
                record.update(status="error", error="The local test runner stopped unexpectedly. See its output; no model run was requested.")
        finally:
            if reader:
                reader.join(timeout=2)
            if process and process.stdout:
                process.stdout.close()
            with self.lock:
                record.update(finished_at=now(), elapsed_ms=round((time.monotonic() - started) * 1000))
                try:
                    self._save(record)
                finally:
                    self.active = None
