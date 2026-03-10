"""
ChromaDB Vector Database for Research Papers.

Uses Ollama for embeddings and provides semantic duplicate detection.
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import requests
import json


# Ollama embedding function
class OllamaEmbeddingFunction:
    """Custom embedding function using Ollama."""
    
    def __init__(self, model_name: str = "gemma3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        
    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.embed_documents(input)

    def embed_documents(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = []
        for text in input:
            try:
                # Note: Ollama /api/embeddings vs /api/embed depends on version
                # Checking /api/embeddings for gemma3
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=30
                )
                response.raise_for_status()
                embedding = response.json().get("embedding", [])
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding: {e}")
                embeddings.append([0.0] * 768)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text."""
        return self.embed_documents([text])[0]

    def name(self) -> str:
        return "ollama-embeddings"


# Global client instance
_chroma_client = None
_collection = None


def init_db(persist_directory: str = "./chroma_db"):
    """
    Initialize ChromaDB with Ollama embeddings.
    
    Args:
        persist_directory: Directory to persist the database
    """
    global _chroma_client, _collection
    
    # Create Persistent ChromaDB client
    _chroma_client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create or get collection with Ollama embedding function
    embedding_func = OllamaEmbeddingFunction()
    
    try:
        _collection = _chroma_client.get_collection(
            name="research_papers",
            embedding_function=embedding_func
        )
        print(f"Loaded existing collection with {_collection.count()} papers")
    except:
        _collection = _chroma_client.get_or_create_collection(
            name="research_papers",
            embedding_function=embedding_func,
            metadata={"description": "Research papers with semantic search"}
        )
        print("Created new collection 'research_papers'")
    
    return _collection


import hashlib

def add_paper(paper: Dict[str, Any]) -> Optional[str]:
    """
    Add a paper to the database with duplicate detection.
    
    Args:
        paper: Dictionary with title, summary, link, source, published, etc.
        
    Returns:
        Paper ID if added, None if duplicate
    """
    if _collection is None:
        init_db()
    
    # Create document text for embedding (title + summary)
    document = f"{paper.get('title', '')} {paper.get('summary', '')}"
    
    # Generate stable unique ID from link
    link = paper.get('link', '')
    paper_id = hashlib.md5(link.encode('utf-8')).hexdigest()
    paper_id = f"{paper.get('source', 'unknown')}_{paper_id}"
    
    # Prepare metadata
    metadata = {
        "title": paper.get('title', '')[:500],  # Limit length for ChromaDB
        "summary": paper.get('summary', ''),
        "link": paper.get('link', ''),
        "source": paper.get('source', ''),
        "published": paper.get('published', ''),
        "fetched_date": datetime.now(timezone.utc).isoformat(),
        "is_duplicate": False,
        "sent_in_newsletter": "",  # Track if/when sent in newsletter
        "topics": json.dumps(paper.get('topics', []))
    }
    
    # Add optional fields
    if 'authors' in paper:
        metadata['authors'] = json.dumps(paper['authors'][:10])  # Limit authors
    if 'arxiv_id' in paper:
        metadata['arxiv_id'] = paper.get('arxiv_id', '')
    
    try:
        # Add to collection
        _collection.add(
            ids=[paper_id],
            documents=[document],
            metadatas=[metadata]
        )
        return paper_id
    except Exception as e:
        print(f"Error adding paper: {e}")
        return None


def find_semantic_duplicates(paper: Dict[str, Any], threshold: float = 0.85, n_results: int = 5) -> List[Dict]:
    """
    Find semantically similar papers using vector search.
    
    Args:
        paper: Paper to check for duplicates
        threshold: Similarity threshold (0-1)
        n_results: Number of similar papers to retrieve
        
    Returns:
        List of similar papers with similarity scores
    """
    if _collection is None or _collection.count() == 0:
        return []
    
    # Create query document
    query_text = f"{paper.get('title', '')} {paper.get('summary', '')}"
    
    try:
        # Query similar papers
        results = _collection.query(
            query_texts=[query_text],
            n_results=min(n_results, _collection.count())
        )
        
        similar_papers = []
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i, (doc_id, distance, metadata) in enumerate(zip(
                results['ids'][0],
                results['distances'][0],
                results['metadatas'][0]
            )):
                # Convert distance to similarity (1 - distance for cosine)
                similarity = 1 - distance
                
                if similarity >= threshold:
                    similar_papers.append({
                        'id': doc_id,
                        'similarity': similarity,
                        'metadata': metadata
                    })
        
        return similar_papers
    except Exception as e:
        print(f"Error finding duplicates: {e}")
        return []


