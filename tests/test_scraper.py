
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.scraper import scrape_article_content

def test_multi_source_scraper():
    urls = [
        "https://arxiv.org/abs/2312.00752",
        "https://huggingface.co/papers/2512.21218",
        "https://research.google/blog/google-research-2025-bolder-breakthroughs-bigger-impact/",
        "https://deepmind.google/blog/gemma-scope-2-helping-the-ai-safety-community-deepen-understanding-of-complex-language-model-behavior/"
    ]
    
    for url in urls:
        print(f"\n{'='*20}")
        print(f"Testing URL: {url}")
        print(f"{'='*20}")
        content = scrape_article_content(url)
        if content and len(content) > 100:
            print(f"SUCCESS: Content length: {len(content)}")
            print(f"Snippet: {content[:300]}...")
        else:
            print(f"FAILED: Content length: {len(content) if content else 0}")
            if content:
                print(f"Received short/wrong content: {content}")

if __name__ == "__main__":
    test_multi_source_scraper()
