"""Small explicit model registry and a provisional engineering policy.

This mapping exercises integration; it is not learned from benchmark outcomes.
Part 3 will replace it with a policy supported by development measurements.
"""

from dataclasses import asdict, dataclass

from .records import ContractError, Labels
from .taxonomy import TAXONOMY_VERSION

REGISTRY_VERSION = "gpt-pilot-1"
POLICY_VERSION = "engineering-1"
POLICY_EVIDENCE = "unvalidated_engineering_mapping"
CHECKED_ON = "2026-10-28"


@dataclass(frozen=True)
class Configuration:
    id: str
    model: str
    effort: str


# These pairs are documented capabilities, not proof of account access.
# The live adapter checks Codex's paginated model catalog before classification.
CONFIGURATIONS = (
    Configuration("luna-low", "gpt-6-luna", "low"),
    Configuration("luna-high", "gpt-6-luna", "high"),
    Configuration("sol-low", "gpt-6.1-sol", "low"),
    Configuration("sol-high", "gpt-6.1-sol", "high"),
)
MODEL_SOURCES = {
    "gpt-6-luna": "https://developers.openai.com/api/docs/models/gpt-6-luna",
    "gpt-6.1-sol": "https://developers.openai.com/api/docs/models/gpt-6.1-sol",
}


@dataclass(frozen=True)
class Route:
    configuration: Configuration
    labels: Labels
    reason: str

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "registry_version": REGISTRY_VERSION,
            "policy_version": POLICY_VERSION,
            "policy_evidence": POLICY_EVIDENCE,
            "taxonomy_version": TAXONOMY_VERSION,
        }


def registry_preview() -> dict:
    return {
        "version": REGISTRY_VERSION,
        "checked_on": CHECKED_ON,
        "sources": MODEL_SOURCES.copy(),
        "account_access": "unverified",
        "configurations": [asdict(config) for config in CONFIGURATIONS],
    }


def select_route(labels: Labels, eligible: set[str] | None = None) -> Route:
    """Use labels only; eligibility is operational information, not a feature.

    Unknowns stop this first slice. Automatic reliable fallback and its budget
    rules belong to Part 2; do not pretend the provisional map establishes one.
    An unavailable chosen route stops rather than silently switching models.
    """
    if labels.task_type == "mixed_or_unclear" or "unknown" in (
        labels.cause_evidence, labels.change_scope,
    ):
        raise ContractError("fallback_pending", "This prompt needs fallback handling, which is the Part 2 checkpoint. No coding turn was started.")
    if labels.change_scope == "cross_component":
        config_id, reason = "sol-high", "Explicit cross-component scope."
    elif labels.task_type == "diagnose" or labels.cause_evidence == "hypothesis_only":
        config_id, reason = "luna-high", "Localized investigation or an unsupported cause hypothesis."
    elif labels.task_type == "validate":
        config_id, reason = "sol-low", "Localized validation with supporting details."
    else:
        config_id, reason = "luna-low", "Localized repair with supporting details."
    if eligible is not None and config_id not in eligible:
        raise ContractError("configuration_unavailable", f"The selected configuration {config_id} is not in Codex's supported catalog. No coding turn was started.")
    config = next(item for item in CONFIGURATIONS if item.id == config_id)
    return Route(config, labels, reason)
