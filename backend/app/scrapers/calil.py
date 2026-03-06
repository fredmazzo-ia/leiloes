"""
Scraper para Calil Leilões via Superbid Exchange.
Fonte: https://exchange.superbid.net/loja-oficial/calil-leiloes-818
Raspagem real: ofertas da loja (__NEXT_DATA__ ou fallback em links/oferta).
"""
import json
import re
from datetime import datetime
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedAuction, ScrapedLot

RE_LANCE_ATUAL = re.compile(r"Lance\s+atual:\s*R\$\s*([\d.,]+)", re.I)
RE_PRAÇA = re.compile(r"Pra[cç]a\s+[UÚ]nica\s*\|\s*(\d{2}/\d{2})\s*-\s*(\d{2}:\d{2})", re.I)
RE_LOTE = re.compile(r"Lote\s+(\d+)", re.I)


def _parse_br_currency(s: str) -> Optional[float]:
    if not s:
        return None
    s = str(s).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_superbid_date(day_month: str, time_str: str, year: Optional[int] = None) -> Optional[datetime]:
    """Ex: '05/05', '14:00' -> datetime (ano atual ou year)."""
    try:
        d, m = day_month.split("/")
        h, mi = time_str.split(":")
        y = year or datetime.utcnow().year
        return datetime(y, int(m), int(d), int(h), int(mi))
    except (ValueError, IndexError):
        return None


