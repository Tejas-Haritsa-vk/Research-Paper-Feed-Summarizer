import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from database import find_semantic_duplicates
import requests


def extract_topics(title: str, summary: str, llm_agent: Any) -> List[str]:
    """
    Extract relevant topics from paper content using LLM.
    
    Args:
        title: Paper title
        summary: Paper summary
        llm_agent: The OllamaAgent instance to use
        
    Returns:
        List of topic strings
    """
    prompt = f"""
    Analyze the following research paper title and summary and provide a list of 3-5 relevant concise topics.
    Include at least one broad category if it applies (e.g., "AI", "Deep Learning", "Machine Learning", "Computer Vision", "NLP").
    Provide the output ONLY as a valid JSON list of strings.
    
    Title: {title}
    Summary: {summary}
    
    JSON Output:
    """
    
    try:
        response = llm_agent.chat(user_query=prompt, context="")
        # Simple extraction of JSON list
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            topics = json.loads(match.group(0))
            return [str(t).strip() for t in topics]
    except Exception as e:
        print(f"Error extracting topics: {e}")
    
    # Default fallback for storage if LLM completely fails
    return ["Research", "Scientific Paper"]


def extract_arxiv_id(link: str) -> Optional[str]:
    """Extract arXiv ID from link."""
    match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', link)
    return match.group(1) if match else None


def extract_authors(paper: Dict[str, Any]) -> List[str]:
    """
    Extract author names from paper metadata.
    
    Args:
        paper: Paper dictionary
        
    Returns:
        List of author names
    """
    # Authors might be in different formats
    authors = paper.get('authors', [])
    
    if isinstance(authors, str):
        # Parse from string (comma or semicolon separated)
        authors = re.split(r'[,;]', authors)
        authors = [a.strip() for a in authors if a.strip()]
    elif isinstance(authors, list):
        authors = [str(a).strip() for a in authors if a]
    
    return authors[:10]  # Limit to first 10 authors


