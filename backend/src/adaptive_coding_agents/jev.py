"""Direct TypeSafe System One client. One request, no retries or fallback labels.

Contract checked 2026-10-25:
https://docs.typesafe.ai/api/system-one
https://docs.typesafe.ai/primitives/choice
https://docs.typesafe.ai/models
"""

import hashlib
from http.client import HTTPException
import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .records import Classification, ChoiceAnswer, ContractError, Labels, PromptRecord, TokenUsage
from .taxonomy import category_questions

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.14.0"
TIMEOUT_SECONDS = 30
RESPONSE_LIMIT_BYTES = 1_048_576


def build_request(prompt: str) -> dict:
    PromptRecord.capture(prompt)
    return {"model": MODEL, "state": prompt, "questions": category_questions()}


def encode_request(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


class JevError(RuntimeError):
    """Sanitized failure metadata; provider bodies may contain private input."""

    def __init__(self, code: str, message: str, *, http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.request_attempted = False
        self.elapsed_ms = 0
        self.usage = TokenUsage()
        self.returned_model: str | None = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": str(self),
            "http_status": self.http_status,
            "request_attempted": self.request_attempted,
            "elapsed_ms": self.elapsed_ms,
            "usage": self.usage.to_dict(),
            "returned_model": self.returned_model,
        }


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a credential or repeat a paid request at a redirected URL.
        return None


def _post(body: bytes, api_key: str, timeout: float) -> bytes:
    request = Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with build_opener(_NoRedirect()).open(request, timeout=timeout) as response:
            if response.status != 200:
                raise JevError("http_error", "TypeSafe returned an unexpected HTTP status.", http_status=response.status)
            content = response.read(RESPONSE_LIMIT_BYTES + 1)
            if len(content) > RESPONSE_LIMIT_BYTES:
                raise JevError("invalid_response", "TypeSafe's response exceeded the local size limit.")
            return content
    except HTTPError as exc:
        status = exc.code
        exc.close()
        if status in (401, 403):
            code, message = "authentication_error", "TypeSafe rejected access; check the API key and account permissions."
        elif status == 402:
            code, message = "billing_error", "TypeSafe requires billing or credits for this request."
        elif status == 429:
            code, message = "rate_limited", "TypeSafe rate limited the request; no retry was made."
        elif status >= 500:
            code, message = "provider_error", "TypeSafe reported a service failure; no retry was made."
        else:
            code, message = "http_error", "TypeSafe rejected the request; no retry was made."
        raise JevError(code, message, http_status=status) from None
    except (TimeoutError, URLError, OSError, HTTPException) as exc:
        timed_out = isinstance(exc, TimeoutError) or isinstance(getattr(exc, "reason", None), TimeoutError)
        code = "timeout" if timed_out else "network_error"
        raise JevError(code, "No complete response was received; the request may have been processed. No retry was made.") from None


def _usage(value: object) -> TokenUsage:
    if value is None:
        return TokenUsage()
    if not isinstance(value, dict):
        raise ContractError("invalid_response", "Invalid usage object.")
    counts = {}
    for name in ("input_tokens", "output_tokens"):
        count = value.get(name)
        if count is not None and (type(count) is not int or count < 0):
            raise ContractError("invalid_response", "Invalid provider token count.")
        counts[name] = count
    return TokenUsage(**counts)


def _probability(value: object) -> float:
    if type(value) not in (int, float) or not 0 <= value <= 1:
        raise ContractError("invalid_response", "Expected a finite probability between zero and one.")
    return float(value)


def _answers(value: object) -> dict[str, ChoiceAnswer]:
    if not isinstance(value, dict) or set(value) != set(Labels.OPTIONS):
        raise ContractError("invalid_response", "Expected answers for exactly the three category questions.")
    answers = {}
    for name, choices in Labels.OPTIONS.items():
        answer = value[name]
        if not isinstance(answer, dict) or answer.get("type") != "choice":
            raise ContractError("invalid_response", "Expected a Choice answer.")
        selected = answer.get("choice")
        if not isinstance(selected, str) or selected not in choices:
            raise ContractError("invalid_response", f"Invalid category for {name}.")
        probabilities = answer.get("probabilities")
        if not isinstance(probabilities, dict) or set(probabilities) != set(choices):
            raise ContractError("invalid_response", "Expected a probability for every category option.")
        probabilities = {label: _probability(score) for label, score in probabilities.items()}
        if not math.isclose(sum(probabilities.values()), 1.0, rel_tol=0, abs_tol=1e-5):
            raise ContractError("invalid_response", "Category probabilities must sum to one.")
        if probabilities[selected] < max(probabilities.values()) - 1e-5:
            raise ContractError("invalid_response", "The chosen category does not have the highest probability.")
        answers[name] = ChoiceAnswer(selected, _probability(answer.get("confidence")), probabilities)
    Labels.from_dict({name: answer.choice for name, answer in answers.items()})
    return answers


class JevClient:
    """Explicit live client; constructing it does not contact TypeSafe."""

    def __init__(self, api_key: str, *, timeout: float = TIMEOUT_SECONDS):
        if not isinstance(api_key, str) or not api_key or not all(33 <= ord(char) <= 126 for char in api_key):
            raise JevError("missing_credentials", "Set TYPESAFE_API_KEY to a valid nonempty API key for live calls.")
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be a finite positive number.")
        self._api_key = api_key
        self._timeout = timeout

    def classify(self, prompt: str) -> Classification:
        prompt_record = PromptRecord.capture(prompt)
        body = encode_request(build_request(prompt))
        started = time.perf_counter()
        usage = TokenUsage()
        returned_model = None
        try:
            raw = _post(body, self._api_key, self._timeout)
            try:
                response = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, ValueError, RecursionError):
                raise ContractError("invalid_response", "TypeSafe returned invalid UTF-8 JSON.") from None
            if not isinstance(response, dict):
                raise ContractError("invalid_response", "Expected a response object.")
            usage = _usage(response.get("usage"))
            model_value = response.get("model")
            if not isinstance(model_value, str) or not model_value.strip():
                raise ContractError("invalid_response", "Missing returned model identifier.")
            returned_model = model_value
            answers = _answers(response.get("answers"))
            return Classification(
                prompt_record, hashlib.sha256(body).hexdigest(), MODEL, returned_model,
                answers, usage, round((time.perf_counter() - started) * 1000),
            )
        except (JevError, ContractError) as exc:
            error = exc if isinstance(exc, JevError) else JevError(exc.code, str(exc))
            error.request_attempted = True
            error.elapsed_ms = round((time.perf_counter() - started) * 1000)
            error.usage = usage
            error.returned_model = returned_model
            raise error from None
