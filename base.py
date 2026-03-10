# app/sources/base.py
import abc
from abc import ABC
from typing import List, Dict, Any

class BaseFetcher(ABC):
    source_name: str = "base"

    @abc.abstractmethod
    async def fetch_new(self) -> List[Dict[str, Any]]:
        """
        Return list of article dictionaries (normalized).
        Should only return items not yet seen (optionally can return recent items and let main dedupe).
        Each dict should have: title, summary, link, published
        """
        raise NotImplementedError
