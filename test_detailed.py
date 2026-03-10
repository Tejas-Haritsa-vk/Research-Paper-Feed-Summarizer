#!/usr/bin/env python
"""Detailed test script to verify all clients with different configurations."""
# -*- coding: utf-8 -*-

import json
import sys
from clients.arxiv_client import fetch_arxiv_papers
from clients.paperswithcode_client import fetch_pwc_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.meta_fair_client import fetch_meta_fair_papers


def test_client_detailed(name, fetch_func, query='', max_results=10, days=90):
    """Test a single client and display detailed results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Query: '{query}' | Max: {max_results} | Days: {days}")
    print(f"{'='*60}")
    
    try:
        results = fetch_func(query=query, max_results=max_results, days=days)
        
        if results:
            print(f"[SUCCESS] Found {len(results)} papers/posts")
            print(f"\nShowing first 3 results:")
            for i, paper in enumerate(results[:3], 1):
                print(f"\n--- Item {i} ---")
                title = paper.get('title', 'N/A')
                print(f"Title: {title[:120]}{'...' if len(title) > 120 else ''}")
                print(f"Published: {paper.get('published', 'N/A')}")
                print(f"Link: {paper.get('link', 'N/A')}")
                if paper.get('summary'):
                    summary = paper['summary'][:200].replace('\n', ' ')
                    print(f"Summary: {summary}{'...' if len(paper['summary']) > 200 else ''}")
        else:
            print(f"[WARNING] No results found")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Research Paper Agent - Detailed Client Testing")
    print("Testing with 90-day range and broader queries")
    print("="*60)
    
    # Test arXiv with deep learning query
    test_client_detailed("arXiv (deep learning)", fetch_arxiv_papers, 
                        query='deep learning', max_results=5, days=90)
    
    # Test PapersWithCode
    test_client_detailed("PapersWithCode (machine learning)", fetch_pwc_papers, 
                        query='machine learning', max_results=5, days=90)
    
    # Test OpenReview
    test_client_detailed("OpenReview (transformer)", fetch_openreview_papers, 
                        query='transformer', max_results=5, days=90)
    
    # Test Google Research with NO query (get latest posts)
    test_client_detailed("Google Research Blog (all posts)", fetch_google_research, 
                        query='', max_results=10, days=90)
    
    # Test Meta FAIR with NO query (get latest posts)
    test_client_detailed("Meta FAIR Blog (all posts)", fetch_meta_fair_papers, 
                        query='', max_results=10, days=90)
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