def get_papers(days: int = 7, source: Optional[str] = None, limit: int = 100, exclude_sent: bool = True, topics: Optional[List[str]] = None) -> List[Dict]:
    """
    Retrieve papers from database with filtering.
    
    Args:
        days: Number of days to look back
        source: Filter by source (optional)
        limit: Maximum number of papers to return
        exclude_sent: If True, exclude papers already sent in newsletters
        topics: Filter by specific topics (optional)
        
    Returns:
        List of papers
    """
    if _collection is None:
        init_db()
        
    if _collection is None or _collection.count() == 0:
        return []
    
    try:
        # Get all papers first (ChromaDB has issues with complex where clauses)
        results = _collection.get()
        
        if not results or not results['ids']:
            return []
        
        # Filter in Python
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days))
        papers = []
        
        for i, paper_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            
            # Date filter
            try:
                fetched_date_str = metadata.get('fetched_date', '')
                if fetched_date_str:
                    fetched_date = datetime.fromisoformat(fetched_date_str.replace('Z', '+00:00'))
                    if fetched_date < cutoff_date:
                        continue
            except:
                pass  # Include if date parsing fails
            
            # Source filter
            if source and metadata.get('source', '') != source:
                continue
            
            # Exclude sent filter
            if exclude_sent and metadata.get('sent_in_newsletter', '') != '':
                continue
                
            # Topic filter
            if topics:
                stored_topics = []
                try:
                    stored_topics_str = metadata.get('topics', '[]')
                    stored_topics = json.loads(stored_topics_str)
                except:
                    pass
                
                # Check if any requested topic matches (case-insensitive, substring)
                topic_match = False
                requested_topics = [t.lower().strip() for t in topics]
                for st in stored_topics:
                    st_low = st.lower().strip()
                    for rt in requested_topics:
                        # Match if requested topic is a substring of stored topic, or vice versa
                        # and ensure rt is not too short to avoid accidental matches (e.g. "a" in "paper")
                        if (rt in st_low or st_low in rt) and len(rt) >= 2:
                            topic_match = True
                            break
                    if topic_match:
                        break
                
                if not topic_match:
                    continue
            
            papers.append({
                'id': paper_id,
                'title': metadata.get('title', ''),
                'link': metadata.get('link', ''),
                'source': metadata.get('source', ''),
                'published': metadata.get('published', ''),
                'summary': metadata.get('summary', results['documents'][i] if results and results['documents'] else ''),
                'fetched_date': metadata.get('fetched_date', ''),
                'sent_in_newsletter': metadata.get('sent_in_newsletter', ''),
                'topics': json.loads(metadata.get('topics', '[]'))
            })
            
            # Limit results
            if len(papers) >= limit:
                break
        
        return papers
    except Exception as e:
        print(f"Error retrieving papers: {e}")
        return []


def mark_papers_as_sent(paper_ids: List[str]) -> int:
    """
    Mark papers as sent in newsletter.
    
    Args:
        paper_ids: List of paper IDs to mark as sent
        
    Returns:
        Number of papers marked
    """
    if _collection is None:
        init_db()

    if _collection is None or not paper_ids:
        return 0
    
    try:
        sent_date = datetime.now(timezone.utc).isoformat()
        
        # Update each paper's metadata
        for paper_id in paper_ids:
            try:
                # Get current paper
                result = _collection.get(ids=[paper_id])
                if result and result['ids']:
                    # Update metadata
                    _collection.update(
                        ids=[paper_id],
                        metadatas=[{**result['metadatas'][0], 'sent_in_newsletter': sent_date}]
                    )
            except Exception as e:
                print(f"Error marking paper {paper_id} as sent: {e}")
        
        return len(paper_ids)
    except Exception as e:
        print(f"Error in mark_papers_as_sent: {e}")
        return 0


def get_collection():
    """Get the current ChromaDB collection."""
    if _collection is None:
        init_db()
    return _collection


def get_stats() -> Dict[str, Any]:
    """Get database statistics."""
    if _collection is None:
        return {"total_papers": 0}
    
    # Get all papers to count sent vs unsent
    try:
        all_results = _collection.get()
        total = len(all_results['ids']) if all_results and all_results['ids'] else 0
        
        sent = 0
        if all_results and all_results['metadatas']:
            sent = sum(1 for m in all_results['metadatas'] if m.get('sent_in_newsletter', '') != '')
        
        return {
            "total_papers": total,
            "sent_in_newsletter": sent,
            "unsent": total - sent,
            "collection_name": _collection.name
        }
    except:
        return {
            "total_papers": _collection.count(),
            "collection_name": _collection.name
        }
