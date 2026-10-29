"""Record one live classification attempt before dispatch and after completion.

No prompt text, credentials, or raw provider error bodies are persisted. A pending
record after a crash means the outcome is unknown; it must never trigger replay.
"""

from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from uuid import uuid4

from . import __version__
from .jev import ENDPOINT, MODEL, JevClient, JevError, build_request, encode_request
from .records import ContractError, PromptRecord, SCHEMA_VERSION, TokenUsage
from .taxonomy import TAXONOMY_VERSION

DEFAULT_RUN_DIR = Path("runs/jev")
RECORD_SCHEMA_VERSION = "jev-attempt-1"
PRICE_INPUT_PER_MILLION_USD = Decimal("0.042")
PRICING_CHECKED_ON = "2026-10-27"
PRICING_SOURCE = "https://docs.typesafe.ai/models"


def validate_example_id(value: str | None) -> None:
    if value is not None and (not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value) is None):
        raise ContractError("invalid_example_id", "Example IDs must be 1-64 letters, digits, dots, underscores, or hyphens, starting with a letter or digit.")


def estimate_cost(usage: dict, returned_model: str | None) -> dict:
    """A dated estimate from reported input tokens, never an actual billed amount."""
    count = usage.get("input_tokens")
    known_count = type(count) is int and count >= 0
    priced_model = returned_model == MODEL
    amount = PRICE_INPUT_PER_MILLION_USD * count / Decimal(1_000_000) if known_count and priced_model else None
    return {
        "status": "estimated" if amount is not None else "unavailable",
        "estimated_cost_usd": format(amount, "f") if amount is not None else None,
        "basis": "provider_input_tokens" if amount is not None else None,
        "reason": None if amount is not None else ("missing_input_usage" if not known_count else "unverified_model_pricing"),
        "priced_model": MODEL,
        "input_usd_per_million_tokens": str(PRICE_INPUT_PER_MILLION_USD),
        "output_usd_per_million_tokens": "0",
        "pricing_checked_on": PRICING_CHECKED_ON,
        "pricing_source": PRICING_SOURCE,
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, data: dict) -> None:
    """Replace a record atomically using a private, flushed temporary file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".attempt-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class RunRecordError(RuntimeError):
    """Storage failed; an observed result may still be returned for manual recovery."""

    def __init__(self, *, path: Path, observed_result: dict | None = None):
        super().__init__("Unable to save the attempt record. Inspect the record and observed result before any manual retry.")
        self.path = path
        self.observed_result = observed_result

    def to_dict(self) -> dict:
        return {
            "status": "error",
            "record_path": str(self.path),
            "error": {
                "code": "recording_error",
                "message": str(self),
                "request_attempted": False if self.observed_result is None else self.observed_result.get("request_attempted"),
            },
            "observed_result": self.observed_result,
        }


def classify_recorded(prompt: str, *, api_key: str, run_dir: Path = DEFAULT_RUN_DIR,
                      example_id: str | None = None) -> dict:
    """Persist intent, call the existing client once, and save its safe summary.

Input/ID errors are rejected before creating records. Missing credentials produce
an error record with request_attempted=false. Storage failure before dispatch
prevents the call; storage failure afterward surfaces the observed result.
"""
    validate_example_id(example_id)
    prompt_record = PromptRecord.capture(prompt)
    request = build_request(prompt)
    run_id = str(uuid4())
    path = Path(run_dir) / run_id / "attempt.json"
    data = {
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "example_id": example_id,
        "started_at": _now(),
        "finished_at": None,
        "status": "pending",
        "mode": "live",
        "provider": "typesafe",
        "endpoint": ENDPOINT,
        "client_version": __version__,
        "requested_model": MODEL,
        "returned_model": None,
        "taxonomy_version": TAXONOMY_VERSION,
        "input_policy_version": "prompt-only-1",
        **asdict(prompt_record),
        "request_sha256": hashlib.sha256(encode_request(request)).hexdigest(),
        "questions_sha256": hashlib.sha256(encode_request(request["questions"])).hexdigest(),
        "questions": request["questions"],
        "question_count": len(request["questions"]),
        "request_attempted": None,
        "usage": TokenUsage().to_dict(),
        "cost_estimate": estimate_cost({}, None),
    }
    try:
        path.parent.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.parent.mkdir(mode=0o700)  # A unique directory; never overwrite a prior attempt.
        _write_json(path, data)
    except OSError:
        raise RunRecordError(path=path) from None

    started = time.perf_counter()
    dispatched = False
    try:
        client = JevClient(api_key)
        dispatched = True
        outcome = client.classify(prompt).to_dict()
    except (JevError, ContractError) as exc:
        detail = exc.to_dict() if isinstance(exc, JevError) else {
            "code": exc.code, "message": str(exc), "request_attempted": False,
        }
        outcome = {
            "status": "error",
            "request_attempted": detail["request_attempted"],
            "elapsed_ms": detail.get("elapsed_ms", round((time.perf_counter() - started) * 1000)),
            "returned_model": detail.get("returned_model"),
            "usage": detail.get("usage", TokenUsage().to_dict()),
            "error": detail,
        }
    except (KeyboardInterrupt, Exception) as exc:
        # Suppress unexpected exception text because it may contain request data.
        interrupted = isinstance(exc, KeyboardInterrupt)
        outcome = {
            "status": "interrupted" if interrupted else "error",
            "request_attempted": None if dispatched else False,
            "elapsed_ms": round((time.perf_counter() - started) * 1000),
            "returned_model": None,
            "usage": TokenUsage().to_dict(),
            "error": {
                "code": "interrupted" if interrupted else "internal_error",
                "message": "No complete result was captured. The request may have been processed; no retry was made." if dispatched else "The client stopped before dispatch; no request was made.",
            },
        }
    completed = {**data, **outcome, "finished_at": _now(),
                 "cost_estimate": estimate_cost(outcome["usage"], outcome.get("returned_model"))}
    try:
        _write_json(path, completed)
    except OSError:
        raise RunRecordError(path=path, observed_result=completed) from None
    return {**completed, "record_path": str(path)}
