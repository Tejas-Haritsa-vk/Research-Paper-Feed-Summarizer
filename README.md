# Research Paper Feed Summarizer

A focused, repo-specific toolkit that fetches recent research papers from multiple sources, normalizes the metadata, and exposes simple endpoints to let an LLM/Agent (the repository uses an OllamaAgent wrapper by default) analyze or summarize fetched context. This README keeps the sections you asked for and tailors them to the actual files and behavior in this repository.

## What this does

- Fetches recent research articles from multiple sources (arXiv is implemented; a PapersWithCode fetcher example is present and other clients are scaffolded).
- Normalizes results (title, summary/abstract, link, isoformatted published date) into a consistent structure or Article model.
- Exposes a FastAPI service (main.py) with endpoints that:
  - fetch recent papers from multiple sources,
  - send collected summaries/context to an LLM agent for analysis or summarization,
  - return the agent's responses or token-count information.
- Provides a small demo runner (app.py) and interactive notebooks (Demo.ipynb, Summarize_Paper.ipynb) to try flows locally.

## Key features

- Multi-source fetching:
  - clients/arxiv_client.py — production-ready arXiv Atom fetcher: fetch_arxiv_papers(query='', max_results=50, days=7)
  - paperswithcode.py — example async fetcher that normalizes to an Article model (PapersWithCode API example)
  - base.py — abstract BaseFetcher for adding new sources consistently
- FastAPI server (main.py) with endpoints:
  - GET /fetch_all_sources — aggregate fetch across supported clients
  - POST /analyze_with_llm — fetch context and ask the LLM a question
  - POST /summarize_with_llm — summarize provided context via the LLM wrapper
  - POST /get_num_tokens — agent token counting helper
- Agent integration:
  - agents/ollama_agent (referenced in main.py) is used to talk to an on-prem or local Ollama instance by default.
  - The agent is expected to provide chat(...) and get_num_tokens(...) methods.
- Notebooks for interactive exploration and quick experiments.

## High-level architecture

- main.py — FastAPI application and orchestration of clients + agent
  - Initializes an OllamaAgent with defaults (model="gemma3:4b", host="http://127.0.0.1:11434", temperature=0.1, seed=41, num_ctx=61440).
  - Endpoints call client functions (for example clients/arxiv_client.fetch_arxiv_papers).
- clients/ (or top-level client files) — implement fetchers for specific sources
  - clients/arxiv_client.py — parses Atom XML from export.arxiv.org and returns normalized entries with published in ISO format.
  - paperswithcode.py — async example that normalizes into an Article model (fields: title, summary, link, authors, pdf_url, raw, source, source_id).
- agents/ — LLM wrappers (OllamaAgent is used in the repo). The agent handles prompt construction, chat calls, and token counting.
- app.py — demo runner that starts the FastAPI server in a background thread and exercises the fetch + agent flow.
- Notebooks — Demo.ipynb and Summarize_Paper.ipynb show example interactive usages and experimentation.

## Prerequisites

- Python 3.8+
- Clone the repo:
  git clone https://github.com/Tejas-Haritsa-vk/Research-Paper-Feed-Summarizer.git
  cd Research-Paper-Feed-Summarizer
- Create and activate a virtual environment:
  python -m venv .venv
  source .venv/bin/activate   # macOS / Linux
  .venv\Scripts\activate      # Windows (PowerShell)
- Install dependencies:
  pip install -r requirements.txt

Key packages (requirements.txt)
- fastapi==0.115.0
- uvicorn==0.30.0
- requests==2.31.0
- feedparser==6.0.11

Runtime considerations
- If you use the default OllamaAgent, run your Ollama service locally (or update the agent initialization in main.py to your host).
- Network access is required for external APIs (arXiv, PapersWithCode).
- Optional dependencies may be required by agent implementations (langchain_core, an Ollama client, etc.) — check agents/ for specifics.

## How to run (quick)

1) Start the API server directly
   uvicorn main:app --host 0.0.0.0 --port 8080

2) Or run the small demo launcher (starts a server in a background thread and demonstrates a flow)
   python app.py

Endpoints (examples)
- GET /fetch_all_sources
  - params: query (default "deep learning"), max_results (int), days (int)
  - example: curl "http://127.0.0.1:8080/fetch_all_sources?query=vision&max_results=3&days=7"

- POST /analyze_with_llm
  - example: curl -X POST "http://127.0.0.1:8080/analyze_with_llm" -d "query=Summarize latest methods" -d "context_query=vision"

- POST /summarize_with_llm
  - example: provide `query` and `query_context` (stringified context)

## Repository-specific notes

- arXiv client behavior:
  - clients/arxiv_client.py constructs queries combining user query and an internal base_query filter:
    base_query = "(all:deep+learning OR all:vision OR all:LLM OR all:multimodal) AND (cat:cs.CV OR cat:cs.LG OR cat:cs.CL)"
  - Function signature: fetch_arxiv_papers(query='', max_results=50, days=7) — returns entries with 'title', 'summary', 'link', 'published' (ISO string).
- PapersWithCode example:
  - paperswithcode.py demonstrates an async fetcher that normalizes to an Article Pydantic model and attaches raw metadata to art.raw.
- Agent interface:
  - main.py expects the agent to implement:
    - chat(user_query, context) or chat(query, summaries)
    - get_num_tokens(text)
  - If you don't run Ollama locally, modify main.py to initialize an alternative agent (OpenAI, HF, etc.) that exposes the same methods.

## Extending and customizing

- Add a new source:
  1. Create a client module in clients/ (or app/sources/) that returns normalized dicts or an Article model.
  2. Optionally subclass BaseFetcher in base.py when building an async fetcher.
  3. Add the client call in main.py (include it in the /fetch_all_sources response).
  4. Add caching, deduplication, and rate limiting as needed.

- Replace or add an agent:
  1. Implement a new wrapper in agents/ that exposes chat(...) and get_num_tokens(...).
  2. Update the agent initialization in main.py to use the new wrapper and configuration (API keys, host, model name, temperature).

- Output/export:
  - This repo focuses on fetch + LLM analysis endpoints. Add a persister or exporter if you want outputs saved to JSON/CSV/Markdown/Notion/Obsidian/email.

## Contributing

Thanks for considering contributions! Suggested workflow:
1. Open an issue describing the change or bug you want to address.
2. Fork the repo and create a branch for your change:
   git checkout -b feature/your-feature
3. Make small, focused commits and add tests where relevant.
4. Update requirements.txt if you add new dependencies.
5. Open a pull request with a clear description of what changed and why.

Tips:
- Keep external API calls isolated so tests can mock them easily.
- For new clients, include sample shapes of API responses in tests or fixtures.
- Document any new env vars or runtime requirements in this README.

## License

- There is currently no LICENSE file in the repository. Add an explicit license to clarify reuse terms.
- Suggested starter: create a LICENSE file with the MIT license if you want permissive reuse:
  - Add LICENSE containing the MIT text and then add a short header in this README, e.g.: "License: MIT — see LICENSE file."

## Contact

- Repo owner: Tejas-Haritsa-vk (this repository)
- For feature requests/bugs: open an issue in this repository

## Acknowledgements

- arXiv (export.arxiv.org) — Atom/RSS feed for research papers.
- PapersWithCode — great source for code and normalized metadata (example client included).
- Ollama and any LLM wrappers used in agents/.
- FastAPI, Uvicorn, requests, feedparser and other open-source tools used in this project.
- Langchain components referenced in the demo (JsonOutputParser usage in app.py).
