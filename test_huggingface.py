#!/usr/bin/env python
"""Test HuggingFace client to verify it's working."""
# -*- coding: utf-8 -*-

from clients.huggingface_client import fetch_huggingface_papers

print("="*60)
print("Testing HuggingFace Daily Papers Client")
print("="*60)

# Test 1: Get all recent papers (90 days, no query filter)
print("\n[TEST 1] Fetching recent trending papers (90 days, no filter)")
papers = fetch_huggingface_papers(query='', max_results=5, days=90)

if papers:
    print(f"[SUCCESS] Found {len(papers)} papers")
    for i, paper in enumerate(papers, 1):
        print(f"\n--- Paper {i} ---")
        print(f"Title: {paper['title'][:100]}...")
        print(f"Published: {paper['published']}")
        print(f"Upvotes: {paper.get('upvotes', 0)}")
        print(f"Link: {paper['link']}")
        if paper.get('github'):
            print(f"GitHub: {paper['github']}")
        print(f"Summary: {paper['summary'][:150]}...")
else:
    print("[WARNING] No papers found")

# Test 2: Search for specific topic
print("\n" + "="*60)
print("\n[TEST 2] Searching for 'deep learning' papers")
papers = fetch_huggingface_papers(query='deep learning', max_results=3, days=90)

if papers:
    print(f"[SUCCESS] Found {len(papers)} papers matching 'deep learning'")
    for i, paper in enumerate(papers, 1):
        print(f"\n--- Paper {i} ---")
        print(f"Title: {paper['title'][:100]}...")
        print(f"Upvotes: {paper.get('upvotes', 0)}")
else:
    print("[INFO] No papers found matching 'deep learning'")

print("\n" + "="*60)
print("Testing Complete!")
print("="*60)
