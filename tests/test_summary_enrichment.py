
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.content_generation import enrich_summaries

class MockLLM:
    def chat(self, user_query: str, context: str) -> str:
        return "This is a detailed and professional summary of the paper that addresses the core problem and innovations."

@patch('utils.content_generation.scrape_article_content')
def test_enrich_summaries(mock_scrape):
    llm = MockLLM()
    papers = [
        {
            "title": "Short Summary Paper",
            "summary": "This is a very short summary.",
            "link": "https://deepmind.google/blog/new-paper"
        },
        {
            "title": "Long Summary Paper",
            "summary": "This is a much longer summary that exceeds the minimum length threshold. " * 20,
            "link": "https://arxiv.org/abs/1234.5678"
        }
    ]
    
    # Mock the scraper to return meaningful content
    mock_scrape.return_value = "This is the full text of the article found at the link. It contains lot of technical details."
    
    print("Testing summary enrichment...")
    enriched_papers = enrich_summaries(papers, llm, min_length=100)
    
    # Check that the short one was enriched
    assert "detailed and professional" in enriched_papers[0]['summary']
    assert len(enriched_papers[0]['summary']) > len("This is a very short summary.")
    
    # Check that the long one was untouched
    assert enriched_papers[1]['summary'].startswith("This is a much longer summary")
    
    print("Verification successful!")

if __name__ == "__main__":
    test_enrich_summaries()
