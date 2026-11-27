"""Replay the frozen selection and compare original UTF-8 bytes without touching a prediction."""
from pathlib import Path
from tempfile import TemporaryDirectory

from reserve_cache import DATA, VERIFY, check, read, save, sha
from reserve_scenarios import freeze_scenarios
from reserve_select import COLUMNS, ROOT, SCRATCH, digest, fingerprint, freeze


def replay():
    reserve = read(DATA / "reserve.json")
    source = read(SCRATCH)
    ledger = read(DATA / "screening-ledger.json")
    messages = read(DATA / "initial-prompts.json")
    rows = source["records"]
    projected = [{k: row[k] if k != "problem_statement" else row["prompt"] for k in COLUMNS} for row in rows]
    check(fingerprint(projected) == reserve["upstream_projection_fingerprint"], "Projected upstream data")
    by_id = {r["instance_id"]: r for r in rows}
    check(len(by_id) == len(ledger["rows"]) == 500, "Population")
    check(sha(Path(__file__).with_name("reserve_select.py")) == reserve["selector_sha256"], "Selection source")
    check(sha(DATA / "screening-decisions.json") == reserve["decisions_sha256"], "Screening decisions")
    for name, checksum in ledger["development_sources"].items():
        path = ROOT / name if "/" in name else ROOT / "data" / name
        check(sha(path) == checksum, "Development source identity")
    for task, message in zip(reserve["tasks"], messages, strict=True):
        original = by_id[task["instance_id"]]
        check(message["id"] == task["initial_message_id"], "Initial message ID")
        check(original["prompt"].encode("utf-8") == message["prompt"].encode("utf-8"), "Original issue bytes")
        check(digest(message["prompt"]) == task["prompt_sha256"] == original["prompt_sha256"], "Issue digest")
        check(task["base_commit"] == original["base_commit"], "Issue base")
    names = ["initial-prompts.json", "sample-rule.json", "screening-ledger.json", "reserve.json",
             "followup-prompts.json", "scenarios.json"]
    with TemporaryDirectory() as tmp:
        dest = Path(tmp)
        freeze(dest, DATA / "screening-decisions.json")
        (dest / "scenario-specs.json").write_bytes((DATA / "scenario-specs.json").read_bytes())
        freeze_scenarios(dest)
        for name in names:
            check(sha(dest / name) == sha(DATA / name), "Replay digest: " + name)
    report = {"passed": True, "selected_issues": len(messages), "population": len(rows),
              "projected_source_fingerprint": reserve["upstream_projection_fingerprint"],
              "screening_sources": len(ledger["development_sources"]),
              "matching_file_sha256": {name: sha(DATA / name) for name in names},
              "scope": "Replayed selection from the pre-screened projection and fixed review decisions. Compared original UTF-8 bytes. Recompiled public probes. No classifier or grader invoked."}
    path = VERIFY / "selection-replay.json"
    if path.exists():
        check(read(path) == report, "Existing selection replay")
    else:
        save(path, report)
    print("Selection replay passed for", len(messages), "groups and", len(names), "frozen files.")


if __name__ == "__main__":
    replay()
