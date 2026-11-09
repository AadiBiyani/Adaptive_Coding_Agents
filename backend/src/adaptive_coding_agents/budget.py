"""Persistent admission budgets, not a guarantee of a provider's final bill.

Reserve before dispatch; never free an uncertain attempt automatically. The lock
serializes local workflows sharing a ledger, including across terminal restarts.
"""

from copy import deepcopy
from decimal import Decimal, InvalidOperation
import fcntl
import json
import os
from pathlib import Path

from .records import ContractError
from .run_records import _write_json, validate_example_id
from .workflow_records import now

DEFAULT_BUDGET_FILE = Path("runs/part-2-budget.json")
DEFAULT_CHAT_TURN_LIMIT = 10
CLASSIFIER_EXPERIMENT = "classifier-pilot"
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
    def __init__(self, path: Path, *, purpose: str = "interactive"):
        if not isinstance(purpose, str):
            raise ContractError("invalid_experiment", "Use interactive or a named experiment allocation.")
        validate_example_id(purpose)
        self.path = path.resolve()
        self.purpose = purpose
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

    def enable_demo_controls(self, *, turns_per_chat=DEFAULT_CHAT_TURN_LIMIT):
        """Explicit, audited migration. Never replenish dollars or erase attempts."""
        self.require()
        if type(turns_per_chat) is not int or not 1 <= turns_per_chat <= 100:
            raise ContractError("invalid_chat_limit", "Choose 1–100 user turns per chat.")
        if self.data["schema_version"] == "admission-budget-2":
            if self.data["chat_turn_limit"] != turns_per_chat:
                raise ContractError("budget_exists", "Demo controls already exist with a different chat limit; they will not be reset.")
            return self.summary()
        if any(e["status"] in ("pending", "uncertain") for e in self.data["entries"].values()):
            raise ContractError("budget_uncertain", "Reconcile pending or uncertain spending before changing the demo controls.")
        original = deepcopy(self.data)
        backup = self.path.with_name(self.path.name + ".before-chat-controls.json")
        if backup.exists():
            try:
                if json.loads(backup.read_text()) != original:
                    raise ValueError
            except (OSError, ValueError):
                raise ContractError("migration_backup_exists", "An existing backup differs from this ledger. Inspect it before migrating.") from None
        else:
            _write_json(backup, original)
        coding_root = self.path.parent / "coding"
        legacy_purposes = {}
        for key, entry in original["entries"].items():
            # Historical coding calls (including their Jev calls) are interactive.
            # Other legacy Jev calls conservatively count toward the pilot quota.
            record_path = Path(entry["record_path"]).resolve() if entry.get("record_path") else None
            coding = entry["provider"] == "openai" or (record_path is not None and record_path.is_relative_to(coding_root))
            purpose = entry.get("purpose") or ("interactive" if coding else CLASSIFIER_EXPERIMENT)
            if purpose not in {"interactive", CLASSIFIER_EXPERIMENT}:
                raise ContractError("migration_scope_unknown", "An older attempt has an unknown experiment. Inspect its limits before migrating.")
            legacy_purposes[key] = purpose
        self.data = {**original, "schema_version": "admission-budget-2",
            "attempt_limits": {"jev": None, "openai": None}, "chat_turn_limit": turns_per_chat,
            "experiments": {CLASSIFIER_EXPERIMENT: {"attempt_limits": {"jev": 40, "openai": 0}, "created_at": now()}},
            "legacy_entry_purposes": legacy_purposes,
            "migration": {"from_schema": original["schema_version"], "migrated_at": now(),
                "previous_attempt_limits": original["attempt_limits"], "backup_path": str(backup),
                "dollar_caps_and_entries_preserved": True}}
        self.save()
        return self.summary()

    def allocate_experiment(self, name, *, max_jev_requests, max_coding_turns):
        self.require()
        if not isinstance(name, str):
            raise ContractError("invalid_experiment", "An experiment must have a name.")
        validate_example_id(name)
        limits = {"jev": max_jev_requests, "openai": max_coding_turns}
        if name == "interactive" or any(type(n) is not int or n < 0 for n in limits.values()):
            raise ContractError("invalid_experiment", "Use a named experiment and nonnegative request/turn limits.")
        if self.data["schema_version"] != "admission-budget-2":
            raise ContractError("demo_controls_required", "Enable the shared-dollar/chat controls before allocating an experiment.")
        existing = self.data["experiments"].get(name)
        if existing is not None:
            if existing["attempt_limits"] != limits:
                raise ContractError("experiment_exists", "This experiment's limits already exist and cannot be reset or increased.")
        else:
            self.data["experiments"][name] = {"attempt_limits": limits, "created_at": now()}
            self.save()
        return self.summary()

    def chat_turn_limit(self):
        self.require()
        return self.data.get("chat_turn_limit")

    def entry_purpose(self, entry_id, entry):
        return entry.get("purpose") or self.data.get("legacy_entry_purposes", {}).get(entry_id)

    def attempts_used(self, provider, *, purpose=None):
        self.require()
        scope = purpose or self.purpose
        return sum(e["provider"] == provider and e["attempted"] is not False and
            (self.data["schema_version"] == "admission-budget-1" or self.entry_purpose(key, e) == scope)
            for key, e in self.data["entries"].items())

    def attempt_limit(self, provider):
        self.require()
        if self.data["schema_version"] == "admission-budget-1":
            return self.data["attempt_limits"][provider]
        if self.purpose == "interactive":
            return None  # User turns are bounded by their chat/session instead.
        experiment = self.data["experiments"].get(self.purpose)
        if experiment is None:
            raise ContractError("experiment_unapproved", "Allocate request limits for this experiment before making calls.")
        return experiment["attempt_limits"][provider]

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
        limit = self.attempt_limit(provider)
        if (limit is not None and self.attempts_used(provider) >= limit) or self.remaining(provider) < amount:
            raise ContractError("budget_exhausted", "The remaining provider budget or attempt limit cannot cover this request.")

    def reserve(self, identifier: str, provider: str, amount: Decimal):
        amount = money(amount)
        self.check(provider, amount)
        if identifier in self.data["entries"]:
            raise ContractError("duplicate_attempt", "This attempt already has a budget record; it cannot be dispatched twice.")
        self.data["entries"][identifier] = {"provider": provider, "reserved_usd": str(amount),
            "charge_usd": None, "status": "pending", "attempted": False, "created_at": now(),
            "record_path": None, "actual_billed_cost_usd": None, "purpose": self.purpose}
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
        experiments = {name: {**config, "attempts_used": {p: self.attempts_used(p, purpose=name) for p in ("jev", "openai")}}
                       for name, config in self.data.get("experiments", {}).items()}
        return {**self.data, "budget_file": str(self.path),
                "purpose": self.purpose, "experiment_usage": experiments,
                "remaining_usd": {p: str(self.remaining(p)) for p in ("jev", "openai")},
                "warning": "Admission accounting only. Unknown charges retain reservations and block further calls. In-flight billing may exceed a reservation."}


