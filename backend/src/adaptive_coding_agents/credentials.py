"""Read two local credentials without executing a shell or changing its environment."""

from dataclasses import dataclass, field
import os
from pathlib import Path
import re

from .records import ContractError

KEYS = ("TYPESAFE_API_KEY", "OPENAI_API_KEY")


@dataclass(frozen=True)
class Credentials:
    typesafe: str = field(default="", repr=False)
    openai: str = field(default="", repr=False)


def load_credentials(path: Path | None = Path(".env")) -> Credentials:
    """Environment wins (including explicit empty values). No expansion/interpolation.

    Only the specified file is read; never search parent directories or credential
    stores. Previews do not call this function. Error messages never include values.
    """
    values = {}
    if path is not None:
        try:
            with path.open("rb") as stream:
                raw = stream.read(16_385)
        except FileNotFoundError:
            raw = b""
        except OSError:
            raise ContractError("env_file_error", "Unable to read the specified environment file.") from None
        try:
            if len(raw) > 16_384:
                raise ValueError
            for line in raw.decode("utf-8-sig").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                name, separator, value = line.partition("=")
                name, value = name.strip(), value.strip()
                if not separator or name not in KEYS or name in values:
                    raise ValueError
                if value[:1] in ("'", '"'):
                    if len(value) < 2 or value[-1] != value[0]:
                        raise ValueError
                    value = value[1:-1]
                if value and re.fullmatch(r"[A-Za-z0-9_.-]+", value) is None:
                    raise ValueError
                values[name] = value
        except (UnicodeError, ValueError):
            raise ContractError("invalid_env_file", "Use unique TYPESAFE_API_KEY= and OPENAI_API_KEY= entries with literal, single-line keys. Values were not displayed.") from None
    result = [os.environ[name] if name in os.environ else values.get(name, "") for name in KEYS]
    return Credentials(*result)


def validate_openai_key(value: str) -> None:
    if not isinstance(value, str) or not value or re.fullmatch(r"[A-Za-z0-9_.-]+", value) is None:
        raise ContractError("missing_openai_credentials", "Set a nonempty OPENAI_API_KEY in the environment or the selected .env file.")
