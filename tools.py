from __future__ import annotations

import html
import time
from dataclasses import dataclass
from typing import Callable
from urllib.parse import quote_plus

from config import get_settings
from state import Source


USER_AGENT = "Deep-Research-Multi-Agent/1.0"


@dataclass(frozen=True)
class ToolOutcome:
    ok: bool
    sources: list[Source]
    error: str | None = None


def clean_text(value: str, limit: int = 500) -> str:
    compact = " ".join(html.unescape(value).split())
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def search_web(query: str, max_results: int | None = None) -> ToolOutcome:
    settings = get_settings()
    result_limit = max_results or settings.search_max_results

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return ToolOutcome(False, [], "Missing requests or beautifulsoup4. Run pip install -r requirements.txt.")

    if not query.strip():
        return ToolOutcome(False, [], "Search query was empty.")

    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return ToolOutcome(False, [], f"Search failed for '{query}': {exc}")

    soup = BeautifulSoup(response.text, "html.parser")
    sources: list[Source] = []
    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        snippet = item.select_one(".result__snippet")
        if not link:
            continue
        sources.append(
            {
                "title": clean_text(link.get_text(" ", strip=True), 180),
                "url": link.get("href", ""),
                "snippet": clean_text(snippet.get_text(" ", strip=True), 420) if snippet else "",
                "query": query,
            }
        )
        if len(sources) >= result_limit:
            break

    if not sources:
        return ToolOutcome(False, [], f"No sources found for '{query}'.")
    return ToolOutcome(True, sources)


def search_with_retries(
    query: str,
    max_results: int | None = None,
    attempts: int = 2,
    search_fn: Callable[[str, int | None], ToolOutcome] = search_web,
) -> ToolOutcome:
    last_error = None
    for attempt in range(1, max(1, attempts) + 1):
        outcome = search_fn(query, max_results)
        if outcome.ok:
            return outcome
        last_error = outcome.error
        if attempt < attempts:
            time.sleep(0.4 * attempt)
    return ToolOutcome(False, [], last_error or "Search failed.")


def offline_sources(goal: str) -> list[Source]:
    topics = [
        "agent orchestration",
        "evaluation and guardrails",
        "human oversight",
        "tool reliability",
    ]
    return [
        {
            "title": f"Offline demo note: {topic.title()}",
            "url": f"offline://demo/{index}",
            "snippet": (
                f"For '{goal}', teams should assess {topic}, define measurable success criteria, "
                "and keep a trace of agent decisions for review."
            ),
            "query": topic,
        }
        for index, topic in enumerate(topics, start=1)
    ]
