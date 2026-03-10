#main.py
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from clients.arxiv_client import fetch_arxiv_papers
from clients.huggingface_client import fetch_huggingface_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.deepmind_client import fetch_deepmind_papers
from clients.google_ai_blog_client import fetch_google_ai_blog
from clients.meta_fair_client import fetch_meta_fair_papers
from agents.ollama_agent import OllamaAgent  # <-- import your LLM agent
from database import init_db, add_paper, get_papers as db_get_papers, get_stats as db_get_stats
from utils.deduplication import deduplicate_papers, extract_authors, extract_arxiv_id, extract_topics
from utils.newsletter import generate_html_newsletter as generate_html_newsletter_v1, generate_text_newsletter
from utils.newsletter_v2 import generate_html_newsletter as generate_html_newsletter_v2
from typing import List
from utils.content_generation import generate_tldr, generate_insights, enrich_summaries


app = FastAPI(title="Multi-Source Research Paper MCP Server")

# Initialize Ollama
llm = OllamaAgent(model="gemma3:4b", host="http://127.0.0.1:11434", temperature=0.1, seed=41, num_ctx=61440, )

# Initialize ChromaDB on startup
@app.on_event("startup")
async def startup_event():
    """Initialize ChromaDB on application startup."""
    init_db()
    print("ChromaDB initialized successfully")


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/fetch_all_sources")
def fetch_all_sources(query: str = "deep learning", max_results: int = 5, days: int = 7):
    """Fetch new research papers from all supported sources."""
    return {
        "arxiv": fetch_arxiv_papers(query, max_results, days),
        "huggingface": fetch_huggingface_papers(query, max_results, days),
        "openreview": fetch_openreview_papers(query, max_results, days),
        "google_research": fetch_google_research(query, max_results, days),
        "deepmind": fetch_deepmind_papers(query, max_results, days),
        "google_ai_blog": fetch_google_ai_blog(query, max_results, days),
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
def get_num_tokens_endpoint(
    query_context: str
):
    """Get number of tokens in text."""
    num_tokens = llm.get_num_tokens(query_context)
    return num_tokens


@app.post("/fetch_and_store")
def fetch_and_store(
    query: str = Query("deep learning", description="Search query"),
    max_results: int = Query(5, description="Max results per source"),
    days: int = Query(7, description="Days to look back")
):
    """Fetch papers from all sources, deduplicate, and store in ChromaDB."""
    # Fetch from all sources
    all_papers = []
    
    sources = [
        ("arXiv", fetch_arxiv_papers),
        ("HuggingFace", fetch_huggingface_papers),
        ("OpenReview", fetch_openreview_papers),
        ("Google Research", fetch_google_research),
        ("Google DeepMind", fetch_deepmind_papers),
        ("Google AI Blog", fetch_google_ai_blog),
        ("Meta AI Blog", fetch_meta_fair_papers)
    ]
    
    for source_name, fetch_func in sources:
        try:
            papers = fetch_func(query=query, max_results=max_results, days=days)
            for paper in papers:
                paper['source'] = source_name
                # Extract additional metadata
                if 'link' in paper:
                    arxiv_id = extract_arxiv_id(paper['link'])
                    if arxiv_id:
                        paper['arxiv_id'] = arxiv_id
                all_papers.append(paper)
        except Exception as e:
            print(f"Error fetching from {source_name}: {e}")
    
    # Deduplicate papers
    unique_papers = deduplicate_papers(all_papers, threshold=0.85)
    
    # Enrich short summaries (blog posts, etc.)
    unique_papers = enrich_summaries(unique_papers, llm)
    
    # Extract topics and store in database
    stored_count = 0
    for paper in unique_papers:
        try:
            # Extract topics using LLM
            paper['topics'] = extract_topics(paper.get('title', ''), paper.get('summary', ''), llm)
            
            paper_id = add_paper(paper)
            if paper_id:
                stored_count += 1
        except Exception as e:
            print(f"Error storing paper: {e}")
    
    return {
        "fetched": len(all_papers),
        "duplicates_removed": len(all_papers) - len(unique_papers),
        "stored": stored_count,
        "papers": unique_papers
    }


@app.get("/papers")
def get_papers(
    days: int = Query(7, description="Days to look back"),
    source: str = Query(None, description="Filter by source"),
    topics: List[str] = Query(["AI", "Deep Learning"], description="Topics to filter by")
):
    """Retrieve deduplicated papers from ChromaDB."""
    papers = db_get_papers(days=days, source=source, topics=topics)
    return {"count": len(papers), "papers": papers}


@app.get("/newsletter", response_class=HTMLResponse)
def get_newsletter(
    days: int = Query(7, description="Days to look back"),
    format: str = Query("html", description="Format: html or text"),
    exclude_sent: bool = Query(True, description="Exclude papers already sent in newsletters"),
    mark_as_sent: bool = Query(True, description="Mark papers as sent after generating newsletter"),
    topics: List[str] = Query(["AI", "Deep Learning"], description="Topics to filter by"),
    include_tldr: bool = Query(True, description="Include an LLM-generated TL;DR summary"),
    include_insights: bool = Query(True, description="Include per-paper LLM-generated insights")
):
    """Generate newsletter from stored papers."""
    papers = db_get_papers(days=days, exclude_sent=exclude_sent, topics=topics)
    
    if not papers:
        return HTMLResponse(content="<html><body><h1>No new papers to send</h1></body></html>")
    
    # Generate TL;DR if requested
    tldr = None
    if include_tldr:
        tldr = generate_tldr(papers, llm)
    
    # Generate insights if requested
    if include_insights:
        papers = generate_insights(papers, llm)
    
    # Mark papers as sent if requested
    if mark_as_sent and exclude_sent:
        from database import mark_papers_as_sent
        paper_ids = [p['id'] for p in papers]
        marked_count = mark_papers_as_sent(paper_ids)
        print(f"Marked {marked_count} papers as sent in newsletter")
    
    if format == "text":
        newsletter = generate_text_newsletter(papers, tldr=tldr)
        return newsletter
    else:
        print(f"Generating HTML newsletter v2 for {len(papers)} papers...")
        newsletter = generate_html_newsletter_v2(papers, tldr=tldr)
        return HTMLResponse(content=newsletter)


@app.get("/stats")
def get_stats():
    """Get database statistics."""
    stats = db_get_stats()
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
