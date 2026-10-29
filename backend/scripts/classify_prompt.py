"""Inspect a Jev request locally; --live explicitly sends one request to TypeSafe."""

import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys

from adaptive_coding_agents.jev import ENDPOINT, MODEL, build_request, encode_request
from adaptive_coding_agents.records import ContractError, PROMPT_LIMIT_BYTES, PromptRecord, SCHEMA_VERSION
from adaptive_coding_agents.run_records import DEFAULT_RUN_DIR, RunRecordError, classify_recorded, validate_example_id
from adaptive_coding_agents.taxonomy import TAXONOMY_VERSION


def read_prompt(path: Path | None) -> str:
    try:
        if path is None:
            raw = sys.stdin.buffer.read(PROMPT_LIMIT_BYTES + 1)
        else:
            with path.open("rb") as source:
                raw = source.read(PROMPT_LIMIT_BYTES + 1)
    except OSError:
        raise ContractError("input_error", "Unable to read the prompt file or stdin.") from None
    if len(raw) > PROMPT_LIMIT_BYTES:
        raise ContractError("prompt_too_large", f"The prompt exceeds {PROMPT_LIMIT_BYTES} UTF-8 bytes.")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ContractError("invalid_utf8", "The prompt must be valid UTF-8 text.") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, help="UTF-8 prompt file; otherwise read stdin.")
    parser.add_argument("--example-id", help="Optional example identifier, recorded locally and never sent to Jev.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR,
                        help="Live attempt records directory (default: runs/jev). Preview writes no files.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview the request without contacting TypeSafe (default).")
    mode.add_argument("--live", action="store_true", help="Send one paid-capable API request; requires TYPESAFE_API_KEY.")
    args = parser.parse_args(argv)
    if args.prompt_file is None and sys.stdin.isatty():
        parser.error("Supply --prompt-file or pipe a prompt into stdin.")
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "mode": "live" if args.live else "preview",
        "provider": "typesafe",
        "endpoint": ENDPOINT,
        "requested_model": MODEL,
        "taxonomy_version": TAXONOMY_VERSION,
        "input_policy_version": "prompt-only-1",
    }
    try:
        validate_example_id(args.example_id)
        prompt = read_prompt(args.prompt_file)
        metadata.update(asdict(PromptRecord.capture(prompt)))
        request = build_request(prompt)
        metadata["request_sha256"] = hashlib.sha256(encode_request(request)).hexdigest()
        if args.live:
            result = classify_recorded(prompt, api_key=os.environ.get("TYPESAFE_API_KEY", ""),
                                       run_dir=args.run_dir, example_id=args.example_id)
        else:
            # Deliberately expose the full body for local review, never pretend it is a prediction.
            result = {**metadata, "status": "preview", "request_attempted": False, "request": request}
        failed = result["status"] not in ("ok", "preview")
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), file=sys.stderr if failed else sys.stdout)
        return 130 if result["status"] == "interrupted" else int(failed)
    except RunRecordError as exc:
        print(json.dumps({**metadata, **exc.to_dict()}, indent=2, allow_nan=False), file=sys.stderr)
        return 1
    except ContractError as exc:
        detail = {
            "code": exc.code, "message": str(exc), "request_attempted": False,
        }
        print(json.dumps({**metadata, "status": "error", "error": detail}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
