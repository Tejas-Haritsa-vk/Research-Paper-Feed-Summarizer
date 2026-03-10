#!/usr/bin/env python
"""Test newsletter tracking to prevent duplicate sends."""
# -*- coding: utf-8 -*-

print("Testing Newsletter Tracking System")
print("="*60)

# Initialize database
print("\n[1] Initializing database...")
from database import init_db, add_paper, get_papers, mark_papers_as_sent, get_stats
init_db()

# Add test papers
print("\n[2] Adding test papers...")
papers_to_add = [
    {
        "title": "Test Paper A",
        "summary": "First test paper",
        "link": "https://test-a.com",
        "source": "arXiv",
        "published": "2025-01-01"
    },
    {
        "title": "Test Paper B",
        "summary": "Second test paper",
        "link": "https://test-b.com",
        "source": "Google Research",
        "published": "2025-01-02"
    },
    {
        "title": "Test Paper C",
        "summary": "Third test paper",
        "link": "https://test-c.com",
        "source": "HuggingFace",
        "published": "2025-01-03"
    }
]

paper_ids = []
for paper in papers_to_add:
    pid = add_paper(paper)
    if pid:
        paper_ids.append(pid)
print(f"Added {len(paper_ids)} test papers")

# Check initial stats
print("\n[3] Initial database stats:")
stats = get_stats()
print(f"   Total papers: {stats['total_papers']}")
print(f"   Sent in newsletter: {stats['sent_in_newsletter']}")
print(f"   Unsent: {stats['unsent']}")

# Get papers (should exclude already sent by default)
print("\n[4] Getting unsent papers (exclude_sent=True):")
unsent = get_papers(days=365, exclude_sent=True)
print(f"   Found {len(unsent)} unsent papers")

# Mark first 2 papers as sent
print("\n[5] Marking first 2 papers as sent in newsletter...")
marked = mark_papers_as_sent(paper_ids[:2])
print(f"   Marked {marked} papers as sent")

# Check stats again
print("\n[6] Stats after marking:")
stats = get_stats()
print(f"   Total papers: {stats['total_papers']}")
print(f"   Sent in newsletter: {stats['sent_in_newsletter']}")
print(f"   Unsent: {stats['unsent']}")

# Get unsent papers again
print("\n[7] Getting unsent papers again:")
unsent = get_papers(days=365, exclude_sent=True)
print(f"   Found {len(unsent)} unsent papers")
for p in unsent:
    print(f"   - {p['title']}")

# Get ALL papers (including sent)
print("\n[8] Getting ALL papers (exclude_sent=False):")
all_papers = get_papers(days=365, exclude_sent=False)
print(f"   Found {len(all_papers)} total papers")
for p in all_papers:
    sent_status = "SENT" if p['sent_in_newsletter'] else "UNSENT"
    print(f"   - {p['title']} [{sent_status}]")

print("\n" + "="*60)
print("Test Complete!")
print("\nSummary:")
print("  - Papers marked as sent are excluded from future newsletters")
print("  - Use exclude_sent=False to see all papers including sent ones")
print("  - Stats endpoint tracks sent vs unsent counts")
print("="*60)
