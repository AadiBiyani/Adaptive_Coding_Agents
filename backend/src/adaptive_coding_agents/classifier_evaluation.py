"""Small human-labeled classifier pilot. No coding, training, or success claims."""

from collections import Counter
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from .budget import BudgetLedger, JEV_RESERVATION, CLASSIFIER_EXPERIMENT
from .classification import classify_with_budget
from .jev import MODEL, JevClient, build_request, encode_request
from .records import ContractError, Labels, PromptRecord
from .run_records import _write_json, validate_example_id
from .taxonomy import TAXONOMY_VERSION
from .workflow_records import now


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_dataset(path: Path) -> tuple[dict, str]:
    """Validate inputs even before annotations exist; never infer missing labels."""
    try:
        if path.stat().st_size > 2_000_000:
            raise ValueError
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["schema_version"] != "classifier-pilot-1" or data["taxonomy_version"] != TAXONOMY_VERSION:
            raise ValueError
        if not isinstance(data["examples"], list) or not 0 < len(data["examples"]) <= 40:
            raise ValueError
        groups, identifiers, prompts, inputs = {}, set(), {}, []
        for row in data["examples"]:
            validate_example_id(row["id"])
            validate_example_id(row["group_id"])
            if row["id"] in identifiers or row["split"] not in ("development", "held_out"):
                raise ValueError
            identifiers.add(row["id"])
            for mapping, key in ((groups, row["group_id"]), (prompts, PromptRecord.capture(row["prompt"]).prompt_sha256)):
                if key in mapping and mapping[key] != row["split"]:
                    raise ContractError("split_leakage", "Related or duplicate prompts occur in both splits.")
                mapping[key] = row["split"]
            inputs.append({key: row[key] for key in ("id", "group_id", "split", "prompt")})
        if any(sum(r["split"] == split for r in data["examples"]) > 20 for split in ("development", "held_out")):
            raise ContractError("pilot_size", "This pilot accepts 1-20 examples per split.")
        return data, fingerprint(inputs)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError("invalid_dataset", "The classifier dataset is missing or does not match the pilot schema.") from None


def reviewed(row: dict) -> bool:
    review = row.get("review")
    if (not isinstance(review, dict) or review.get("status") != "human_reviewed" or
            not review.get("reviewer_id") or not review.get("reviewed_at") or
            row.get("annotation_input") != "current_prompt_only"):
        return False
    try:
        Labels.from_dict(row.get("labels"))
        return True
    except ContractError:
        return False


def load_examples(path: Path, split: str) -> tuple[list[dict], str]:
    if split not in ("development", "held_out"):
        raise ContractError("invalid_split", "Choose development or held_out.")
    data, inputs_hash = load_dataset(path)
    selected = [row for row in data["examples"] if row["split"] == split]
    if not selected:
        raise ContractError("pilot_size", "This pilot accepts 1-20 examples per split.")
    if not all(reviewed(row) for row in selected):
        raise ContractError("labels_need_review", "Review labels from each current prompt before running this split. Do not use Jev predictions as gold labels.")
    return selected, inputs_hash


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


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    metrics = {}
    for name, choices in Labels.OPTIONS.items():
        confusion = Counter((r["expected"][name], (r.get("predicted") or {}).get(name, "__error__")) for r in rows)
        correct = sum(confusion[c, c] for c in choices)
        f1 = []
        for c in choices:
            tp = confusion[c, c]
            fp = sum(v for (actual, predicted), v in confusion.items() if predicted == c and actual != c)
            fn = sum(v for (actual, predicted), v in confusion.items() if actual == c and predicted != c)
            f1.append(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0)
        metrics[name] = {"accuracy": correct / n if n else None,
            "macro_f1": sum(f1) / len(f1) if n else None,
            "macro_f1_labels": list(choices), "zero_division": 0,
            "confusion": {a: {p: confusion[a, p] for p in (*choices, "__error__")} for a in choices}}
    return {"attempted": n, "failures": sum(r["status"] != "ok" for r in rows),
        "all_fields_exact_match": sum(r.get("predicted") == r["expected"] for r in rows) / n if n else None,
        "unknown_or_mixed": sum(any(v in ("unknown", "mixed_or_unclear") for v in (r.get("predicted") or {}).values()) for r in rows),
        "fields": metrics, "failure_denominator": "All attempted examples, including failures."}


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
