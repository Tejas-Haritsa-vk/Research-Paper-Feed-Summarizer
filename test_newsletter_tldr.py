from utils.newsletter import generate_html_newsletter, generate_text_newsletter
import os

def test_tldr_manual():
    print("--- Testing Newsletter TL;DR Section ---")
    
    mock_papers = [
        {
            "title": "Uncovering the Truth about Large Language Models",
            "summary": "This paper investigates the inherent biases and logical fallacies often present in modern LLMs.",
            "source": "arXiv",
            "published": "2025-12-20",
            "topics": ["LLM", "Bias", "AI Ethics"]
        },
        {
            "title": "Gemma 3: The Next Generation of Open Models",
            "summary": "Google Research introduces Gemma 3, a highly efficient and capable family of open-weights models.",
            "source": "Google Research",
            "published": "2025-12-21",
            "topics": ["Gemma", "Open Models", "Deep Learning"]
        }
    ]
    
    mock_tldr = "This newsletter explores the latest developments in Large Language Models (LLMs), specifically focusing on the detection of biases and the release of new open-weights models like Google's Gemma 3. These papers highlight a shift towards both more ethical auditing of AI and increased accessibility of high-performance models."
    
    # Test HTML
    print("Generating HTML newsletter with TL;DR...")
    html = generate_html_newsletter(mock_papers, tldr=mock_tldr)
    
    with open("test_newsletter_tldr.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML saved to test_newsletter_tldr.html (Size: {len(html)} bytes)")
    
    # Check for TL;DR markers in HTML
    if "TL;DR (1-2 min read)" in html and mock_tldr in html:
        print("[OK] TL;DR found in HTML output")
    else:
        print("[FAIL] TL;DR missing in HTML output")
        
    # Test Text
    print("\nGenerating Text newsletter with TL;DR...")
    text = generate_text_newsletter(mock_papers, tldr=mock_tldr)
    print("Text Output Preview:")
    print("-" * 30)
    print(text[:300] + "...")
    print("-" * 30)
    
    if "TL;DR (1-2 min read):" in text and mock_tldr in text:
        print("[OK] TL;DR found in Text output")
    else:
        print("[FAIL] TL;DR missing in Text output")

if __name__ == "__main__":
    test_tldr_manual()
