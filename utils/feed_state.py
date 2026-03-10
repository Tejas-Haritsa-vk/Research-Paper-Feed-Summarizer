
from typing import List, Dict, Optional
from database import get_papers, mark_papers_as_sent

def get_unsent_papers(days: int = 7, limit: int = 100, topics: Optional[List[str]] = None, exclude_sent: bool = True) -> List[Dict]:
    """
    Retrieve papers that have not been sent in a newsletter yet.
    
    Args:
        days: Days to look back.
        limit: Max papers to return.
        topics: List of topics to filter by.
        
    Returns:
        List of paper dictionaries.
    """
    return get_papers(
        days=days, 
        limit=limit, 
        exclude_sent=exclude_sent, 
        topics=topics
    )

def mark_feed_batch_as_sent(paper_ids: List[str]) -> int:
    """
    Mark a batch of papers as sent.
    
    Args:
        paper_ids: List of paper IDs.
        
    Returns:
        Count of updated papers.
    """
    if not paper_ids:
        return 0
    return mark_papers_as_sent(paper_ids)
