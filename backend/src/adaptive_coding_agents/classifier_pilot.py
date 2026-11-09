"""Owner-triggered browser access to the existing budgeted classifier pilot.

Previewing and annotating never dispatch inference. A short-lived confirmation
binds a run to reviewed labels, questions, model, split, and development freeze.
"""

from copy import deepcopy
import json
from pathlib import Path
import secrets
import threading
import time

from .budget import BudgetLedger, CLASSIFIER_EXPERIMENT
from .classifier_evaluation import (check_batch_budget, evaluate_classifier, fingerprint,
                                   load_dataset, prepare_evaluation, reviewed)
from .jev import JevClient
from .records import ContractError, Labels
from .run_records import _write_json
from .taxonomy import category_questions
from .ui_store import identifier
from .workflow_records import now


class ClassifierPilot:
    def __init__(self, *, dataset: Path, output_root: Path, budget_file: Path, api_key: str,
                 scrub=lambda value: value):
        self.dataset, self.output_root = dataset.resolve(), output_root.resolve()
        self.budget_file, self.api_key, self.scrub = budget_file, api_key, scrub
        self.lock = threading.RLock()
        self.active, self.previews, self.jobs = None, {}, {}
        for path in self.output_root.glob("*/ui.json"):
            try:
                job = self._read(path)
                identifier(job["id"])
                if job.get("schema_version") != "classifier-pilot-ui-1":
                    continue
                if job["status"] in {"running", "stopping"}:
                    job.update(status="interrupted", finished_at=now(),
                        error="The server stopped. Inspect the report and budget; no requests were replayed.")
                    _write_json(path, job)
                self.jobs[job["id"]] = job
            except (OSError, ValueError, TypeError, KeyError):
                continue

    @staticmethod
    def _read(path):
        if path.stat().st_size > 4_000_000:
            raise ValueError("Report too large")
        return json.loads(path.read_text(encoding="utf-8"))

    def _reports(self):
        reports = []
        for path in self.output_root.glob("*/report.json"):
            try:
                identifier(path.parent.name)
                report = self._read(path)
                if report.get("schema_version") == "classifier-evaluation-1":
                    reports.append({**report, "id": path.parent.name})
            except (OSError, ValueError, TypeError):
                continue
        return reports

    def _locked(self, split, reports):
        # Once predictions exist, do not let them become their own gold labels.
        return bool(self.active) or any(r.get("split") == split and r.get("results") for r in reports)

    def state(self, split):
        if split not in {"development", "held_out"}:
            raise ContractError("invalid_split", "Choose development or held_out.")
        with self.lock:
            reports = self._reports()
            result = {"available": False, "examples": [], "counts": {}, "questions": category_questions(),
                "active_id": self.active["id"] if self.active else None,
                "credentials_ready": bool(self.api_key), "dataset_path": str(self.dataset),
                "runs": self.list(), "development_reports": [], "annotations_locked": self._locked(split, reports)}
            try:
                data, inputs_hash = load_dataset(self.dataset)
            except ContractError as exc:
                return {**result, "error": str(exc)}
            freezes = [{"id": r["id"], "started_at": r["started_at"]} for r in reports
                       if r.get("split") == "development" and r.get("status") == "completed"
                       and r.get("dataset_inputs_sha256") == inputs_hash]
            return self.scrub({**result, "available": True, "dataset_sha256": fingerprint(data),
                "examples": [r for r in data["examples"] if r["split"] == split],
                "counts": {s: {"total": sum(r["split"] == s for r in data["examples"]),
                    "reviewed": sum(r["split"] == s and reviewed(r) for r in data["examples"])}
                    for s in ("development", "held_out")}, "development_reports": freezes})

    def annotate(self, data):
        with self.lock:
            dataset, _ = load_dataset(self.dataset)
            if data.get("dataset_sha256") != fingerprint(dataset):
                raise ContractError("stale_dataset", "Labels changed in another window. Refresh before saving.")
            row = next((r for r in dataset["examples"] if r["id"] == data.get("example_id")), None)
            if row is None:
                raise ContractError("example_missing", "This prompt is not in the pilot dataset.")
            if self._locked(row["split"], self._reports()):
                raise ContractError("annotations_frozen", "Labels are frozen while a run is active and after predictions exist for this split.")
            reviewer = data.get("reviewer_id")
            if data.get("reviewed") is not True or not isinstance(reviewer, str) or not 1 <= len(reviewer.strip()) <= 80:
                raise ContractError("review_required", "Enter a reviewer nickname and confirm that you reviewed only this prompt.")
            Labels.from_dict(data.get("labels"))
            row.update(labels=deepcopy(data["labels"]), annotation_input="current_prompt_only",
                review={"status": "human_reviewed", "reviewer_id": reviewer.strip(), "reviewed_at": now()})
            _write_json(self.dataset, dataset)
            self.previews.clear()
            return self.state(row["split"])

    def _freeze_path(self, freeze_id):
        return self.output_root / identifier(freeze_id) / "report.json" if freeze_id else None

    def preview(self, *, split, freeze_id=None):
        with self.lock:
            if self.active:
                raise ContractError("already_running", "Wait for the current classifier batch to finish.")
            JevClient(self.api_key)  # Local credential validation, no network.
            _, plan = prepare_evaluation(self.dataset, split, self._freeze_path(freeze_id))
            with BudgetLedger(self.budget_file, purpose=CLASSIFIER_EXPERIMENT) as ledger:
                check_batch_budget(ledger, plan["planned"])
                remaining = ledger.summary()["remaining_usd"]
                requests_left = ledger.attempt_limit("jev") - ledger.attempts_used("jev")
            self.previews = {k: p for k, p in self.previews.items() if p["expires"] > time.monotonic()}
            if len(self.previews) >= 16:
                self.previews.pop(next(iter(self.previews)))
            token = secrets.token_urlsafe(32)
            self.previews[token] = {"plan": plan, "freeze_id": freeze_id, "expires": time.monotonic() + 300}
            return {**plan, "confirmation_token": token, "expires_in_seconds": 300,
                "remaining_usd": remaining, "jev_requests_remaining": requests_left,
                "estimate_kind": "conservative_admission_estimate", "actual_billed_cost_usd": None,
                "warning": "This spends Jev tokens. OpenAI is not called. The estimate is an admission allowance, not a guaranteed bill. No automatic retries."}

    def start(self, data):
        run_id = identifier(data["request_id"])
        with self.lock:
            if data.get("confirmed") is not True:
                raise ContractError("confirmation_required", "Confirm the preview before spending Jev tokens.")
            if run_id in self.jobs:
                return self.get(run_id)  # Retrying the same HTTP request never replays a batch.
            if self.active:
                raise ContractError("already_running", "Wait for the current classifier batch to finish.")
            token = data.get("confirmation_token")
            preview = self.previews.get(token) if isinstance(token, str) else None
            if preview is None or preview["expires"] <= time.monotonic():
                raise ContractError("confirmation_expired", "Preview the batch again before confirming.")
            _, plan = prepare_evaluation(self.dataset, preview["plan"]["split"], self._freeze_path(preview["freeze_id"]))
            if plan != preview["plan"]:
                raise ContractError("stale_preview", "The batch changed. Preview and confirm its cost again.")
            with BudgetLedger(self.budget_file, purpose=CLASSIFIER_EXPERIMENT) as ledger:
                check_batch_budget(ledger, plan["planned"])
            folder = self.output_root / run_id
            if folder.exists():
                raise ContractError("duplicate_attempt", "This report folder exists; choose a new request ID without replaying it.")
            folder.mkdir(parents=True, mode=0o700)
            job = {"schema_version": "classifier-pilot-ui-1", "id": run_id, "status": "running",
                "started_at": now(), "finished_at": None, "plan": plan, "error": None,
                "report": None, "confirmed_at": now()}
            _write_json(folder / "ui.json", job)
            self.jobs[run_id] = job
            self.previews.pop(token)
            self.active = {"id": run_id, "cancel": threading.Event()}
            threading.Thread(target=self._run, args=(self.active, preview), daemon=True).start()
            return self.get(run_id)

    def _run(self, active, preview):
        run_id = active["id"]
        def progress(report):
            with self.lock:
                self.jobs[run_id]["report"] = self.scrub(report)
        try:
            report = evaluate_classifier(dataset=self.dataset, split=preview["plan"]["split"],
                api_key=self.api_key, budget_file=self.budget_file, output_root=self.output_root,
                freeze_from=self._freeze_path(preview["freeze_id"]), run_id=run_id,
                expected_plan_sha256=preview["plan"]["plan_sha256"], cancel_event=active["cancel"], progress=progress)
            with self.lock:
                self.jobs[run_id].update(status=report["status"], report=self.scrub(report))
        except Exception as exc:
            with self.lock:
                self.jobs[run_id].update(status="error", error=self.scrub(str(exc)) if isinstance(exc, ContractError)
                    else "The batch stopped unexpectedly. Inspect the report and budget before another run.")
        finally:
            with self.lock:
                self.jobs[run_id]["finished_at"] = now()
                try:
                    _write_json(self.output_root / run_id / "ui.json", self.jobs[run_id])
                finally:
                    self.active = None

    def stop(self, run_id):
        with self.lock:
            identifier(run_id)
            if self.active and self.active["id"] == run_id:
                self.active["cancel"].set()
                self.jobs[run_id]["status"] = "stopping"
            return self.get(run_id)

    def get(self, run_id):
        with self.lock:
            identifier(run_id)
            if run_id in self.jobs:
                job = deepcopy(self.jobs[run_id])
                if job["report"] is None:
                    try:
                        job["report"] = self._read(self.output_root / run_id / "report.json")
                    except (OSError, ValueError):
                        pass
                return self.scrub(job)
            report = next((r for r in self._reports() if r["id"] == run_id), None)
            if report:
                return self.scrub({"id": run_id, "status": report["status"], "report": report, "plan": report})
            raise ContractError("evaluation_missing", "This classifier run is not available.")

    def list(self):
        with self.lock:
            reports = {r["id"]: {"id": r["id"], "split": r["split"], "status": r["status"],
                "started_at": r["started_at"]} for r in self._reports()}
            for job in self.jobs.values():
                reports[job["id"]] = {"id": job["id"], "split": job["plan"]["split"],
                    "status": job["status"], "started_at": job["started_at"]}
            return sorted(reports.values(), key=lambda r: r["started_at"], reverse=True)
