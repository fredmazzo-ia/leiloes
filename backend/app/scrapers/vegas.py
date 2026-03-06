"""
Scraper para Vegas Leilões (https://www.vegasleiloes.com.br/).
Raspagem real: listagem de leilões (encerrados + página principal) e lotes por leilão.
"""
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedAuction, ScrapedLot

# Regex para valores em reais no texto
RE_MONEY = re.compile(r"R\$\s*([\d.,]+)")
RE_LANCE_MIN = re.compile(r"Lance\s+M[ií]nimo[^(]*\([^)]*\):\s*R\$\s*([\d.,]+)", re.I)
RE_AVALIACAO = re.compile(r"Avalia[cç][aã]o:\s*R\$\s*([\d.,]+)", re.I)


def _parse_br_currency(s: str) -> Optional[float]:
    """Converte '1.234.567,89' ou '1.234.567' para float."""
    if not s:
        return None
    s = s.strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_vegas_date(s: str) -> Optional[datetime]:
    """Ex: '04/03/2026 às 15:00' -> datetime."""
    if not s:
        return None
    m = re.search(r"(\d{2}/\d{2}/\d{4})\s*[àaàs]?\s*(\d{2}:\d{2})?", s.strip())
    if not m:
        return None
    try:
        day, month, year = m.group(1).split("/")
        hour, minute = (m.group(2) or "00:00").split(":")
        return datetime(int(year), int(month), int(day), int(hour), int(minute))
    except (ValueError, IndexError):
        return None


class VegasScraper(BaseScraper):
    source_name = "vegas"
    base_url = "https://www.vegasleiloes.com.br"

    async def scrape(self) -> list[ScrapedAuction]:
        """Raspagem: leilões (encerrados + home com cards) e, para cada um, lotes da página de lotes."""
        auctions: list[ScrapedAuction] = []
        seen_ids: set[str] = set()

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"},
        ) as client:
            # 1) Leilões encerrados (várias páginas)
            for page in range(1, 4):
                url = f"{self.base_url}/leiloes/encerrados?page={page}"
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    page_auctions = self._parse_listagem(r.text, url)
                    for a in page_auctions:
                        if a.external_id not in seen_ids:
                            seen_ids.add(a.external_id)
                            auctions.append(a)
                except Exception:
                    break

            # 2) Página principal (pode ter cards de leilões)
            try:
                r = await client.get(f"{self.base_url}/leiloes")
                r.raise_for_status()
                page_auctions = self._parse_listagem(r.text, f"{self.base_url}/leiloes")
                for a in page_auctions:
                    if a.external_id not in seen_ids:
                        seen_ids.add(a.external_id)
                        auctions.append(a)
            except Exception:
                pass

            # 3) Para cada leilão, buscar lotes em /leilao/{id}/lotes
            for auction in auctions:
                leilao_id = auction.external_id
                if not leilao_id.isdigit():
                    continue
                try:
                    lotes_url = f"{self.base_url}/leilao/{leilao_id}/lotes"
                    r = await client.get(lotes_url)
                    r.raise_for_status()
                    auction.lots = self._parse_lotes(r.text, lotes_url)
                except Exception:
                    auction.lots = []

        return auctions

    def _parse_listagem(self, html: str, page_url: str) -> list[ScrapedAuction]:
        """Extrai cards de leilão da listagem (encerrados ou home)."""
        soup = BeautifulSoup(html, "html.parser")
        result = []
        for card in soup.select(".card.box-leilao"):
            link = card.select_one('a[href*="/leilao/"][href*="/lotes"]')
            if not link:
                continue
            href = link.get("href") or ""
            full_url = urljoin(self.base_url, href)
            # external_id = id do leilão (ex: 4097)
            m = re.search(r"/leilao/(\d+)/lotes", full_url)
            if not m:
                continue
            external_id = m.group(1)
            title_el = card.select_one("h6.card-title")
            title = (title_el.get_text(strip=True) if title_el else "") or "Leilão Vegas"
            description_parts = []
            for p in card.select("p.mb-0"):
                description_parts.append(p.get_text(strip=True))
            for div in card.select(".card-text.mb-auto div"):
                description_parts.append(div.get_text(strip=True))
            description = " | ".join(filter(None, description_parts)) or None
            starts_at = None
            for text in description_parts:
                if "Leilão:" in text or "leilão:" in text:
                    starts_at = _parse_vegas_date(text)
                    break
            label = card.select_one(".label_leilao")
            # Encerrado vs Aberto não altera o modelo; podemos guardar em raw depois
            result.append(
                ScrapedAuction(
                    external_id=external_id,
                    source=self.source_name,
                    title=title[:512],
                    url=full_url,
                    description=description[:1024] if description else None,
                    starts_at=starts_at,
                    ends_at=None,
                    lots=[],  # preenchido depois em scrape()
                )
            )
        return result

    def _parse_lotes(self, html: str, page_url: str) -> list[ScrapedLot]:
        """Extrai lotes da página /leilao/{id}/lotes."""
        soup = BeautifulSoup(html, "html.parser")
        result = []
        # Cards de lote: .card-body com link para /item/{id}/detalhes
        for block in soup.select(".card-body"):
            link = block.select_one('a[href*="/item/"][href*="/detalhes"]')
            if not link:
                continue
            href = link.get("href") or ""
            full_url = urljoin(self.base_url, href)
            m = re.search(r"/item/(\d+)/detalhes", href)
            external_id = m.group(1) if m else full_url
            title_el = block.select_one("h5")
            title = (title_el.get_text(strip=True) if title_el else "") or f"Lote {external_id}"
            desc_div = block.select_one('div[style*="text-align: justify"]') or block
            desc_text = desc_div.get_text(separator=" ", strip=True) if desc_div else ""
            minimum_bid = None
            reference_value = None
            for regex, attr in [(RE_LANCE_MIN, "minimum_bid"), (RE_AVALIACAO, "reference_value")]:
                match = regex.search(desc_text)
                if match:
                    val = _parse_br_currency(match.group(1))
                    if attr == "minimum_bid":
                        minimum_bid = val
                    else:
                        reference_value = val
            if not minimum_bid and reference_value:
                minimum_bid = reference_value
            result.append(
                ScrapedLot(
                    external_id=str(external_id),
                    title=title[:512],
                    description=desc_text[:2000] if desc_text else None,
                    category=None,
                    minimum_bid=minimum_bid,
                    current_bid=None,
                    reference_value=reference_value,
                    url=full_url,
                    raw_data=None,
                )
            )
        return result
