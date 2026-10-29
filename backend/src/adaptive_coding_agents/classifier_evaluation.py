"""Small human-labeled classifier pilot. No coding, training, or success claims."""

from collections import Counter
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from .budget import BudgetLedger, JEV_RESERVATION
from .classification import classify_with_budget
from .jev import MODEL, JevClient, build_request, encode_request
from .records import ContractError, Labels, PromptRecord
from .run_records import _write_json, validate_example_id
from .taxonomy import TAXONOMY_VERSION
from .workflow_records import now


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_examples(path: Path, split: str) -> tuple[list[dict], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["schema_version"] != "classifier-pilot-1" or data["taxonomy_version"] != TAXONOMY_VERSION:
            raise ValueError
        groups, identifiers, prompts, selected, inputs = {}, set(), {}, [], []
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
            if row["split"] == split:
                if (not isinstance(row.get("review"), dict) or row["review"].get("status") != "human_reviewed" or
                        not row["review"].get("reviewer_id") or not row["review"].get("reviewed_at") or
                        row.get("annotation_input") != "current_prompt_only"):
                    raise ContractError("labels_need_review", "Review labels from each current prompt before running this split. Do not use Jev predictions as gold labels.")
                Labels.from_dict(row["labels"])
                selected.append(row)
        if not 0 < len(selected) <= 20:
            raise ContractError("pilot_size", "This pilot accepts 1-20 examples per split.")
        return selected, fingerprint(inputs)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError("invalid_dataset", "The classifier dataset is missing or does not match the pilot schema.") from None


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
                        output_root: Path, freeze_from: Path | None = None) -> dict:
    examples, inputs_hash = load_examples(dataset, split)
    JevClient(api_key)  # Validate credentials locally before creating a pending report.
    questions_hash = hashlib.sha256(encode_request(build_request("schema fingerprint")["questions"])).hexdigest()
    if split == "held_out":
        try:
            frozen = json.loads(freeze_from.read_text()) if freeze_from else {}
            if (not isinstance(frozen, dict) or
                    frozen.get("schema_version") != "classifier-evaluation-1" or frozen.get("status") != "completed" or
                    frozen.get("split") != "development" or frozen.get("questions_sha256") != questions_hash or
                    frozen.get("dataset_inputs_sha256") != inputs_hash or frozen.get("requested_model") != MODEL):
                raise ValueError
        except (OSError, ValueError):
            raise ContractError("freeze_required", "Held-out evaluation requires a completed development report with the same classifier model, dataset inputs, and frozen questions.") from None
    path = output_root.resolve() / str(uuid4()) / "report.json"
    report = {"schema_version": "classifier-evaluation-1", "status": "pending", "started_at": now(),
        "split": split, "requested_model": MODEL, "taxonomy_version": TAXONOMY_VERSION, "questions_sha256": questions_hash,
        "dataset_inputs_sha256": inputs_hash, "reviewed_annotations_sha256": fingerprint(examples),
        "freeze_from": str(freeze_from) if freeze_from else None, "planned": len(examples), "results": [],
        "scope": "Authored classifier diagnostic pilot; not coding-task success, routing savings, or a paper-scale accuracy claim."}
    with BudgetLedger(budget_file) as ledger:
        ledger.check("jev", JEV_RESERVATION * len(examples))
        used = sum(e["provider"] == "jev" and e["attempted"] is not False for e in ledger.data["entries"].values())
        if used + len(examples) > ledger.data["attempt_limits"]["jev"]:
            raise ContractError("budget_exhausted", "The approved request count cannot cover this pilot split.")
        path.parent.mkdir(parents=True, mode=0o700)
        _write_json(path, report)
        for example in examples:
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
            _write_json(path, report)
            if result["status"] != "ok" or result["cost_estimate"]["estimated_cost_usd"] is None:
                report.update(status="stopped", stop_reason="classification_error_or_unknown_usage")
                break
        else:
            report["status"] = "completed"
        report.update(finished_at=now(), metrics=summarize(report["results"]),
            unattempted=len(examples) - len(report["results"]), budget=ledger.summary())
        _write_json(path, report)
    return {**report, "record_path": str(path)}
