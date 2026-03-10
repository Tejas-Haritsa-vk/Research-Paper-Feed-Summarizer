import feedparser
from utils.datetime_utils import get_datetimedelta
from datetime import datetime, timezone
import time

def fetch_deepmind_papers(query='', max_results=20, days=7):
    """
    Fetch blog posts from Google DeepMind Blog RSS feed.
    
    Args:
        query: Search term to filter posts (filters by title/summary)
        max_results: Maximum number of posts to return
        days: Number of days to look back
        
    Returns:
        List of post dictionaries with title, summary, link, published
    """
    RSS_FEED = "https://deepmind.google/blog/rss.xml"
    feed = feedparser.parse(RSS_FEED)
    datetimedelta = get_datetimedelta(days)
    posts = []

    for entry in feed.entries[:max_results * 2]:  # Get more to filter by date
        # Filter by query if provided
        if query and query.lower() not in entry.title.lower() and query.lower() not in entry.get('summary', '').lower():
            continue
            
        # Try to filter by date
        try:
            if hasattr(entry, 'published_parsed'):
                pub_datetime = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
                if pub_datetime < datetimedelta:
                    continue
        except:
            pass  # Include if date parsing fails
            
        posts.append({
            'title': entry.title,
            'summary': entry.get('summary', entry.get('description', '')),
            'link': entry.link,
            'published': entry.get('published', 'N/A')
        })
        
        # Limit results
        if len(posts) >= max_results:
            break
    
    return posts
