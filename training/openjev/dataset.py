"""Offline split audit and prompt-only review sheets for the local Flash experiment."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path

from flash import ROOT, write
from adaptive_coding_agents.classifier_dataset import fingerprint, load_dataset, reviewed
from adaptive_coding_agents.records import Labels, PromptRecord
from adaptive_coding_agents.taxonomy import TAXONOMY_VERSION

TRAIN = ROOT / "data/openjev-training.json"
PILOT = ROOT / "data/classifier-pilot.json"
FIELDS = tuple(Labels.OPTIONS)


def splits():
    train = json.loads(TRAIN.read_text(encoding="utf-8"))
    if train["schema_version"] != "openjev-training-1" or train["taxonomy_version"] != TAXONOMY_VERSION:
        raise ValueError("Training schema or taxonomy mismatch")
    pilot, _ = load_dataset(PILOT)
    groups, prompts, ids = {}, {}, set()
    out = {"training": [], "development": [], "held_out": []}
    for row in train["examples"] + pilot["examples"]:
        split = row["split"]
        if row in train["examples"] and (split != "training" or not row.get("source")):
            raise ValueError("Invalid training split or source")
        if row["id"] in ids or not row["id"] or not row.get("group_id"):
            raise ValueError("Duplicate/missing ID or group")
        ids.add(row["id"])
        if row.get("excluded"):
            continue
        PromptRecord.capture(row["prompt"])
        for mapping, key in ((groups, row["group_id"]), (prompts, " ".join(row["prompt"].casefold().split()))):
            if mapping.setdefault(key, split) != split:
                raise ValueError(f"Cross-split group or duplicate at {row['id']}")
        out[split].append(row)
    if len(out["development"]) != 20 or len(out["held_out"]) != 20:
        raise ValueError("Expected original 20/20 pilot")
    return out


def require_review(rows):
    missing = [r["id"] for r in rows if not reviewed(r)]
    if missing or not rows:
        raise ValueError(f"Independently reviewed labels required: {missing}")


def split_hashes(data):
    # Freeze every prompt, plus reviewed train/dev annotations. Hold-out gold can
    # be supplied before evaluation without changing its predeclared input bytes.
    return {s: fingerprint(rows if s != "held_out" else [
        {k: r[k] for k in ("id", "group_id", "prompt", "split")} for r in rows])
        for s, rows in data.items()}


def export(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, ["id", "prompt", *FIELDS])
        writer.writeheader()
        for row in rows:
            writer.writerow({"id": row["id"], "prompt": row["prompt"], **(row.get("labels") or {})})


def draft_evidence(entry, labels):
    if entry.get("taxonomy_version") != TAXONOMY_VERSION:
        raise ValueError(f"Taxonomy mismatch at {entry['id']}")
    quotes = {}
    for field, label in labels.items():
        quote = entry.get(f"{field}_quote") or ""
        if label != "unknown" or quote:
            if not quote.strip() or quote not in entry["prompt"]:
                raise ValueError(f"Expected a verbatim {field} quote from {entry['id']}")
            quotes[field] = quote
    return {"annotation_source": "assistant_prompt_only", "taxonomy_version": TAXONOMY_VERSION,
            "evidence_quotes": quotes}


def pilot_review_id(row):
    """Opaque sheet ID so the source issue name cannot suggest a label."""
    return fingerprint([row["split"], row["id"], row["prompt"]])[:12]


def record(split, path, reviewer):
    if not reviewer.strip():
        raise ValueError("Supply your reviewer ID")
    target = TRAIN if split == "training" else PILOT
    original = json.loads(target.read_text(encoding="utf-8"))
    selected = splits()[split]
    allowed = {r["id"] for r in selected}
    blind_ids = {pilot_review_id(r): r["id"] for r in selected} if split != "training" else {}
    rows = {r["id"]: r for r in original["examples"]}
    changes = 0
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for entry in csv.DictReader(stream):
            ident = entry["id"] if "id" in entry else blind_ids.get(entry.get("review_id"))
            if ident in seen or ident not in allowed or entry["prompt"] != rows[ident]["prompt"]:
                raise ValueError(f"Duplicate, changed, or unexpected review row: {ident}")
            seen.add(ident)
            provenance = {}
            if entry.get("annotation_source"):
                if entry["annotation_source"] != "assistant_prompt_only" or split != "training":
                    raise ValueError("Assistant drafts are supported only for training prompts")
                if entry.get("review_status") == "pending_owner_review":
                    continue
                if entry.get("review_status") != "human_reviewed":
                    raise ValueError(f"Unrecognized draft review status at {ident}")
            labels = {f: entry[f].strip() for f in FIELDS}
            if not any(labels.values()):
                continue
            Labels.from_dict(labels)
            if entry.get("annotation_source"):
                provenance = draft_evidence(entry, labels)
            row = rows[ident]
            if reviewed(row):
                if row["labels"] != labels:
                    raise ValueError(f"Existing annotation differs at {ident}")
                continue
            row.update(labels=labels, review={**provenance, "status": "human_reviewed", "reviewer_id": reviewer,
                                             "reviewed_at": datetime.now(timezone.utc).isoformat()})
            changes += 1
    if changes:
        write(target, original)
    print(f"Recorded {changes} newly reviewed prompts.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "export", "record", "prompt"))
    parser.add_argument("--id", help="Training row to display for prompt-only annotation")
    parser.add_argument("--split", choices=("training", "development", "held_out"), default="training")
    parser.add_argument("--sheet", type=Path)
    parser.add_argument("--reviewer")
    args = parser.parse_args()
    data = splits()
    if args.command == "prompt":
        prompt = next((r["prompt"] for r in data["training"] if r["id"] == args.id), None)
        if args.split != "training" or prompt is None:
            parser.error("Supply an active training --id for prompt-only annotation")
        print(prompt)
    elif args.command == "audit":
        for split, rows in data.items():
            print(split, len(rows), "prompts,", len({r["group_id"] for r in rows}), "groups,",
                  sum(reviewed(r) for r in rows), "reviewed")
            for field in FIELDS:
                print(field, dict(Counter(r["labels"][field] for r in rows if reviewed(r))))
    elif args.command == "export" and args.sheet:
        export(data[args.split], args.sheet)
    elif args.command == "record" and args.sheet and args.reviewer:
        record(args.split, args.sheet, args.reviewer)
    else:
        parser.error("Supply --sheet and, for record, --reviewer")
