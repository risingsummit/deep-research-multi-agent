# LinkedIn Post

I built a Python multi-agent research system using LangGraph and LLM APIs.

Instead of sending one large prompt to one model, this project routes a research goal through multiple specialized agents:

- Planner agent: breaks the goal into research questions
- Researcher agent: gathers source snippets from the web
- Analyst agent: extracts themes, risks, and recommendations
- Verifier agent: checks whether the evidence is strong enough
- Writer agent: synthesizes the final report

The system also includes supervisor routing, retry logic, error handling, typed shared state, offline demo mode, and a Windows launcher so it can be run without a complicated setup.

This was a good exercise in building agentic logic rather than just wrapping a chatbot prompt. The most interesting part was the verifier loop: if evidence is weak, the graph routes the task back to the researcher before allowing the writer to produce the final answer.

Tech stack:
Python, LangGraph, LangChain, OpenAI-compatible LLM APIs, Requests, BeautifulSoup, Pytest

GitHub repo:
PASTE_YOUR_GITHUB_REPO_LINK_HERE

#Python #AI #LangGraph #AIAgents #LLM #MachineLearning #AgenticAI #OpenAI #SoftwareEngineering

## Short Version

Built a Python multi-agent research system with LangGraph and LLM APIs.

It uses planner, researcher, analyst, verifier, and writer agents to collaborate on a research goal, with supervisor routing, retries, error handling, and offline demo mode.

GitHub repo:
PASTE_YOUR_GITHUB_REPO_LINK_HERE

#Python #AI #LangGraph #AIAgents #LLM #AgenticAI

## LinkedIn Share Link

After the repo is public, replace `YOUR_GITHUB_REPO_URL` below:

```text
https://www.linkedin.com/sharing/share-offsite/?url=YOUR_GITHUB_REPO_URL
```
