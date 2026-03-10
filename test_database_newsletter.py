#!/usr/bin/env python
"""Test the database and newsletter functionality."""
# -*- coding: utf-8 -*-

print("Testing ChromaDB Database and Newsletter System")
print("="*60)

# Test 1: Initialize database
print("\n[TEST 1] Initializing ChromaDB...")
from database import init_db, get_stats
try:
    init_db()
    stats = get_stats()
    print(f"[OK] Database initialized: {stats}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 2: Test imports
print("\n[TEST 2] Testing module imports...")
try:
    from utils.deduplication import deduplicate_papers, is_duplicate
    from utils.newsletter import generate_html_newsletter
    print("[OK] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import error: {e}")

# Test 3: Test deduplication with sample papers
print("\n[TEST 3] Testing deduplication logic...")
try:
    sample_papers = [
        {
            "title": "Attention Is All You Need",
            "summary": "We propose the Transformer architecture",
            "link": "https://arxiv.org/abs/1706.03762",
            "source": "arXiv",
            "published": "2017-06-12",
            "authors": ["Vaswani", "Shazeer"]
        },
        {
            "title": "Transformer: Attention Is All You Need",  # Similar title
            "summary": "This paper introduces the Transformer model",  # Similar meaning
            "link": "https://example.com/transformer",
            "source": "HuggingFace",
            "published": "2017-06-12",
            "authors": ["Vaswani"]  # Overlapping author
        },
        {
            "title": "Deep Learning Book",
            "summary": "Comprehensive introduction to deep learning",
            "link": "https://example.com/dlbook",
            "source": "Google Research",
            "published": "2016-01-01"
        }
    ]
    
    unique = deduplicate_papers(sample_papers, threshold=0.85)
    print(f"[OK] Input: {len(sample_papers)} papers")
    print(f"[OK] After deduplication: {len(unique)} unique papers")
    print(f"[OK] Duplicates detected: {len(sample_papers) - len(unique)}")
except Exception as e:
    print(f"[FAIL] Deduplication error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test newsletter generation
print("\n[TEST 4] Testing newsletter generation...")
try:
    test_papers = [
        {
            "title": "Test Paper 1",
            "summary": "This is a test summary",
            "link": "https://test1.com",
            "source": "arXiv",
            "published": "2025-01-01"
        },
        {
            "title": "Test Paper 2",
            "summary": "Another test summary",
            "link": "https://test2.com",
            "source": "HuggingFace",
            "published": "2025-01-02"
        }
    ]
    
    html = generate_html_newsletter(test_papers, title="Test Newsletter")
    if len(html) > 1000 and "<html>" in html:
        print(f"[OK] Newsletter generated successfully ({len(html)} chars)")
        print(f"[OK] Contains proper HTML structure")
    else:
        print(f"[FAIL] Newsletter seems incomplete")
except Exception as e:
    print(f"[FAIL] Newsletter error: {e}")

print("\n" + "="*60)
print("Testing Complete!")
print("\nNext steps:")
print("  1. Start the server: python main.py")
print("  2. Test endpoints:")
print("     - POST http://localhost:8080/fetch_and_store")
print("     - GET http://localhost:8080/newsletter")
print("     - GET http://localhost:8080/stats")
print("="*60)