def normalize_author_name(name: str) -> str:
    """Normalize author name for comparison."""
    # Remove titles, suffixes
    name = re.sub(r'\b(Dr|Prof|PhD|Jr|Sr|III|II)\b\.?', '', name, flags=re.IGNORECASE)
    # Keep only letters and spaces
    name = re.sub(r'[^a-zA-Z\s]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name.lower().strip()


def author_similarity(authors1: List[str], authors2: List[str]) -> float:
    """
    Calculate author list similarity using Jaccard index.
    
    Args:
        authors1: List of author names from paper 1
        authors2: List of author names from paper 2
        
    Returns:
        Similarity score (0-1)
    """
    if not authors1 or not authors2:
        return 0.0
    
    # Normalize names
    set1 = set(normalize_author_name(a) for a in authors1)
    set2 = set(normalize_author_name(a) for a in authors2)
    
    # Jaccard similarity
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats."""
    if not date_str or date_str == 'N/A':
        return None
    
    # Try common formats
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%a, %d %b %Y %H:%M:%S %z",
        "%B %d, %Y",
        "%b %d, %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    
    return None


def date_proximity_score(date1_str: str, date2_str: str) -> float:
    """
    Calculate date proximity score.
    
    Papers published around the same time are more likely to be duplicates.
    
    Args:
        date1_str: Date string from paper 1
        date2_str: Date string from paper 2
        
    Returns:
        Score (0-1), where 1 = same day, 0 = > 30 days apart
    """
    date1 = parse_date(date1_str)
    date2 = parse_date(date2_str)
    
    if not date1 or not date2:
        return 0.0
    
    # Calculate days difference
    days_diff = abs((date1 - date2).days)
    
    # Score decreases linearly over 30 days
    return max(0.0, 1.0 - (days_diff / 30.0))


def exact_match_score(paper1: Dict[str, Any], paper2: Dict[str, Any]) -> float:
    """
    Check for exact matches (same link, arXiv ID, etc.).
    
    Args:
        paper1: First paper
        paper2: Second paper
        
    Returns:
        1.0 if exact match, 0.0 otherwise
    """
    # Check link match
    link1 = paper1.get('link', '').strip().lower()
    link2 = paper2.get('link', '').strip().lower()
    if link1 and link2 and link1 == link2:
        return 1.0
    
    # Check arXiv ID match
    arxiv_id1 = paper1.get('arxiv_id') or extract_arxiv_id(link1)
    arxiv_id2 = paper2.get('arxiv_id') or extract_arxiv_id(link2)
    if arxiv_id1 and arxiv_id2 and arxiv_id1 == arxiv_id2:
        return 1.0
    
    return 0.0


def calculate_duplicate_score(paper1: Dict[str, Any], paper2: Dict[str, Any], semantic_score: float) -> float:
    """
    Calculate comprehensive duplicate score using multiple factors.
    
    Weighting:
    - Semantic similarity (embeddings): 50%
    - Author overlap: 20%
    - Date proximity: 10%
    - Exact match (link/ID): 20%
    
    Args:
        paper1: First paper
        paper2: Second paper
        semantic_score: Pre-computed semantic similarity (0-1)
        
    Returns:
        Combined duplicate score (0-1)
    """
    # Extract metadata
    authors1 = extract_authors(paper1)
    authors2 = extract_authors(paper2)
    
    # Calculate component scores
    semantic = semantic_score * 0.5
    author = author_similarity(authors1, authors2) * 0.2
    date = date_proximity_score(paper1.get('published', ''), paper2.get('published', '')) * 0.1
    exact = exact_match_score(paper1, paper2) * 0.2
    
    final_score = semantic + author + date + exact
    
    return final_score


def is_duplicate(paper1: Dict[str, Any], paper2: Dict[str, Any], threshold: float = 0.85) -> bool:
    """
    Determine if two papers are duplicates using LLM-based semantic analysis.
    
    Args:
        paper1: First paper
        paper2: Second paper
        threshold: Duplicate threshold (default 0.85)
        
    Returns:
        True if papers are duplicates
    """
    # Quick exact match check
    if exact_match_score(paper1, paper2) == 1.0:
        return True
    
    # Use ChromaDB's semantic similarity
    similar_papers = find_semantic_duplicates(paper1, threshold=threshold - 0.15, n_results=5)
    
    # Check if paper2 is in the similar results
    paper2_link = paper2.get('link', '')
    for similar in similar_papers:
        if similar['metadata'].get('link') == paper2_link:
            # Calculate full duplicate score with metadata
            semantic_score = similar['similarity']
            full_score = calculate_duplicate_score(paper1, paper2, semantic_score)
            return full_score >= threshold
    
    return False


# Source priority for choosing which duplicate to keep
SOURCE_PRIORITY = {
    'arXiv': 1,
    'HuggingFace': 2,
    'Google DeepMind': 3,
    'Google Research': 4,
    'Google AI Blog': 5,
    'Meta AI Blog': 6,
    'OpenReview': 7
}


def get_source_priority(source: str) -> int:
    """Get priority for a source (lower is better)."""
    return SOURCE_PRIORITY.get(source, 99)


def deduplicate_papers(papers: List[Dict[str, Any]], threshold: float = 0.85) -> List[Dict[str, Any]]:
    """
    Remove duplicates from a list of papers, keeping the best source.
    
    Args:
        papers: List of papers
        threshold: Duplicate detection threshold
        
    Returns:
        Deduplicated list of papers
    """
    if not papers:
        return []
    
    unique_papers = []
    seen_links = set()
    
    # Sort by source priority first
    papers_sorted = sorted(papers, key=lambda p: get_source_priority(p.get('source', '')))
    
    for paper in papers_sorted:
        link = paper.get('link', '')
        
        # Skip if we've seen this exact link
        if link in seen_links:
            continue
        
        # Check for semantic duplicates
        is_dup = False
        for unique_paper in unique_papers:
            if is_duplicate(paper, unique_paper, threshold):
                is_dup = True
                break
        
        if not is_dup:
            unique_papers.append(paper)
            seen_links.add(link)
    
    return unique_papers
