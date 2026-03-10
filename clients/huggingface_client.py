import requests
from datetime import datetime, timezone
from utils.datetime_utils import get_datetimedelta

def fetch_huggingface_papers(query='', max_results=20, days=7):
    """
    Fetch trending papers from HuggingFace Daily Papers API.
    
    Args:
        query: Search term to filter papers (filters by title/summary)
        max_results: Maximum number of papers to return
        days: Number of days to look back
        
    Returns:
        List of paper dictionaries with title, summary, link, published
    """
    API_URL = "https://huggingface.co/api/daily_papers"
    
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code != 200:
            print(f"HuggingFace API returned status code: {response.status_code}")
            return []
        
        data = response.json()
        datetimedelta = get_datetimedelta(days)
        papers = []
        
        for item in data:
            paper_data = item.get('paper', {})
            
            # Extract publication date
            published_at = paper_data.get('publishedAt')
            if published_at:
                try:
                    # Parse ISO format date
                    pub_datetime = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    # Filter by date
                    if pub_datetime < datetimedelta:
                        continue
                except:
                    pass  # Include if date parsing fails
            
            # Extract paper data
            title = paper_data.get('title', '')
            summary = paper_data.get('summary', '')
            arxiv_id = paper_data.get('id', '')
            
            # Filter by query if provided
            if query:
                query_lower = query.lower()
                if query_lower not in title.lower() and query_lower not in summary.lower():
                    continue
            
            # Build paper dictionary
            paper_dict = {
                'title': title,
                'summary': summary,
                'link': f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else f"https://huggingface.co/papers/{arxiv_id}",
                'published': published_at or 'N/A',
                'upvotes': item.get('upvotes', 0),
                'arxiv_id': arxiv_id
            }
            
            # Add GitHub repo if available
            github_repo = paper_data.get('githubRepo')
            if github_repo:
                paper_dict['github'] = github_repo
                
            papers.append(paper_dict)
            
            # Limit results
            if len(papers) >= max_results:
                break
        
        return papers
        
    except requests.RequestException as e:
        print(f"HuggingFace API request failed: {str(e)}")
        return []
    except Exception as e:
        print(f"Error processing HuggingFace data: {str(e)}")
        return []
