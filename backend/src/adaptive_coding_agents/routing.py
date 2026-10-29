"""Small explicit model registry and a provisional engineering policy.

This mapping exercises integration; it is not learned from benchmark outcomes.
Part 3 will replace it with a policy supported by development measurements.
"""

from dataclasses import asdict, dataclass

from .records import ContractError, Labels
from .taxonomy import TAXONOMY_VERSION

REGISTRY_VERSION = "gpt-pilot-1"
POLICY_VERSION = "engineering-2"
POLICY_EVIDENCE = "unvalidated_engineering_mapping"
CHECKED_ON = "2026-10-29"
DEFAULT_FALLBACK = "sol-high"


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
    fallback: bool = False

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


def select_route(labels: Labels, eligible: set[str] | None = None,
                 fallback_id: str = DEFAULT_FALLBACK) -> Route:
    """Use labels only; eligibility is operational information, not a feature.

    A fixed provisional fallback handles ambiguity or an unavailable preferred
    route. It must fit both the supported catalog and remaining budget. Its
    reliability is a hypothesis until the Part 3 development measurements.
    """
    configurations = {config.id: config for config in CONFIGURATIONS}
    if fallback_id not in configurations:
        raise ContractError("invalid_fallback", "Fallback must be an explicit registry configuration.")
    fallback = False
    if labels.task_type == "mixed_or_unclear" or "unknown" in (
        labels.cause_evidence, labels.change_scope,
    ):
        config_id, reason, fallback = fallback_id, "Prompt-only evidence is insufficient; provisional fallback.", True
    elif labels.change_scope == "cross_component":
        config_id, reason = "sol-high", "Explicit cross-component scope."
    elif labels.task_type == "diagnose" or labels.cause_evidence == "hypothesis_only":
        config_id, reason = "luna-high", "Localized investigation or an unsupported cause hypothesis."
    elif labels.task_type == "validate":
        config_id, reason = "sol-low", "Localized validation with supporting details."
    else:
        config_id, reason = "luna-low", "Localized repair with supporting details."
    if eligible is not None and config_id not in eligible:
        if fallback_id not in eligible:
            raise ContractError("fallback_unavailable", "Neither the preferred route nor the fallback is eligible within availability and budget.")
        config_id, reason, fallback = fallback_id, "Preferred configuration unavailable or outside budget; provisional fallback.", True
    return Route(configurations[config_id], labels, reason, fallback)
