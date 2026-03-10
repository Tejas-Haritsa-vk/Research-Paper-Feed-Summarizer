import requests
from utils.datetime_utils import get_datetimedelta
from datetime import datetime, timezone

def fetch_openreview_papers(query='', max_results=50, days=7):
    API_URL = "https://api.openreview.net/notes"
    params = {'content.title': query, 'details': 'replyCount', 'limit': max_results}
    resp = requests.get(API_URL, params=params)
    if resp.status_code != 200:
        return []
    data = resp.json().get('notes', [])
    datetimedelta = get_datetimedelta(days)
    
    papers = []
    for d in data:
        # cdate is in milliseconds since epoch
        try:
            pub_datetime = datetime.fromtimestamp(d['cdate'] / 1000, tz=timezone.utc)
            if pub_datetime < datetimedelta:
                continue
        except:
            pass  # Include paper if date parsing fails
            
        papers.append({
            'title': d['content'].get('title', ''),
            'summary': d['content'].get('abstract', ''),
            'link': f"https://openreview.net/forum?id={d['id']}",
            'published': d['cdate']
        })
    return papers

