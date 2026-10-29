"""Offline repricing of observed tokens. This never runs a baseline model.

Same-token scenarios do not predict a different model's output length, quality,
latency, or cache behavior. They are not measured routing savings or invoices.
"""

from decimal import Decimal, InvalidOperation

from .records import ContractError
from .routing import CONFIGURATIONS

PRICING_DATE = "2026-10-29"
PRICE_SOURCES = [
    "https://developers.openai.com/api/docs/models/gpt-6-luna",
    "https://developers.openai.com/api/docs/models/gpt-6.1-sol",
    "https://developers.openai.com/api/docs/guides/prompt-caching",
]
# Standard, <=272k input tokens per request, USD per million tokens.
# Cache-write pricing replaces ordinary input pricing; it is not an extra fee.
RATES = {
    "gpt-6-luna": dict(input="0.10", cached="0.01", write="0.125", output="0.50"),
    "gpt-6.1-sol": dict(input="2.00", cached="0.10", write="2.50", output="10.00"),
}


def reprice(usage: dict | None, model: str, *, cache_lifetime: str = "30m") -> dict:
    if cache_lifetime not in ("30m", "12h"):
        raise ContractError("invalid_pricing_scenario", "Choose 30m or 12h cache writes.")
    unavailable = {"amount_usd": None, "reason": "Token usage is unavailable."}
    if not isinstance(usage, dict) or model not in RATES:
        return unavailable
    names = ("inputTokens", "cachedInputTokens", "cacheWriteInputTokens", "outputTokens")
    if any(type(usage.get(key)) is not int or usage[key] < 0 for key in names):
        return {**unavailable, "reason": "The full input, cache-read, cache-write, and output breakdown is unavailable."}
    total, cached, written, output = (usage[key] for key in names)
    plain = total - cached - written
    if plain < 0:
        return {**unavailable, "reason": "The token breakdown is inconsistent."}
    rates = {key: Decimal(value) for key, value in RATES[model].items()}
    if cache_lifetime == "12h":
        rates["write"] *= 2
    counts = dict(input=plain, cached=cached, write=written, output=output)
    parts = {key: Decimal(counts[key]) * rates[key] / 1_000_000 for key in counts}
    return {"amount_usd": str(sum(parts.values())), "reason": None,
            "counts": counts, "rates_per_million": {k: str(v) for k, v in rates.items()},
            "breakdown_usd": {k: str(v) for k, v in parts.items()}}


def compare_record(record: dict, classifier: dict | None, *, baseline_id: str = "sol-high",
                   cache_lifetime: str = "30m") -> dict:
    registry = {config.id: config for config in CONFIGURATIONS}
    if baseline_id not in registry:
        raise ContractError("invalid_baseline", "Choose a configuration from the project registry.")
    baseline = registry[baseline_id]
    route = record.get("route") or {}
    selected = route.get("configuration") or {}
    per_turn = record.get("coding_turn_usage")
    usage = per_turn if per_turn is not None else record.get("coding_usage")
    exact_turn = per_turn is not None
    routed = reprice(usage, selected.get("model"), cache_lifetime=cache_lifetime)
    fixed = reprice(usage, baseline.model, cache_lifetime=cache_lifetime)
    raw_jev = ((classifier or {}).get("cost_estimate") or {}).get("estimated_cost_usd")
    jev = None
    try:
        candidate = Decimal(str(raw_jev))
        if candidate.is_finite() and candidate >= 0:
            jev = candidate
    except (InvalidOperation, ValueError, TypeError):
        pass
    complete = (record.get("status") == "completed" and record.get("turn_completion_observed") is True
                and record.get("accounting_status") != "uncertain" and not record.get("observed_reroute"))
    available = complete and routed["amount_usd"] is not None and fixed["amount_usd"] is not None and jev is not None
    routed_total = Decimal(routed["amount_usd"]) + jev if available else None
    delta = Decimal(fixed["amount_usd"]) - routed_total if available else None
    reason = None if available else ("This run is incomplete or has uncertain final usage." if not complete else
              routed.get("reason") or fixed.get("reason") or "Classifier cost is unavailable.")
    return {
        "available": available, "unavailable_reason": reason,
        "baseline": {"id": baseline.id, "model": baseline.model, "effort": baseline.effort},
        "selected": selected, "scope": "turn" if exact_turn else "thread_snapshot",
        "scope_label": "This turn's reported tokens" if exact_turn else "Observed thread snapshot; may include earlier turns",
        "routed_coding": routed, "fixed_coding": fixed,
        "classifier_estimate_usd": str(jev) if jev is not None else None,
        "routed_total_usd": str(routed_total) if routed_total is not None else None,
        "difference_usd": str(delta) if delta is not None else None,
        "actual_billed_cost_usd": None, "baseline_inference_requested": False,
        "pricing_date": PRICING_DATE, "pricing_sources": PRICE_SOURCES,
        "cache_lifetime": cache_lifetime,
        "assumptions": ["Same observed token counts and cache behavior for both configurations.",
            "Standard processing, at most 272k input tokens per individual request; no regional premium.",
            f"Cache-write lifetime assumed: {cache_lifetime}; actual lifetime is not recorded.",
            "Output includes reasoning tokens. Effort has no separate price multiplier here.",
            "The baseline excludes Jev. Its actual tokens, quality, and latency could differ.",
            "Thread snapshots are not per-turn costs and are never summed across runs."],
    }
