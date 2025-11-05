# app/sources/paperswithcode.py
import httpx
import asyncio
from typing import List
from app.sources.base import BaseFetcher
from app.models import Article
from datetime import datetime

class PapersWithCodeFetcher(BaseFetcher):
    source_name = "paperswithcode"
    BASE = "https://paperswithcode.com/api/v1"

    def __init__(self, client=None):
        self.client = client or httpx.AsyncClient(timeout=20.0)

    async def _fetch_recent(self, page=1, per_page=20):
        # NOTE: PWC API surface can change. Check docs.
        url = f"{self.BASE}/papers/?page={page}&per_page={per_page}"
        r = await self.client.get(url)
        r.raise_for_status()
        return r.json()

    async def fetch_new(self) -> List[Article]:
        out = []
        # simple example: get first 2 pages
        for page in (1,2):
            data = await self._fetch_recent(page=page)
            items = data.get("results") or data.get("data") or []
            for it in items:
                # normalize fields - adjust per actual response shape
                source_id = it.get("id") or it.get("url") or it.get("paper_id")
                title = it.get("title") or it.get("paper_title")
                abstract = it.get("abstract") or it.get("summary") or ""
                authors = [a.get("name") if isinstance(a, dict) else a for a in it.get("authors", [])]
                link = it.get("url") or it.get("paper_url") or f"https://paperswithcode.com{it.get('url','')}"
                pdf_url = it.get("pdf_url") or None
                published = None
                # build Article pydantic model
                art = Article(
                    arxiv_id = it.get("arxiv_id") or None,
                    title = title,
                    summary = abstract,
                    link = link,
                    published = published,
                    authors = authors
                )
                # attach source-specific attributes possibly in raw_metadata
                art.raw = it
                art.source = self.source_name
                art.source_id = source_id
                art.pdf_url = pdf_url
                out.append(art)
        return out
