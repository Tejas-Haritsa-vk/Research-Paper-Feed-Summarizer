
import requests
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET
from typing import Optional

def scrape_article_content(url: str) -> str:
    """
    General purpose scraper for research blog posts.
    Attempts to extract meaningful text from an article.
    """
    try:
        if "arxiv.org" in url:
            return fetch_arxiv_abstract(url) or ""
            
        if "huggingface.co" in url and "/papers/" in url:
            return fetch_huggingface_abstract(url) or ""

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and navigation elements
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.extract()
            
        # Try to find the main content area
        # Common patterns for research blogs including Meta, Google, DeepMind
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.post-content',
            '.article-body',
            '.c-article-body',
            '.blog-post-content',
            '.entry-content',
            '.prose',                 # Tailwind standard for content
            '.rich-text',
            '#main-content',
            '.blog-post__content'      # DeepMind specific
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                # Sanity check: ensure it has significant text
                if len(content.get_text()) > 500:
                    break
        
        if not content:
            content = soup.body
            
        if not content:
            return ""
            
        # Extract text from paragraphs and headers, preserving some structure
        text_elements = content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
        
        structured_text = []
        for el in text_elements:
            # Skip elements inside navigation or footers if they weren't removed
            if any(p.name in ['nav', 'header', 'footer'] for p in el.parents):
                continue
                
            prefix = ""
            if el.name.startswith('h'):
                prefix = "\n## "
            elif el.name == 'li':
                prefix = "- "
            
            text = el.get_text(strip=True)
            if len(text) > 20:
                structured_text.append(f"{prefix}{text}")
        
        clean_text = "\n".join(structured_text)
        
        return clean_text[:12000] # Slightly higher limit for long blogs
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


def fetch_huggingface_abstract(url: str) -> Optional[str]:
    """Extract abstract from a HuggingFace paper page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Look for the Abstract header
        abstract_h2 = soup.find('h2', string=lambda s: s and 'Abstract' in s)
        if abstract_h2:
            abstract_text = []
            # The abstract content is usually in the next sibling div or following paragraphs
            container = abstract_h2.find_next_sibling(['div', 'p'])
            if container:
                # If it's a div, it might contain paragraphs
                if container.name == 'div':
                    paragraphs = container.find_all('p')
                    if paragraphs:
                        abstract_text = [p.get_text(strip=True) for p in paragraphs]
                    else:
                        # Sometimes it's just text in the div
                        abstract_text = [container.get_text(strip=True)]
                else:
                    # It's a p tag directly
                    abstract_text = [container.get_text(strip=True)]
                    # Peek at next few siblings to see if they are also paragraphs
                    for sibling in container.find_next_siblings('p'):
                        abstract_text.append(sibling.get_text(strip=True))
                
            if abstract_text:
                full_abstract = "\n\n".join(abstract_text)
                if len(full_abstract) > 100:
                    return full_abstract
            
        # 2. Check meta description (fallback)
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            desc = meta_description.get('content', '')
            if len(desc) > 150: # Ensure it's not a generic site description
                # Clean up if it starts with "Paper page - "
                desc = re.sub(r"^Paper page - [^\-]+ - ", "", desc)
                return desc.strip()
                
        # 3. Fallback to common prose containers
        prose_content = soup.select_one('div.prose') or soup.select_one('.pb-8.pr-4.text-gray-700')
        if prose_content:
            text = prose_content.get_text(strip=True)
            if len(text) > 100:
                return text
            
    except Exception as e:
        print(f"Error fetching HuggingFace abstract: {e}")
        
    return None

def fetch_arxiv_abstract(link: str) -> Optional[str]:
    """Fetch full abstract from arXiv API using a link."""
    arxiv_id_match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', link)
    if not arxiv_id_match:
        return None
        
    arxiv_id = arxiv_id_match.group(1)
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    try:
        response = requests.get(api_url, timeout=10)
        root = ET.fromstring(response.text)
        ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
        entry = root.find('arxiv:entry', ns)
        if entry is not None:
            summary = entry.find('arxiv:summary', ns)
            if summary is not None:
                return summary.text.strip()
    except Exception as e:
        print(f"Error fetching arXiv abstract for {arxiv_id}: {e}")
        
    return None
