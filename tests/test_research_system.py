from __future__ import annotations

from research_graph import run_research, supervisor_router
from state import ResearchState
from tools import ToolOutcome, search_with_retries


def test_supervisor_routes_to_researcher_when_verifier_requests_more() -> None:
    state: ResearchState = {
        "goal": "test",
        "verification": {"needs_more_research": True},
        "research_round": 1,
        "max_rounds": 2,
    }
    assert supervisor_router(state) == "researcher"


def test_supervisor_routes_to_writer_when_round_limit_reached() -> None:
    state: ResearchState = {
        "goal": "test",
        "verification": {"needs_more_research": True},
        "research_round": 2,
        "max_rounds": 2,
    }
    assert supervisor_router(state) == "writer"


def test_search_retries_return_last_error() -> None:
    def always_fail(query: str, max_results: int | None = None) -> ToolOutcome:
        return ToolOutcome(False, [], f"failed: {query}")

    outcome = search_with_retries("agent systems", attempts=2, search_fn=always_fail)
    assert not outcome.ok
    assert outcome.error == "failed: agent systems"


def test_offline_workflow_generates_report(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = run_research("multi-agent research systems", max_rounds=1)
    assert "Research Report" in result["report"]
    assert len(result["sources"]) >= 3
    assert result["verification"]["approved"] is True
