"""
Scraper para Vegas Leilões (https://www.vegasleiloes.com.br/).
MVP: estrutura pronta; implementação real depende da análise do HTML/JS do site.
"""
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedAuction, ScrapedLot


class VegasScraper(BaseScraper):
    source_name = "vegas"
    base_url = "https://www.vegasleiloes.com.br"

    async def scrape(self) -> list[ScrapedAuction]:
        """Raspagem da listagem de leilões do Vegas."""
        auctions: list[ScrapedAuction] = []
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(f"{self.base_url}/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.select('a[href*="leilao"], a[href*="lote"], a[href*="leiloe"]')[:20]:
                    href = link.get("href") or ""
                    if not href.startswith("http"):
                        href = f"{self.base_url}{href}" if href.startswith("/") else f"{self.base_url}/{href}"
                    title = (link.get_text(strip=True) or "Leilão")[:200]
                    external_id = self._slug_or_id(href, title)
                    auctions.append(
                        ScrapedAuction(
                            external_id=external_id,
                            source=self.source_name,
                            title=title or "Leilão Vegas",
                            url=href,
                            lots=[],
                        )
                    )
                seen = set()
                unique = []
                for a in auctions:
                    if a.external_id not in seen:
                        seen.add(a.external_id)
                        unique.append(a)
                return unique
            except Exception:
                return []

    @staticmethod
    def _slug_or_id(url: str, title: str) -> str:
        s = url.strip("/").split("/")[-1] or re.sub(r"\W+", "-", title)[:64]
        return (s or "unknown")[:128]
