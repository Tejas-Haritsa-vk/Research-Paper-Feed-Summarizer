import requests

def fetch_openreview_papers(query='', max_results=50, timedeltaindays=7):
    API_URL = "https://api.openreview.net/notes"
    params = {'content.title': query, 'details': 'replyCount', 'limit': max_results}
    resp = requests.get(API_URL, params=params)
    if resp.status_code != 200:
        return []
    data = resp.json().get('notes', [])
    papers = [
        {
            'title': d['content'].get('title', ''),
            'summary': d['content'].get('abstract', ''),
            'link': f"https://openreview.net/forum?id={d['id']}",
            'published': d['cdate']
        }
        for d in data
    ]
    return papers
