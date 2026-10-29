"""Persistent admission budgets, not a guarantee of a provider's final bill.

Reserve before dispatch; never free an uncertain attempt automatically. The lock
serializes local workflows sharing a ledger, including across terminal restarts.
"""

from decimal import Decimal, InvalidOperation
import fcntl
import json
import os
from pathlib import Path

from .records import ContractError
from .run_records import _write_json
from .workflow_records import now

DEFAULT_BUDGET_FILE = Path("runs/part-2-budget.json")
JEV_RESERVATION = Decimal("0.001")  # >20k input tokens at the dated Jev rate.
PRICE_DATE = "2026-10-29"
PRICE_SOURCE = "https://developers.openai.com/api/docs/pricing"
# Budget conservatively at the highest Standard short-context cache-write rate.
# No cache-read discount; output already includes reasoning. Not actual billing.
CODING_RATES = {"gpt-6-luna": (Decimal("0.25"), Decimal("0.50")),
                "gpt-6.1-sol": (Decimal("5"), Decimal("10"))}


def money(value) -> Decimal:
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0:
            raise ValueError
        return amount
    except (InvalidOperation, ValueError):
        raise ContractError("invalid_budget", "Budget amounts must be finite, nonnegative USD amounts.") from None


def coding_reservation(model: str) -> Decimal:
    input_rate, output_rate = CODING_RATES[model]
    return (100_000 * input_rate + 10_000 * output_rate) / 1_000_000


def coding_estimate(usage: dict | None, model: str) -> dict:
    counts = [usage.get(name) if usage else None for name in ("inputTokens", "outputTokens")]
    known = all(type(v) is int and v >= 0 for v in counts)
    rates = CODING_RATES[model]
    amount = (counts[0] * rates[0] + counts[1] * rates[1]) / 1_000_000 if known else None
    return {"amount_usd": str(amount) if amount is not None else None,
            "kind": "conservative_admission_estimate", "actual_billed_cost_usd": None,
            "basis": "full_observed_thread_usage_at_current_model_rates",
            "input_usd_per_million": str(rates[0]), "output_usd_per_million": str(rates[1]),
            "pricing_date": PRICE_DATE, "pricing_source": PRICE_SOURCE,
            "limitation": "May include prior turns after resume; not per-turn experimental cost. Usage and billing can arrive late."}


class BudgetLedger:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.lock = None
        self.data = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(str(self.path) + ".lock", os.O_CREAT | os.O_RDWR, 0o600)
        self.lock = os.fdopen(fd, "r+")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise ContractError("budget_busy", "Another workflow is using this budget. Wait for it to finish.") from None
        try:
            if self.path.exists():
                self.data = read_budget(self.path)
            return self
        except BaseException:
            self.__exit__()
            raise

    def __exit__(self, *_):
        if self.lock is not None:
            self.lock.close()

    def save(self):
        try:
            _write_json(self.path, self.data)
        except OSError:
            raise ContractError("budget_storage_error", "Could not persist the budget. No further calls may be scheduled; inspect pending entries.") from None

    def initialize(self, *, jev_usd, openai_usd, max_jev_requests: int, max_coding_turns: int):
        caps = {"jev": str(money(jev_usd)), "openai": str(money(openai_usd))}
        limits = {"jev": max_jev_requests, "openai": max_coding_turns}
        if any(type(n) is not int or n < 0 for n in limits.values()):
            raise ContractError("invalid_budget", "Request/turn limits must be nonnegative integers.")
        if self.data is not None:
            if self.data["caps_usd"] != caps or self.data["attempt_limits"] != limits:
                raise ContractError("budget_exists", "This budget already exists. It cannot be reset or increased by initialization.")
            return self.summary()
        self.data = {"schema_version": "admission-budget-1", "created_at": now(),
                     "caps_usd": caps, "attempt_limits": limits, "entries": {}}
        self.save()
        return self.summary()

    def require(self):
        if self.data is None:
            raise ContractError("budget_missing", "Initialize an explicit spending budget with adaptive-code budget init before live work.")

    def remaining(self, provider: str) -> Decimal:
        self.require()
        return money(self.data["caps_usd"][provider]) - sum(
            (money(e["charge_usd"]) if e["charge_usd"] is not None else
             max(money(e["reserved_usd"]), money(e.get("observed_estimate_usd") or "0"))
             for e in self.data["entries"].values() if e["provider"] == provider), Decimal(0))

    def check(self, provider: str, amount: Decimal):
        self.require()
        if any(e["status"] in ("pending", "uncertain") for e in self.data["entries"].values()):
            raise ContractError("budget_uncertain", "A pending or uncertain attempt needs reconciliation. It will not be replayed or treated as free.")
        attempts = sum(e["provider"] == provider and e["attempted"] is not False
                       for e in self.data["entries"].values())
        if attempts >= self.data["attempt_limits"][provider] or self.remaining(provider) < amount:
            raise ContractError("budget_exhausted", "The remaining provider budget or attempt limit cannot cover this request.")

    def reserve(self, identifier: str, provider: str, amount: Decimal):
        amount = money(amount)
        self.check(provider, amount)
        if identifier in self.data["entries"]:
            raise ContractError("duplicate_attempt", "This attempt already has a budget record; it cannot be dispatched twice.")
        self.data["entries"][identifier] = {"provider": provider, "reserved_usd": str(amount),
            "charge_usd": None, "status": "pending", "attempted": False, "created_at": now(),
            "record_path": None, "actual_billed_cost_usd": None}
        self.save()

    def dispatch(self, identifier: str):
        self.data["entries"][identifier]["attempted"] = None
        self.save()  # Intent is durable before the network request.

    def settle(self, identifier: str, *, amount, attempted, record_path: str, observed_estimate=None):
        entry = self.data["entries"][identifier]
        if entry["status"] != "pending":
            raise ContractError("duplicate_settlement", "The budget entry has already been settled.")
        entry.update(charge_usd=str(money(amount)) if amount is not None else None,
                     observed_estimate_usd=str(money(observed_estimate)) if observed_estimate is not None else None,
                     attempted=attempted, record_path=record_path,
                     status="accounted" if amount is not None else "uncertain", finished_at=now())
        self.save()

    def summary(self):
        self.require()
        return {**self.data, "budget_file": str(self.path),
                "remaining_usd": {p: str(self.remaining(p)) for p in ("jev", "openai")},
                "warning": "Admission accounting only. Unknown charges retain reservations and block further calls. In-flight billing may exceed a reservation."}


def read_budget(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
        if value["schema_version"] != "admission-budget-1" or not isinstance(value["entries"], dict):
            raise ValueError
        for provider in ("jev", "openai"):
            money(value["caps_usd"][provider])
            if type(value["attempt_limits"][provider]) is not int or value["attempt_limits"][provider] < 0:
                raise ValueError
        for entry in value["entries"].values():
            if entry["provider"] not in ("jev", "openai") or entry["status"] not in ("pending", "accounted", "uncertain"):
                raise ValueError
            money(entry["reserved_usd"])
            if entry["charge_usd"] is not None:
                money(entry["charge_usd"])
            if entry.get("observed_estimate_usd") is not None:
                money(entry["observed_estimate_usd"])
            if entry["status"] == "accounted" and entry["charge_usd"] is None:
                raise ValueError
            if entry["attempted"] is not None and type(entry["attempted"]) is not bool:
                raise ValueError
        return value
    except (OSError, ValueError, KeyError, TypeError):
        raise ContractError("invalid_budget_file", "The budget file is missing or invalid. Do not reset it to clear uncertain spending.") from None
