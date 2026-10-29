"""Prompt validation and records for classification; no routing or execution state."""

from dataclasses import asdict, dataclass
import hashlib
from typing import ClassVar

from .taxonomy import LABEL_OPTIONS, TAXONOMY_VERSION

SCHEMA_VERSION = "jev-classification-1"
PROMPT_LIMIT_BYTES = 16_384


class ContractError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PromptRecord:
    prompt_sha256: str
    utf8_bytes: int

    @classmethod
    def capture(cls, text: str) -> "PromptRecord":
        if not isinstance(text, str):
            raise ContractError("unsupported_input", "The prompt must be UTF-8 text.")
        try:
            encoded = text.encode("utf-8")
        except UnicodeEncodeError:
            raise ContractError("invalid_utf8", "The prompt must be valid UTF-8 text.") from None
        if len(encoded) > PROMPT_LIMIT_BYTES:
            raise ContractError("prompt_too_large", f"The prompt exceeds {PROMPT_LIMIT_BYTES} UTF-8 bytes.")
        if not text.strip():
            raise ContractError("empty_prompt", "Provide a nonempty prompt.")
        return cls(hashlib.sha256(encoded).hexdigest(), len(encoded))


@dataclass(frozen=True)
class Labels:
    task_type: str
    cause_evidence: str
    change_scope: str

    OPTIONS: ClassVar[dict[str, tuple[str, ...]]] = LABEL_OPTIONS

    def __post_init__(self) -> None:
        for name, choices in self.OPTIONS.items():
            if not isinstance(getattr(self, name), str) or getattr(self, name) not in choices:
                raise ContractError("invalid_response", f"Invalid category for {name}.")

    @classmethod
    def from_dict(cls, value: object) -> "Labels":
        if not isinstance(value, dict) or set(value) != set(cls.OPTIONS):
            raise ContractError("invalid_response", "Expected exactly the three category fields.")
        return cls(**value)


@dataclass(frozen=True)
class ChoiceAnswer:
    choice: str
    confidence: float
    probabilities: dict[str, float]


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None

    def to_dict(self) -> dict:
        available = sum(value is not None for value in (self.input_tokens, self.output_tokens))
        return {
            **asdict(self),
            "status": ("unavailable", "partial", "available")[available],
            "source": "provider" if available else None,
            "billed_cost_usd": None,
        }


@dataclass(frozen=True)
class Classification:
    prompt: PromptRecord
    request_sha256: str
    requested_model: str
    returned_model: str
    answers: dict[str, ChoiceAnswer]
    usage: TokenUsage
    elapsed_ms: int

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "ok",
            "mode": "live",
            "provider": "typesafe",
            "taxonomy_version": TAXONOMY_VERSION,
            "input_policy_version": "prompt-only-1",
            **asdict(self.prompt),
            "request_sha256": self.request_sha256,
            "requested_model": self.requested_model,
            "returned_model": self.returned_model,
            "question_count": len(self.answers),
            "labels": {name: answer.choice for name, answer in self.answers.items()},
            "answers": {name: asdict(answer) for name, answer in self.answers.items()},
            "usage": self.usage.to_dict(),
            "elapsed_ms": self.elapsed_ms,
            "request_attempted": True,
        }
