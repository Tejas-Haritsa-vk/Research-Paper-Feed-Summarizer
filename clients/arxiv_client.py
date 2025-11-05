import requests
import xml.etree.ElementTree as ET
from utils.datetime_utils import format_datetime_to_python, get_datetimedelta

def fetch_arxiv_papers(query='', max_results=50, days=7):
    base_query = "(all:deep+learning OR all:vision OR all:LLM OR all:multimodal) AND (cat:cs.CV OR cat:cs.LG OR cat:cs.CL)"
    params = {
        'search_query': f"{query} AND {base_query}",
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }

    response = requests.get("http://export.arxiv.org/api/query", params=params)
    root = ET.fromstring(response.text)
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    datetimedelta = get_datetimedelta(days)
    papers = []

    for entry in root.findall('arxiv:entry', ns):
        publishedDate = format_datetime_to_python(entry.find('arxiv:published', ns).text)
        if publishedDate >= datetimedelta:
            papers.append({
                'title': entry.find('arxiv:title', ns).text.strip(),
                'summary': entry.find('arxiv:summary', ns).text.strip(),
                'link': entry.find('arxiv:id', ns).text,
                'published': publishedDate.isoformat()
            })
    return papers
