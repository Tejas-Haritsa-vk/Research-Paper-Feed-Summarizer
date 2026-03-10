
import json
from clients.arxiv_client import fetch_arxiv_papers
from clients.huggingface_client import fetch_huggingface_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.deepmind_client import fetch_deepmind_papers
from clients.google_ai_blog_client import fetch_google_ai_blog
from clients.meta_fair_client import fetch_meta_fair_papers
from agents.ollama_agent import OllamaAgent
from database import init_db, add_paper
from utils.deduplication import deduplicate_papers, extract_arxiv_id, extract_topics
from utils.content_generation import enrich_summaries

# Initialize
llm = OllamaAgent(model="gemma3:4b", host="http://127.0.0.1:11434", temperature=0.1, seed=41, num_ctx=61440)
init_db()

def run_full_sweep(query="deep learning", max_results=3, days=7):
    print(f"Starting sweep for '{query}'...")
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
            print(f"Fetching from {source_name}...")
            papers = fetch_func(query=query, max_results=max_results, days=days)
            for paper in papers:
                paper['source'] = source_name
                if 'link' in paper:
                    arxiv_id = extract_arxiv_id(paper['link'])
                    if arxiv_id:
                        paper['arxiv_id'] = arxiv_id
                all_papers.append(paper)
        except Exception as e:
            print(f"Error fetching from {source_name}: {e}")
            
    print(f"Total papers fetched: {len(all_papers)}")
    
    # Deduplicate
    unique_papers = deduplicate_papers(all_papers, threshold=0.85)
    print(f"Unique papers after deduplication: {len(unique_papers)}")
    
    # Enrich
    print("Enriching short summaries...")
    unique_papers = enrich_summaries(unique_papers, llm)
    
    # Store
    stored_count = 0
    for paper in unique_papers:
        try:
            paper['topics'] = extract_topics(paper.get('title', ''), paper.get('summary', ''), llm)
            paper_id = add_paper(paper)
            if paper_id:
                stored_count += 1
                print(f"Stored: {paper.get('title')}")
        except Exception as e:
            print(f"Error storing paper: {e}")
            
    print(f"Sweep complete. Stored {stored_count} new papers.")

if __name__ == "__main__":
    run_full_sweep()
