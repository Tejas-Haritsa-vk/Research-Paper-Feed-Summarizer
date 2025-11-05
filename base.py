# app/sources/base.py
from abc import ABC
from typing import List
from app.models import Article

class BaseFetcher(ABC):
    source_name: str = "base"

    @abc.abstractmethod
    async def fetch_new(self) -> List[Article]:
        """
        Return list of Article objects (normalized).
        Should only return items not yet seen (optionally can return recent items and let main dedupe).
        """
        raise NotImplementedError
