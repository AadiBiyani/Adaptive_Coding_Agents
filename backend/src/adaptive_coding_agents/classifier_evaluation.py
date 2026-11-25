"""Small human-labeled classifier pilot. No coding, training, or success claims."""

from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from .budget import BudgetLedger, JEV_RESERVATION, CLASSIFIER_EXPERIMENT
from .classification import classify_with_budget
from .classifier_dataset import fingerprint, load_dataset, load_examples, reviewed, summarize
from .jev import MODEL, JevClient, build_request, encode_request
from .records import ContractError
from .run_records import _write_json, validate_example_id
from .taxonomy import TAXONOMY_VERSION
from .workflow_records import now


def prepare_evaluation(dataset: Path, split: str, freeze_from: Path | None = None) -> tuple[list[dict], dict]:
    """No inference: validate the exact batch and its development freeze."""
    examples, inputs_hash = load_examples(dataset, split)
    questions_hash = hashlib.sha256(encode_request(build_request("schema fingerprint")["questions"])).hexdigest()
    frozen_hash = None
    if split == "held_out":
        try:
            frozen = json.loads(freeze_from.read_text()) if freeze_from else {}
            if (not isinstance(frozen, dict) or
                    frozen.get("schema_version") != "classifier-evaluation-1" or frozen.get("status") != "completed" or
                    frozen.get("split") != "development" or frozen.get("questions_sha256") != questions_hash or
                    frozen.get("dataset_inputs_sha256") != inputs_hash or frozen.get("requested_model") != MODEL):
                raise ValueError
            development, _ = load_examples(dataset, "development")
            if frozen.get("reviewed_annotations_sha256") != fingerprint(development):
                raise ValueError
            frozen_hash = fingerprint(frozen)
        except (OSError, ValueError):
            raise ContractError("freeze_required", "Held-out evaluation requires a completed development report with the same classifier model, dataset inputs, reviewed development labels, and frozen questions.") from None
    plan = {"split": split, "requested_model": MODEL, "taxonomy_version": TAXONOMY_VERSION,
        "questions_sha256": questions_hash, "dataset_inputs_sha256": inputs_hash,
        "reviewed_annotations_sha256": fingerprint(examples), "freeze_sha256": frozen_hash,
        "planned": len(examples), "jev_requests": len(examples), "openai_calls": 0,
        "admission_estimate_usd": {"jev": str(JEV_RESERVATION * len(examples)), "openai": "0"}}
    return examples, {**plan, "plan_sha256": fingerprint(plan)}


def check_batch_budget(ledger: BudgetLedger, count: int):
    ledger.check("jev", JEV_RESERVATION * count)
    limit = ledger.attempt_limit("jev")
    if limit is None:
        raise ContractError("experiment_limit_required", "Classifier batches require a separately allocated experiment request cap.")
    if ledger.attempts_used("jev") + count > limit:
        raise ContractError("budget_exhausted", "The approved request count cannot cover this pilot split.")




def evaluate_classifier(*, dataset: Path, split: str, api_key: str, budget_file: Path,
                        output_root: Path, freeze_from: Path | None = None,
                        run_id: str | None = None, expected_plan_sha256: str | None = None,
                        cancel_event=None, progress=None) -> dict:
    examples, plan = prepare_evaluation(dataset, split, freeze_from)
    if expected_plan_sha256 is not None and expected_plan_sha256 != plan["plan_sha256"]:
        raise ContractError("stale_preview", "The reviewed batch changed. Preview its cost and confirm again.")
    JevClient(api_key)  # Validate credentials locally before creating a pending report.
    if run_id is not None:
        validate_example_id(run_id)
    path = output_root.resolve() / (run_id or str(uuid4())) / "report.json"
    if path.exists():
        raise ContractError("duplicate_attempt", "This classifier report already exists. It will not be replayed.")
    report = {"schema_version": "classifier-evaluation-1", "status": "pending", "started_at": now(),
        **plan, "record_path": str(path),
        "freeze_from": str(freeze_from) if freeze_from else None, "planned": len(examples), "results": [],
        "scope": "Authored classifier diagnostic pilot; not coding-task success, routing savings, or a paper-scale accuracy claim."}

    def publish():
        report.update(metrics=summarize(report["results"]), unattempted=len(examples) - len(report["results"]))
        amounts = [r["cost_estimate"]["estimated_cost_usd"] for r in report["results"]]
        report["estimated_cost_usd"] = str(sum((Decimal(a) for a in amounts), Decimal(0))) if all(a is not None for a in amounts) else None
        report["actual_billed_cost_usd"] = None
        _write_json(path, report)
        if progress:
            progress(deepcopy(report))

    with BudgetLedger(budget_file, purpose=CLASSIFIER_EXPERIMENT) as ledger:
        check_batch_budget(ledger, len(examples))
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        publish()
        for example in examples:
            if cancel_event is not None and cancel_event.is_set():
                report.update(status="cancelled", stop_reason="owner_cancelled")
                break
            try:
                result = classify_with_budget(example["prompt"], api_key=api_key, ledger=ledger,
                    run_dir=path.parent / "attempts", example_id=example["id"])
            except ContractError as exc:
                report.update(status="stopped", stop_reason=exc.code)
                break
            report["results"].append({"id": example["id"], "group_id": example["group_id"],
                "status": result["status"], "expected": example["labels"], "predicted": result.get("labels"),
                "record_path": result["record_path"], "usage": result["usage"],
                "cost_estimate": result["cost_estimate"], "elapsed_ms": result.get("elapsed_ms")})
            publish()
            if result["status"] != "ok" or result["cost_estimate"]["estimated_cost_usd"] is None:
                report.update(status="stopped", stop_reason="classification_error_or_unknown_usage")
                break
        else:
            report["status"] = "completed"
        report.update(finished_at=now(), metrics=summarize(report["results"]),
            unattempted=len(examples) - len(report["results"]), budget=ledger.summary())
        publish()
    return {**report, "record_path": str(path)}
