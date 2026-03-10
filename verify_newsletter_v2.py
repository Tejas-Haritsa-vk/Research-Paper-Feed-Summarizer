
from database import get_papers
from utils.newsletter_v2 import generate_html_newsletter
from agents.ollama_agent import OllamaAgent
from utils.content_generation import generate_tldr, generate_insights

# Initialize
llm = OllamaAgent(model="gemma3:4b", host="http://127.0.0.1:11434", temperature=0.1, seed=41, num_ctx=61440)

def verify():
    # Get unsent papers (the ones we just added)
    papers = get_papers(days=1, exclude_sent=True)
    print(f"Found {len(papers)} unsent papers.")
    
    if not papers:
        print("No papers found to generate newsletter.")
        return
        
    # Generate insights
    print("Generating insights...")
    papers = generate_insights(papers, llm)
    
    # Generate TL;DR
    print("Generating TL;DR...")
    tldr = generate_tldr(papers, llm)
    
    # Generate HTML
    print("Generating HTML...")
    html = generate_html_newsletter(papers, tldr=tldr)
    
    with open("test_newsletter_v2.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Newsletter generated: test_newsletter_v2.html")
    
    # Print a snippet of the first paper to check summary and insight
    p = papers[0]
    print(f"\n--- Paper Verification ---")
    print(f"Title: {p['title']}")
    print(f"Summary (first 200 chars): {p['summary'][:200]}...")
    print(f"Insight: {p['insight']}")

if __name__ == "__main__":
    verify()
