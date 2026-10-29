"""One budgeted hosted classification, shared by the terminal and accuracy pilot."""

from pathlib import Path
from uuid import uuid4

from .budget import BudgetLedger, JEV_RESERVATION
from .jev import JevClient
from .records import PromptRecord
from .run_records import RunRecordError, classify_recorded


def classify_with_budget(prompt: str, *, api_key: str, ledger: BudgetLedger,
                         run_dir: Path, example_id: str | None = None) -> dict:
    PromptRecord.capture(prompt)
    JevClient(api_key)
    identifier = "jev-" + str(uuid4())
    ledger.reserve(identifier, "jev", JEV_RESERVATION)
    ledger.dispatch(identifier)
    try:
        result = classify_recorded(prompt, api_key=api_key, run_dir=run_dir, example_id=example_id)
    except RunRecordError as exc:
        ledger.settle(identifier, amount=None, attempted=None, record_path=str(exc.path))
        raise
    except BaseException:
        ledger.settle(identifier, amount=None, attempted=None, record_path=str(run_dir))
        raise
    attempted = result["request_attempted"]
    amount = "0" if attempted is False else result["cost_estimate"]["estimated_cost_usd"]
    ledger.settle(identifier, amount=amount, attempted=attempted, record_path=result["record_path"])
    return {**result, "budget_entry_id": identifier}
