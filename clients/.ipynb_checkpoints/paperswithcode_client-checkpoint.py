import requests
from utils.datetime_utils import get_datetimedelta

def fetch_pwc_papers(query='', max_results=50, timedeltaindays=7):
    API_URL = f"https://paperswithcode.com/api/v1/search/?q={query}&page_size={max_results}"
    response = requests.get(API_URL)
    if response.status_code != 200:
        return []
    data = response.json().get('results', [])
    datetimedelta = get_datetimedelta(timedeltaindays)

    papers = []
    for d in data:
        pub_date = d.get('published') or d.get('date_added')
        if not pub_date:
            continue
        papers.append({
            'title': d['paper_title'],
            'summary': d.get('abstract', ''),
            'link': d['url_abs'],
            'published': pub_date
        })
    return papers
