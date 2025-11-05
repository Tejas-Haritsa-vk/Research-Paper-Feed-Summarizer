#main.py
from fastapi import FastAPI, Query
from clients.arxiv_client import fetch_arxiv_papers
from clients.paperswithcode_client import fetch_pwc_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.meta_fair_client import fetch_meta_fair_papers
from agents.ollama_agent import OllamaAgent  # <-- import your LLM agent


app = FastAPI(title="Multi-Source Research Paper MCP Server")

# Initialize Ollama
llm = OllamaAgent(model="gemma3:4b", host="http://127.0.0.1:11434", temperature=0.1, seed=41, num_ctx=61440, )


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/fetch_all_sources")
def fetch_all_sources(query: str = "deep learning", max_results: int = 5, days: int = 7):
    """Fetch new research papers from all supported sources."""
    return {
        "arxiv": fetch_arxiv_papers(query, max_results, days),
        # "paperswithcode": fetch_pwc_papers(query, max_results, days),
        "openreview": fetch_openreview_papers(query, max_results, days),
        "google_research": fetch_google_research(query, max_results, days),
        "meta_fair": fetch_meta_fair_papers(query, max_results, days),
    }

@app.post("/analyze_with_llm")
def analyze_with_llm(
    query: str = Query(..., description="Your question for the LLM"),
    context_query: str = Query("deep learning", description="Topic for context fetching"),
):
    """Fetch recent papers and have the LLM analyze them."""
    papers = fetch_arxiv_papers(context_query, max_results=3, days=7)
    summaries = [p["summary"] for p in papers if "summary" in p]

    llm_response = llm.chat(query, summaries)
    return {"query": query, "context_used": len(summaries), "llm_response": llm_response}

@app.post("/summarize_with_llm")
def process_with_llm(
    query: str,
    query_context: str,
):
    """Process the fetched papers with LLM."""
    llm_response = llm.chat(user_query=query, context=query_context)
    return {"query": query, "length_of_context_used": len(query_context), "llm_response": llm_response}

@app.post("/get_num_tokens")
def process_with_llm(
    query_context: str
):
    """Process the fetched papers with LLM."""
    num_tokens = llm.get_num_tokens(query_context)
    return num_tokens


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
