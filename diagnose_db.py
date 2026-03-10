import chromadb
from database import init_db, get_stats, get_papers
import json

def diagnose():
    print("--- Database Diagnosis ---")
    init_db()
    stats = get_stats()
    print(f"Stats: {stats}")
    
    from database import _collection
    if _collection is None:
        print("Error: Collection not initialized")
        return
        
    count = _collection.count()
    print(f"Total papers in collection: {count}")
    
    if count == 0:
        print("Database is empty. Please run /fetch_and_store first.")
        return
        
    # Get raw data from Chroma
    print("\n--- Raw Data (First 3 papers) ---")
    results = _collection.get(limit=3)
    for i in range(len(results['ids'])):
        meta = results['metadatas'][i]
        print(f"ID: {results['ids'][i]}")
        print(f"Title: {meta.get('title')}")
        print(f"Topics: {meta.get('topics')}")
        print(f"Fetched: {meta.get('fetched_date')}")
        print(f"Sent: {meta.get('sent_in_newsletter')}")
        print("-" * 20)

    # Test get_papers with various filters
    print("\n--- Testing get_papers ---")
    
    print("1. get_papers(days=30, exclude_sent=False, topics=None)")
    papers = get_papers(days=30, exclude_sent=False, topics=None)
    print(f"Result count: {len(papers)}")

    print("\n2. get_papers(days=30, exclude_sent=True, topics=None)")
    papers = get_papers(days=30, exclude_sent=True, topics=None)
    print(f"Result count: {len(papers)}")
    
    print("\n3. get_papers(days=30, exclude_sent=False, topics=['AI', 'Deep Learning'])")
    papers = get_papers(days=30, exclude_sent=False, topics=['AI', 'Deep Learning'])
    print(f"Result count: {len(papers)}")

if __name__ == "__main__":
    diagnose()
