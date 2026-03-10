#!/usr/bin/env python
"""Test script to verify all clients are working and returning relevant data."""
# -*- coding: utf-8 -*-

import json
import sys
from clients.arxiv_client import fetch_arxiv_papers
from clients.paperswithcode_client import fetch_pwc_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.meta_fair_client import fetch_meta_fair_papers


def test_client(name, fetch_func, query='deep learning', max_results=3, days=90):
    """Test a single client and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        results = fetch_func(query=query, max_results=max_results, days=days)
        
        if results:
            print(f"[SUCCESS] Found {len(results)} papers")
            print(f"\nSample results:")
            for i, paper in enumerate(results[:2], 1):  # Show first 2 papers
                print(f"\n--- Paper {i} ---")
                print(f"Title: {paper.get('title', 'N/A')[:100]}...")
                print(f"Published: {paper.get('published', 'N/A')}")
                print(f"Link: {paper.get('link', 'N/A')}")
                if paper.get('summary'):
                    summary = paper['summary'][:150].replace('\n', ' ')
                    print(f"Summary: {summary}...")
        else:
            print(f"[WARNING] No results found (this might be normal for recent papers)")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Research Paper Agent - Client Testing (90 days)")
    print("="*60)
    
    # Test each client
    test_client("arXiv", fetch_arxiv_papers)
    test_client("PapersWithCode", fetch_pwc_papers)
    test_client("OpenReview", fetch_openreview_papers)
    test_client("Google Research", fetch_google_research, query='')
    test_client("Meta FAIR", fetch_meta_fair_papers, query='')
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

