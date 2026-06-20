from __future__ import annotations

import json
import re
from typing import Any

from config import get_settings
from state import ResearchState, Source
from tools import offline_sources, search_with_retries


def _trace(state: ResearchState, message: str) -> list[str]:
    return [*state.get("trace", []), message]


def _unique_sources(sources: list[Source]) -> list[Source]:
    seen: set[str] = set()
    unique: list[Source] = []
    for source in sources:
        key = source.get("url") or f"{source.get('title')}:{source.get('snippet')}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(source)
    return unique


def _llm_json(system: str, prompt: str, fallback: Any) -> Any:
    settings = get_settings()
    if not settings.openai_api_key:
        return fallback

    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return fallback

    try:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0)
        response = llm.invoke(
            [
                ("system", f"{system}\nReturn valid JSON only."),
                ("human", prompt),
            ]
        )
        content = str(response.content)
        match = re.search(r"```(?:json)?\s*(.*?)```", content, flags=re.S)
        if match:
            content = match.group(1)
        return json.loads(content)
    except Exception:
        return fallback


def _llm_text(system: str, prompt: str, fallback: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return fallback

    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return fallback

    try:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0.2)
        response = llm.invoke([("system", system), ("human", prompt)])
        return str(response.content).strip() or fallback
    except Exception:
        return fallback


def planner_agent(state: ResearchState) -> ResearchState:
    goal = state["goal"]
    fallback = [
        f"What are the most important facts and trends related to {goal}?",
        f"What risks, limitations, or tradeoffs matter for {goal}?",
        f"What practical recommendations follow from recent evidence about {goal}?",
    ]
    plan = _llm_json(
        "You are a research planning agent. Break goals into concise web research questions.",
        f"Goal: {goal}\nCreate 3 to 5 search questions as a JSON array of strings.",
        fallback,
    )
    if not isinstance(plan, list) or not all(isinstance(item, str) for item in plan):
        plan = fallback

    return {
        **state,
        "plan": plan[:5],
        "research_round": state.get("research_round", 0),
        "max_rounds": state.get("max_rounds", get_settings().research_max_rounds),
        "trace": _trace(state, f"Planner created {len(plan[:5])} research questions."),
    }


def researcher_agent(state: ResearchState) -> ResearchState:
    settings = get_settings()
    round_number = state.get("research_round", 0) + 1
    plan = state.get("plan", [])
    existing_sources = state.get("sources", [])
    errors = list(state.get("errors", []))
    gathered: list[Source] = []

    if not settings.openai_api_key:
        gathered = offline_sources(state["goal"])
        return {
            **state,
            "sources": _unique_sources([*existing_sources, *gathered]),
            "research_round": round_number,
            "trace": _trace(state, "Researcher used offline demo evidence because no API key is configured."),
        }

    queries = plan[:3] or [state["goal"]]
    if state.get("verification", {}).get("missing"):
        queries = [f"{state['goal']} {gap}" for gap in state["verification"]["missing"][:2]]

    for query in queries:
        outcome = search_with_retries(query, settings.search_max_results)
        if outcome.ok:
            gathered.extend(outcome.sources)
        else:
            errors.append(outcome.error or f"Unknown search error for {query}.")

    return {
        **state,
        "sources": _unique_sources([*existing_sources, *gathered]),
        "errors": errors,
        "research_round": round_number,
        "trace": _trace(state, f"Researcher completed round {round_number} and gathered {len(gathered)} source snippets."),
    }


def analyst_agent(state: ResearchState) -> ResearchState:
    source_text = "\n".join(
        f"- {source['title']}: {source['snippet']} ({source['url']})"
        for source in state.get("sources", [])
    )
    fallback = {
        "themes": [
            "Use specialist agents for planning, evidence gathering, critique, and synthesis.",
            "Keep every handoff visible so failures can be diagnosed.",
            "Use verification loops before producing final recommendations.",
        ],
        "risks": [
            "Weak sources can create overconfident conclusions.",
            "Tool failures need graceful fallback paths.",
            "LLM outputs require structure checks before downstream use.",
        ],
        "recommendations": [
            "Use typed state for shared context.",
            "Cap research retries to prevent runaway loops.",
            "Show trace events in the UI for explainability.",
        ],
    }
    analysis = _llm_json(
        "You are an analysis agent. Extract evidence-backed themes, risks, and recommendations.",
        f"Research goal: {state['goal']}\nSources:\n{source_text}\nReturn JSON with keys themes, risks, recommendations.",
        fallback,
    )
    if not isinstance(analysis, dict):
        analysis = fallback

    return {
        **state,
        "analysis": analysis,
        "trace": _trace(state, "Analyst extracted themes, risks, and recommendations."),
    }


def verifier_agent(state: ResearchState) -> ResearchState:
    sources = state.get("sources", [])
    errors = state.get("errors", [])
    source_count = len(sources)
    enough_sources = source_count >= 3
    needs_more = not enough_sources and state.get("research_round", 0) < state.get("max_rounds", 2)
    missing = []
    if not enough_sources:
        missing.append("additional independent sources")
    if errors:
        missing.append("replacement sources for failed searches")

    verification = {
        "approved": not needs_more,
        "source_count": source_count,
        "needs_more_research": needs_more,
        "missing": missing,
        "errors_seen": errors[-3:],
    }
    return {
        **state,
        "verification": verification,
        "trace": _trace(
            state,
            "Verifier approved the evidence." if verification["approved"] else "Verifier requested another research round.",
        ),
    }


def writer_agent(state: ResearchState) -> ResearchState:
    citations = "\n".join(
        f"[{index}] {source['title']} - {source['url']}"
        for index, source in enumerate(state.get("sources", []), start=1)
    )
    fallback = _offline_report(state)
    report = _llm_text(
        "You are a synthesis agent. Write concise research reports with citations and practical next steps.",
        (
            f"Goal: {state['goal']}\n\n"
            f"Analysis JSON:\n{json.dumps(state.get('analysis', {}), indent=2)}\n\n"
            f"Verification JSON:\n{json.dumps(state.get('verification', {}), indent=2)}\n\n"
            f"Citations:\n{citations}\n\n"
            "Write a report with: Executive Summary, Key Findings, Risks, Recommendations, Sources."
        ),
        fallback,
    )
    return {
        **state,
        "report": report,
        "trace": _trace(state, "Writer synthesized the final report."),
    }


def _offline_report(state: ResearchState) -> str:
    analysis = state.get("analysis", {})
    sources = state.get("sources", [])

    def lines(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- No items found."

    source_lines = "\n".join(
        f"- [{index}] {source['title']} - {source['url']}"
        for index, source in enumerate(sources, start=1)
    )
    return (
        f"# Research Report: {state['goal']}\n\n"
        "## Executive Summary\n"
        "The multi-agent workflow completed planning, research, analysis, verification, and synthesis. "
        "This run used deterministic demo logic unless an OpenAI API key was configured.\n\n"
        "## Key Findings\n"
        f"{lines(list(analysis.get('themes', [])))}\n\n"
        "## Risks\n"
        f"{lines(list(analysis.get('risks', [])))}\n\n"
        "## Recommendations\n"
        f"{lines(list(analysis.get('recommendations', [])))}\n\n"
        "## Sources\n"
        f"{source_lines or '- No sources collected.'}\n"
    )
