from __future__ import annotations

from typing import Any, Literal, TypedDict


class Source(TypedDict):
    title: str
    url: str
    snippet: str
    query: str


class ResearchState(TypedDict, total=False):
    goal: str
    plan: list[str]
    current_query: str
    sources: list[Source]
    analysis: dict[str, Any]
    verification: dict[str, Any]
    report: str
    errors: list[str]
    trace: list[str]
    research_round: int
    max_rounds: int
    next_agent: Literal["planner", "researcher", "analyst", "verifier", "writer", "end"]
