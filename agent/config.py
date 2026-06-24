from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class LMStudioConfig:
    base_url: str = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    api_key: str = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
    model: str | None = os.getenv("LMSTUDIO_MODEL") or None
    temperature: float = _get_float("LMSTUDIO_TEMPERATURE", 0.5)
    max_tokens: int = _get_int("LMSTUDIO_MAX_TOKENS", 300)
    memory_turns: int = _get_int("AGENT_MEMORY_TURNS", 6)
