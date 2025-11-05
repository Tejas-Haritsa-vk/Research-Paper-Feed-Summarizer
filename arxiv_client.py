import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import datetime, timezone, timedelta

def fetch_arxiv_papers(query='', max_results=50, timedeltaindays=7):
    # --- Build Query ---
    base_query = "(all:deep+learning OR all:vision OR all:LLM OR all:multimodal) AND (cat:cs.CV OR cat:cs.LG OR cat:cs.CL)"
    query_filter = f"ti:{query}"
    params = {
            'search_query': f"{query} AND {base_query}",
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
    
    BASE_URL = "http://export.arxiv.org/api/query"
    response = requests.get(BASE_URL, params=params)
    root = ET.fromstring(response.text)
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    papers = []
    datetimedelta = get_datetimedelta(timedeltaindays)
    for entry in root.findall('arxiv:entry', ns):
        publishedDate = format_datetime_to_python(entry.find('arxiv:published', ns).text)
        if publishedDate >= datetimedelta:
            papers.append({
                'title': entry.find('arxiv:title', ns).text.strip(),
                'summary': entry.find('arxiv:summary', ns).text.strip(),
                'link': entry.find('arxiv:id', ns).text,
                'published': publishedDate
            })
    return papers


def format_datetime_to_python(datetime_string):

    # Parse time_string into an aware datetime
    dtobject = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return dtobject
    


def get_datetimedelta(timedeltaindays):
    # Get the current date and time
    now = datetime.now(timezone.utc)
    
    # Calculate the datetime one week ago
    datetimedelta = now - timedelta(days=timedeltaindays)

    return datetimedelta