#!/usr/bin/env python
"""Test the Meta AI Blog web scraper."""
# -*- coding: utf-8 -*-

from clients.meta_fair_client import fetch_meta_fair_papers

print("="*60)
print("Testing Meta AI Blog Web Scraper (90 days)")
print("="*60)

# Test without query to get all recent posts
print("\n[TEST] Fetching recent Meta AI blog posts (90 days)")
posts = fetch_meta_fair_papers(query='', max_results=5, days=90)

if posts:
    print(f"[SUCCESS] Found {len(posts)} blog posts")
    for i, post in enumerate(posts, 1):
        print(f"\n--- Post {i} ---")
        print(f"Title: {post['title'][:80]}...")
        print(f"Published: {post.get('published', 'N/A')}")
        print(f"Link: {post.get('link', 'N/A')[:70]}...")
        if post.get('summary') and post['summary'] != 'No summary available':
            summary = post['summary'][:150].replace('\n', ' ')
            print(f"Summary: {summary}...")
else:
    print("[INFO] No posts found or scraping failed")

print("\n" + "="*60)
print("Testing Complete!")
print("="*60)
