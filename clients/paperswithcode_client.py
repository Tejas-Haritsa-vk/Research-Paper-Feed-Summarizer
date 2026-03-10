import requests
from utils.datetime_utils import format_datetime_to_python, get_datetimedelta

def fetch_pwc_papers(query='', max_results=50, days=7):
    API_URL = f"https://paperswithcode.com/api/v1/search/?q={query}&page_size={max_results}"
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code != 200:
            print(f"PapersWithCode API returned status code: {response.status_code}")
            return []
        
        # Try to parse JSON response
        try:
            data = response.json().get('results', [])
        except ValueError:
            print(f"PapersWithCode API did not return valid JSON")
            return []
            
        datetimedelta = get_datetimedelta(days)

        papers = []
        for d in data:
            pub_date = d.get('published') or d.get('date_added')
            if not pub_date:
                continue
            # Try to parse and filter by date if possible
            try:
                pub_datetime = format_datetime_to_python(pub_date) if 'T' in pub_date else None
                if pub_datetime and pub_datetime < datetimedelta:
                    continue
            except:
                pass  # If date parsing fails, include the paper
            papers.append({
                'title': d['paper_title'],
                'summary': d.get('abstract', ''),
                'link': d['url_abs'],
                'published': pub_date
            })
        return papers
    except requests.RequestException as e:
        print(f"PapersWithCode API request failed: {str(e)}")
        return []

