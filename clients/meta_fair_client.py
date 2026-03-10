"""
Meta AI Blog client using web scraping.

Meta AI blog (https://ai.meta.com/blog/) does not provide an RSS feed.
This client uses web scraping with BeautifulSoup to extract blog posts.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from utils.datetime_utils import get_datetimedelta
import time
from dateutil import parser


def fetch_meta_fair_papers(query='', max_results=20, days=7):
    """
    Fetch blog posts from Meta AI Blog using web scraping.
    
    Args:
        query: Search term to filter posts (filters by title)
        max_results: Maximum number of posts to return
        days: Number of days to look back
        
    Returns:
        List of post dictionaries with title, summary, link, published
    """
    BASE_URL = "https://ai.meta.com/blog/"
    
    try:
        # Request the blog page
        response = requests.get(BASE_URL, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        datetimedelta = get_datetimedelta(days)
        posts = []
        
        # Find blog post links (using the class pattern from browser investigation)
        # Look for links that go to /blog/ and have meaningful text
        blog_links = soup.find_all('a', href=lambda x: x and '/blog/' in x and x != '/blog/')
        
        seen_urls = set()
        
        for link in blog_links:
            # Get the URL
            url = link.get('href', '')
            if not url or url in seen_urls:
                continue
                
            # Make URL absolute if needed
            if url.startswith('/'):
                url = f"https://ai.meta.com{url}"
            
            # Get title text
            title = link.get_text(strip=True)
            if not title or len(title) < 10:  # Filter out navigation links
                continue
            
            seen_urls.add(url)
            
            # Try to find date near the link
            published_date = 'N/A'
            parent = link.parent
            for _ in range(3):  # Look up to 3 levels up
                if parent:
                    # Look for date-like text (e.g., "Dec 19, 2024")
                    date_elements = parent.find_all(text=True)
                    for text in date_elements:
                        if any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                            try:
                                # Try to parse the date
                                parsed_date = parser.parse(text, fuzzy=True)
                                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                                
                                # Filter by date
                                if parsed_date < datetimedelta:
                                    break
                                    
                                published_date = text.strip()
                                break
                            except:
                                pass
                    if published_date != 'N/A':
                        break
                    parent = parent.parent
            
            # Filter by query if provided
            if query and query.lower() not in title.lower():
                continue
            
            # Try to find a summary (look for paragraph text near the link)
            summary = ''
            container = link.find_parent('div')
            if container:
                paragraphs = container.find_all(['p', 'div'], class_=lambda x: x and ('summary' in str(x).lower() or '8xkk' in str(x)))
                if paragraphs:
                    summary = paragraphs[0].get_text(strip=True)
            
            posts.append({
                'title': title,
                'summary': summary if summary else 'No summary available',
                'link': url,
                'published': published_date
            })
            
            # Limit results
            if len(posts) >= max_results:
                break
        
        return posts
        
    except requests.RequestException as e:
        print(f"Meta AI Blog scraping failed: {str(e)}")
        return []
    except Exception as e:
        print(f"Error parsing Meta AI Blog: {str(e)}")
        return []
