#!/usr/bin/env python
"""Comprehensive test of all clients with 90-day window."""
# -*- coding: utf-8 -*-

from clients.arxiv_client import fetch_arxiv_papers
from clients.huggingface_client import fetch_huggingface_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.meta_fair_client import fetch_meta_fair_papers


def test_client(name, fetch_func, query='deep learning', max_results=5, days=90):
    """Test a single client and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Query: '{query}' | Max Results: {max_results} | Days: {days}")
    print(f"{'='*60}")
    
    try:
        results = fetch_func(query=query, max_results=max_results, days=days)
        
        if results:
            print(f"[SUCCESS] Found {len(results)} results")
            print(f"\nShowing first 3 results:")
            for i, paper in enumerate(results[:3], 1):
                print(f"\n--- Result {i} ---")
                title = paper.get('title', 'N/A')
                print(f"Title: {title[:100]}{'...' if len(title) > 100 else ''}")
                print(f"Published: {paper.get('published', 'N/A')}")
                print(f"Link: {paper.get('link', 'N/A')[:80]}...")
                
                # Show special features if available
                if paper.get('upvotes'):
                    print(f"Upvotes: {paper.get('upvotes')}")
                if paper.get('github'):
                    print(f"GitHub: {paper.get('github')[:60]}...")
                
                if paper.get('summary'):
                    summary = paper['summary'][:150].replace('\n', ' ')
                    print(f"Summary: {summary}...")
        else:
            print(f"[INFO] No results found")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Research Paper Agent - Comprehensive Client Test")
    print("Testing all clients with 90-day lookback window")
    print("="*60)
    
    # Test each client
    test_client("arXiv", fetch_arxiv_papers, 
                query='deep learning', max_results=5, days=90)
    
    test_client("HuggingFace Daily Papers", fetch_huggingface_papers, 
                query='', max_results=5, days=90)
    
    test_client("OpenReview", fetch_openreview_papers, 
                query='vision', max_results=5, days=90)
    
    test_client("Google Research Blog", fetch_google_research, 
                query='', max_results=10, days=90)
    
    test_client("Meta FAIR Blog", fetch_meta_fair_papers, 
                query='', max_results=10, days=90)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("Working clients: arXiv, HuggingFace")
    print("Blog feeds: May have limited recent posts")
    print("="*60)
