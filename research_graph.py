from __future__ import annotations

from typing import Literal

from agents import analyst_agent, planner_agent, researcher_agent, verifier_agent, writer_agent
from config import get_settings
from state import ResearchState


def supervisor_router(state: ResearchState) -> Literal["researcher", "writer"]:
    verification = state.get("verification", {})
    if verification.get("needs_more_research") and state.get("research_round", 0) < state.get("max_rounds", 2):
        return "researcher"
    return "writer"


def build_research_graph():
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(ResearchState)
    graph.add_node("planner", planner_agent)
    graph.add_node("researcher", researcher_agent)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("verifier", verifier_agent)
    graph.add_node("writer", writer_agent)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "verifier")
    graph.add_conditional_edges("verifier", supervisor_router, {"researcher": "researcher", "writer": "writer"})
    graph.add_edge("writer", END)
    return graph.compile()


def run_research(goal: str, max_rounds: int | None = None) -> ResearchState:
    settings = get_settings()
    initial_state: ResearchState = {
        "goal": goal,
        "plan": [],
        "sources": [],
        "analysis": {},
        "verification": {},
        "errors": [],
        "trace": ["Supervisor received the research goal."],
        "research_round": 0,
        "max_rounds": max_rounds or settings.research_max_rounds,
    }

    try:
        graph = build_research_graph()
        return graph.invoke(initial_state)
    except ImportError as exc:
        fallback_state = planner_agent(initial_state)
        fallback_state = researcher_agent(fallback_state)
        fallback_state = analyst_agent(fallback_state)
        fallback_state = verifier_agent(fallback_state)
        fallback_state = writer_agent(fallback_state)
        fallback_state["errors"] = [*fallback_state.get("errors", []), f"LangGraph import failed: {exc}"]
        fallback_state["trace"] = [*fallback_state.get("trace", []), "Supervisor used sequential fallback because LangGraph is unavailable."]
        return fallback_state
