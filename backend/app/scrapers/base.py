"""
Classe base para scrapers de leilões.
Cada site (Calil, Vegas, etc.) implementa um scraper que retorna dados normalizados.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ScrapedLot:
    external_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    minimum_bid: Optional[float] = None
    current_bid: Optional[float] = None
    reference_value: Optional[float] = None
    url: Optional[str] = None
    raw_data: Optional[str] = None


@dataclass
class ScrapedAuction:
    external_id: str
    source: str
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    lots: list[ScrapedLot]


class BaseScraper(ABC):
    source_name: str = ""

    @abstractmethod
    async def scrape(self) -> list[ScrapedAuction]:
        """Raspagem do site e retorno da lista de leilões normalizados."""
        pass