class CalilScraper(BaseScraper):
    source_name = "calil"
    base_url = "https://exchange.superbid.net"
    loja_url = "https://exchange.superbid.net/loja-oficial/calil-leiloes-818"

    async def scrape(self) -> list[ScrapedAuction]:
        """Raspagem das ofertas da loja Calil na Superbid (várias páginas)."""
        all_lots: list[ScrapedLot] = []
        page = 1
        page_size = 30

        async with httpx.AsyncClient(
            timeout=25.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"},
        ) as client:
            while True:
                url = (
                    f"{self.loja_url}?filter=statusId:1;stores.id:818"
                    f"&searchType=opened&pageNumber={page}&pageSize={page_size}&orderBy=price:desc"
                )
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    html = r.text
                except Exception:
                    break

                # 1) Tentar __NEXT_DATA__
                lots = self._parse_next_data(html)
                if not lots:
                    # 2) Fallback: links /oferta/ e texto ao redor
                    lots = self._parse_oferta_links(html)

                if not lots:
                    break
                all_lots.extend(lots)
                if len(lots) < page_size:
                    break
                page += 1
                if page > 10:
                    break

        # Calil na Superbid: cada "oferta" é um lote; agrupamos em um único leilão virtual "Calil - Superbid"
        if not all_lots:
            return []
        return [
            ScrapedAuction(
                external_id="calil-superbid-818",
                source=self.source_name,
                title="Calil Leilões (Superbid Exchange)",
                url=self.loja_url,
                description=f"{len(all_lots)} ofertas abertas",
                starts_at=None,
                ends_at=None,
                lots=all_lots,
            )
        ]

    def _parse_next_data(self, html: str) -> list[ScrapedLot]:
        """Extrai ofertas do JSON __NEXT_DATA__ (Next.js)."""
        lots: list[ScrapedLot] = []
        match = re.search(r'<script\s+id="__NEXT_DATA__"[^>]*>(\{.+?)</script>', html, re.DOTALL)
        if not match:
            return lots
        try:
            data: dict = json.loads(match.group(1))
            props = data.get("props") or {}
            page_props = props.get("pageProps") or {}
            # Superbid: ofertas podem estar em initialOffers, offers ou dentro de data
            offers = (
                page_props.get("initialOffers")
                or page_props.get("offers")
                or (page_props.get("data") or {}).get("offers")
                or (page_props.get("searchResult") or {}).get("offers")
                or []
            )
            if isinstance(offers, dict):
                offers = offers.get("items") or offers.get("data") or []
            # Buscar recursivamente lista de ofertas (objetos com id/title/price)
            if not isinstance(offers, list) or not offers:
                offers = self._find_offers_in_json(page_props)
            if not isinstance(offers, list):
                return lots
            for item in offers:
                if not isinstance(item, dict):
                    continue
                lot = self._offer_item_to_lot(item)
                if lot:
                    lots.append(lot)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return lots

    def _find_offers_in_json(self, obj: Any, depth: int = 0) -> list:
        """Procura em pageProps qualquer lista de objetos que pareçam ofertas (id + title/name)."""
        if depth > 5:
            return []
        if isinstance(obj, list):
            if obj and isinstance(obj[0], dict):
                first = obj[0]
                if any(first.get(k) for k in ("id", "offerId", "productId")):
                    return obj
            for x in obj:
                found = self._find_offers_in_json(x, depth + 1)
                if found:
                    return found
        if isinstance(obj, dict):
            for k in ("offers", "items", "data", "initialOffers", "searchResult"):
                found = self._find_offers_in_json(obj.get(k) or [], depth + 1)
                if found:
                    return found
        return []

    def _offer_item_to_lot(self, item: dict[str, Any]) -> Optional[ScrapedLot]:
        """Converte um item de oferta do JSON para ScrapedLot."""
        offer_id = str(item.get("id") or item.get("offerId") or item.get("productId") or "")
        title = (item.get("title") or item.get("name") or item.get("description") or "")[:512]
        if not title and not offer_id:
            return None
        friendly_url = item.get("friendlyUrl") or item.get("slug") or ""
        url = f"{self.base_url}/oferta/{friendly_url}" if friendly_url else None
        price = None
        for key in ("currentPrice", "price", "minimumBid", "lanceAtual", "currentBid"):
            val = item.get(key)
            if val is not None:
                if isinstance(val, (int, float)):
                    price = float(val)
                elif isinstance(val, str):
                    price = _parse_br_currency(val)
                break
        if price is None and isinstance(item.get("formattedPrice"), str):
            price = _parse_br_currency(item["formattedPrice"])
        evaluation = item.get("evaluationValue") or item.get("referenceValue")
        if isinstance(evaluation, str):
            evaluation = _parse_br_currency(evaluation)
        return ScrapedLot(
            external_id=offer_id or (friendly_url.split("-")[-1] if friendly_url else "unknown"),
            title=title or f"Oferta {offer_id}",
            description=item.get("description") or None,
            category=item.get("category") or item.get("subCategory", {}).get("description") if isinstance(item.get("subCategory"), dict) else None,
            minimum_bid=price,
            current_bid=price,
            reference_value=float(evaluation) if isinstance(evaluation, (int, float)) else None,
            url=url,
            raw_data=None,
        )

    def _parse_oferta_links(self, html: str) -> list[ScrapedLot]:
        """Fallback: extrai ofertas a partir de links /oferta/ e texto próximo."""
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        lots = []
        for a in soup.select('a[href*="/oferta/"]'):
            href = a.get("href") or ""
            if "exchange.superbid" in href or href.startswith("/oferta/"):
                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
            else:
                continue
            # slug-id no final da URL
            slug_id = href.strip("/").split("/")[-1]
            external_id = (slug_id.split("-")[-1] if "-" in slug_id else slug_id)[:128]
            if external_id in seen:
                continue
            seen.add(external_id)
            text = a.get_text(separator=" ", strip=True)
            title = (a.get("aria-label") or text or f"Oferta {external_id}")[:512]
            if len(title) > 200:
                title = title[:197] + "..."
            lance_match = RE_LANCE_ATUAL.search(text)
            current_bid = _parse_br_currency(lance_match.group(1)) if lance_match else None
            lots.append(
                ScrapedLot(
                    external_id=external_id[:128],
                    title=title,
                    description=None,
                    category=None,
                    minimum_bid=current_bid,
                    current_bid=current_bid,
                    reference_value=None,
                    url=full_url,
                    raw_data=None,
                )
            )
        return lots
