
import sys
import os
from typing import List, Dict

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.content_generation import generate_insights

import json

class MockLLM:
    def chat(self, user_query: str, context: str) -> str:
        # Simple mock that returns JSON with prefixes to test cleaning
        num_papers = context.count("Paper ")
        insights = [f"Paper {i+1}: This is a cleaned insight for paper {i+1}." for i in range(num_papers)]
        json_str = json.dumps({"insights": insights})
        return f'```json\n{json_str}\n```'

def test_generate_insights():
    llm = MockLLM()
    papers = [
        {"title": f"Paper {i}", "summary": f"Summary for paper {i}"}
        for i in range(12)
    ]
    
    print(f"Testing insight generation for {len(papers)} papers with batch_size=5...")
    updated_papers = generate_insights(papers, llm, batch_size=5)
    
    assert len(updated_papers) == 12
    for i, paper in enumerate(updated_papers):
        assert "insight" in paper
        print(f"Paper {i}: {paper['insight']}")
    
    print("Verification successful!")

if __name__ == "__main__":
    test_generate_insights()
