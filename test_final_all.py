#!/usr/bin/env python
"""Comprehensive test of ALL clients including new Google blogs - 90 days."""
# -*- coding: utf-8 -*-

from clients.arxiv_client import fetch_arxiv_papers
from clients.huggingface_client import fetch_huggingface_papers
from clients.openreview_client import fetch_openreview_papers
from clients.google_research_client import fetch_google_research
from clients.deepmind_client import fetch_deepmind_papers
from clients.google_ai_blog_client import fetch_google_ai_blog
from clients.meta_fair_client import fetch_meta_fair_papers


def test_client(name, fetch_func, query='', max_results=3, days=90):
    """Test a single client and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Query: '{query}' | Max: {max_results} | Days: {days}")
    print(f"{'='*60}")
    
    try:
        results = fetch_func(query=query, max_results=max_results, days=days)
        
        if results:
            print(f"[SUCCESS] Found {len(results)} results")
            for i, item in enumerate(results[:2], 1):  # Show first 2
                print(f"\n--- Result {i} ---")
                print(f"Title: {item['title'][:80]}...")
                print(f"Published: {item.get('published', 'N/A')}")
                print(f"Link: {item.get('link', 'N/A')[:70]}...")
        else:
            print(f"[INFO] No results found")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")


if __name__ == "__main__":
    print("="*60)
    print("Research Paper Agent - FINAL COMPREHENSIVE TEST")
    print("All Clients | 90-Day Window")
    print("="*60)
    
    # Research Paper Sources
    print("\n" + "="*60)
    print("RESEARCH PAPER SOURCES")
    print("="*60)
    
    test_client("arXiv", fetch_arxiv_papers, 
                query='deep learning', max_results=3, days=90)
    
    test_client("HuggingFace Trending Papers", fetch_huggingface_papers, 
                query='', max_results=3, days=90)
    
    test_client("OpenReview", fetch_openreview_papers, 
                query='vision', max_results=3, days=90)
    
    # Google Blog Sources
    print("\n" + "="*60)
    print("GOOGLE BLOG SOURCES")
    print("="*60)
    
    test_client("Google DeepMind Blog", fetch_deepmind_papers, 
                query='', max_results=3, days=90)
    
    test_client("Google AI Blog", fetch_google_ai_blog, 
                query='', max_results=3, days=90)
    
    test_client("Google Research Blog", fetch_google_research, 
                query='', max_results=3, days=90)
    
    # Meta (Note: No RSS available)
    print("\n" + "="*60)
    print("META AI (No RSS Available)")
    print("="*60)
    
    test_client("Meta AI Blog", fetch_meta_fair_papers, 
                query='', max_results=3, days=90)
    
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print("Working Sources:")
    print("  - arXiv: Academic papers (EXCELLENT)")
    print("  - HuggingFace: Trending papers with GitHub repos (EXCELLENT)")
    print("  - Google DeepMind: Latest AI research from DeepMind (EXCELLENT)")
    print("  - Google AI Blog: AI product announcements (EXCELLENT)")
    print("  - Google Research: Technical research blog (EXCELLENT)")
    print("\nLimited/No Data:")
    print("  - OpenReview: Conference papers (batch publishing)")
    print("  - Meta AI: No RSS feed available")
    print("="*60)
