#!/usr/bin/env python
"""Test topic filtering functionality."""
# -*- coding: utf-8 -*-

import json
from database import init_db, add_paper, get_papers

print("Testing Topic Filtering System")
print("="*60)

# Initialize database
print("\n[1] Initializing database...")
init_db()

# Add test papers with topics
print("\n[2] Adding test papers with topics...")
papers_to_add = [
    {
        "title": "Quantum Computing Advances",
        "summary": "This paper discusses quantum supremacy.",
        "link": "https://quantum.com",
        "source": "arXiv",
        "published": "2025-01-01",
        "topics": ["Quantum", "Physics"]
    },
    {
        "title": "Scaling Vision Transformers",
        "summary": "How to scale ViTs for better performance.",
        "link": "https://vit.ai",
        "source": "Google Research",
        "published": "2025-01-02",
        "topics": ["Computer Vision", "Deep Learning", "Transformers"]
    },
    {
        "title": "Reinforcement Learning in Robotics",
        "summary": "RL for humanoid control.",
        "link": "https://robots.io",
        "source": "HuggingFace",
        "published": "2025-01-03",
        "topics": ["Robotics", "Reinforcement Learning", "AI"]
    }
]

for paper in papers_to_add:
    add_paper(paper)

# Test Topic Filter: ["AI"]
print("\n[3] Filtering papers for topics: ['AI']")
papers = get_papers(days=365, topics=["AI"], exclude_sent=False)
print(f"   Found {len(papers)} papers matching 'AI'")
for p in papers:
    print(f"   - {p['title']} Topics: {p.get('topics')}")

# Test Topic Filter: ["Quantum", "Robotics"]
print("\n[4] Filtering papers for topics: ['Quantum', 'Robotics']")
papers = get_papers(days=365, topics=["Quantum", "Robotics"], exclude_sent=False)
print(f"   Found {len(papers)} papers matching 'Quantum' OR 'Robotics'")
for p in papers:
    print(f"   - {p['title']} Topics: {p.get('topics')}")

# Test Default filter (as used in main.py logic but direct call)
print("\n[5] Filtering papers for topics: ['Deep Learning', 'Computer Vision']")
papers = get_papers(days=365, topics=["Deep Learning", "Computer Vision"], exclude_sent=False)
print(f"   Found {len(papers)} papers matching 'Deep Learning' OR 'Computer Vision'")
for p in papers:
    print(f"   - {p['title']} Topics: {p.get('topics')}")

print("\n" + "="*60)
print("Topic Filter Test Complete!")
