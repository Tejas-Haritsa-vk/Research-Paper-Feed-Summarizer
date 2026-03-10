#!/usr/bin/env python
"""Test the new Google blog clients with 90-day window."""
# -*- coding: utf-8 -*-

from clients.deepmind_client import fetch_deepmind_papers
from clients.google_ai_blog_client import fetch_google_ai_blog
from clients.google_research_client import fetch_google_research

def test_client(name, fetch_func, query='', max_results=5, days=90):
    """Test a single client and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Query: '{query}' | Max Results: {max_results} | Days: {days}")
    print(f"{'='*60}")
    
    try:
        results = fetch_func(query=query, max_results=max_results, days=days)
        
        if results:
            print(f"[SUCCESS] Found {len(results)} results")
            print(f"\nShowing all results:")
            for i, post in enumerate(results, 1):
                print(f"\n--- Post {i} ---")
                print(f"Title: {post['title'][:100]}...")
                print(f"Published: {post.get('published', 'N/A')}")
                print(f"Link: {post.get('link', 'N/A')[:80]}...")
                if post.get('summary'):
                    summary = post['summary'][:150].replace('\n', ' ')
                    print(f"Summary: {summary}...")
        else:
            print(f"[INFO] No results found")
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Testing New Google Blog Clients (90 days)")
    print("="*60)
    
    # Test each Google client with empty query to get all recent posts
    test_client("Google DeepMind Blog", fetch_deepmind_papers, 
                query='', max_results=5, days=90)
    
    test_client("Google AI Blog", fetch_google_ai_blog, 
                query='', max_results=5, days=90)
    
    test_client("Google Research Blog", fetch_google_research, 
                query='', max_results=5, days=90)
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
