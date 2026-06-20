from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None


load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    search_max_results: int
    research_max_rounds: int
    request_timeout_seconds: int


def _read_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        search_max_results=max(1, min(_read_int("SEARCH_MAX_RESULTS", 4), 8)),
        research_max_rounds=max(1, min(_read_int("RESEARCH_MAX_ROUNDS", 2), 4)),
        request_timeout_seconds=max(3, min(_read_int("REQUEST_TIMEOUT_SECONDS", 12), 30)),
    )
