# Deep Research Multi-Agent System

An agentic AI research system built with **Python**, **LangGraph**, and **LLM APIs**. Instead of sending one large prompt to one model, this project routes a research goal through multiple specialist agents that collaborate, check each other, handle tool failures, and produce a final evidence-backed report.

## Why This Project Matters

Most simple AI demos are single-prompt wrappers. This project demonstrates a more production-oriented pattern: separate agents with clear responsibilities, shared state, conditional routing, retry logic, and a verification loop before final synthesis.

It is designed as a portfolio-ready example of:

- Multi-agent orchestration
- Agentic task delegation
- LangGraph state machines
- LLM API integration
- Tool reliability and error handling
- Research workflow automation

## Features

- **Planner agent** breaks a user goal into focused research questions.
- **Researcher agent** gathers web evidence and records source snippets.
- **Analyst agent** extracts themes, risks, and recommendations.
- **Verifier agent** checks source coverage and can request another research round.
- **Writer agent** synthesizes the final report with citations.
- **Supervisor routing** decides whether to continue researching or finalize.
- **Offline demo mode** works without an API key for testing and walkthroughs.
- **Windows launcher** runs the system without typing terminal commands.

## Architecture

```text
User goal
  -> Planner Agent
  -> Researcher Agent
  -> Analyst Agent
  -> Verifier Agent
       -> Researcher Agent again if evidence is weak
       -> Writer Agent when evidence is approved
  -> Final research report
```

The agents communicate through a shared typed state object defined in `state.py`. The workflow itself is built in `research_graph.py` using LangGraph conditional edges.

## Tech Stack

- Python
- LangGraph
- LangChain Core
- OpenAI-compatible LLM APIs via `langchain-openai`
- Requests and BeautifulSoup for web search extraction
- Pytest for routing and fallback tests

## Project Structure

```text
deep-research-multi-agent/
  agents.py                      Specialist agent implementations
  config.py                      Runtime settings
  research_graph.py              LangGraph workflow and supervisor routing
  run_research.py                CLI entry point
  state.py                       Typed shared graph state
  tools.py                       Web search, retries, source normalization
  requirements.txt               Python dependencies
  RUN-MULTI-AGENT-SYSTEM.bat     Double-click Windows launcher
  RUN-MULTI-AGENT-SYSTEM.cmd     Launcher implementation
  tests/                         Routing, retry, and fallback tests
```

## Quick Start

On Windows, double-click:

```text
RUN-MULTI-AGENT-SYSTEM.bat
```

The launcher creates a local virtual environment, installs dependencies, and runs the multi-agent system.

Important: use **64-bit Python**. The 32-bit Windows installer can fail when installing LangGraph/OpenAI dependencies such as `tiktoken` and `ormsgpack`.

Manual setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run_research.py "Research the benefits and risks of AI agents in cybersecurity operations"
```

## LLM Configuration

Add an OpenAI API key to `.env`:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Without an API key, the system runs in offline demo mode with deterministic local logic so the workflow can still be demonstrated.

## Example Output

```text
# Research Report: Research multi-agent AI systems

## Executive Summary
The multi-agent workflow completed planning, research, analysis, verification, and synthesis.

## Key Findings
- Use specialist agents for planning, evidence gathering, critique, and synthesis.
- Keep every handoff visible so failures can be diagnosed.
- Use verification loops before producing final recommendations.

Agent trace:
- Supervisor received the research goal.
- Planner created research questions.
- Researcher gathered source snippets.
- Analyst extracted themes, risks, and recommendations.
- Verifier approved the evidence.
- Writer synthesized the final report.
```

## Testing

```powershell
pytest tests
```

The tests cover supervisor routing, retry behavior, and offline workflow generation.

## LinkedIn

I wrote a ready-to-post LinkedIn project summary in [`LINKEDIN_POST.md`](LINKEDIN_POST.md).

Repo URL: https://github.com/risingsummit/deep-research-multi-agent

## Landing Page

The GitHub Pages landing page lives in [`docs/`](docs/). In GitHub repository settings, publish Pages from the `main` branch and `/docs` folder.

## Portfolio Summary

This project shows that I can build beyond basic AI prompts: I can design agent workflows, model state, route tasks, add verification loops, handle failures, and package the result into a runnable Python system.
