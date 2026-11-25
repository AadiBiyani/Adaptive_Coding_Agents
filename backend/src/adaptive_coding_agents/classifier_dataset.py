"""Portable pilot dataset validation and classifier metrics shared by both runners."""

from collections import Counter
import hashlib
import json
from pathlib import Path

from .records import ContractError, Labels, PromptRecord
from .run_records import validate_example_id
from .taxonomy import TAXONOMY_VERSION


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