def read_budget(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
        if value["schema_version"] not in ("admission-budget-1", "admission-budget-2") or not isinstance(value["entries"], dict):
            raise ValueError
        scoped = value["schema_version"] == "admission-budget-2"
        for provider in ("jev", "openai"):
            money(value["caps_usd"][provider])
            limit = value["attempt_limits"][provider]
            if (scoped and limit is not None) or (not scoped and (type(limit) is not int or limit < 0)):
                raise ValueError
        if scoped:
            if type(value["chat_turn_limit"]) is not int or not 1 <= value["chat_turn_limit"] <= 100:
                raise ValueError
            if not isinstance(value["experiments"], dict) or not isinstance(value["legacy_entry_purposes"], dict):
                raise ValueError
            for name, config in value["experiments"].items():
                validate_example_id(name)
                if name == "interactive" or any(type(config["attempt_limits"][p]) is not int or config["attempt_limits"][p] < 0 for p in ("jev", "openai")):
                    raise ValueError
            allowed = {"interactive", *value["experiments"]}
            if any(key not in value["entries"] or purpose not in allowed for key, purpose in value["legacy_entry_purposes"].items()):
                raise ValueError
        for key, entry in value["entries"].items():
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
            if scoped:
                purpose = entry.get("purpose") or value["legacy_entry_purposes"].get(key)
                if purpose not in allowed:
                    raise ValueError
        return value
    except (OSError, ValueError, KeyError, TypeError):
        raise ContractError("invalid_budget_file", "The budget file is missing or invalid. Do not reset it to clear uncertain spending.") from None
