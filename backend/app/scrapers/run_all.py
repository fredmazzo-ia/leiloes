"""
Executa todos os scrapers e persiste no banco.
Uso: python -m app.scrapers.run_all
"""
import asyncio
import os
import sys

# Garantir que o app está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.models.database import Base
from app.models.schemas import AuctionModel, LotModel
from app.scrapers.calil import CalilScraper
from app.scrapers.vegas import VegasScraper


async def run_all():
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    scrapers = [CalilScraper(), VegasScraper()]

    async with AsyncSessionLocal() as session:
        for scraper in scrapers:
            try:
                print(f"Executando scraper: {scraper.source_name}...")
                auctions = await scraper.scrape()
                print(f"  -> {len(auctions)} leilão(ões), {sum(len(a.lots) for a in auctions)} lote(s)")
                for sa in auctions:
                    result = await session.execute(
                        select(AuctionModel).where(
                            AuctionModel.source == sa.source,
                            AuctionModel.external_id == sa.external_id,
                        )
                    )
                    existing = result.scalar_one_or_none()
                    if existing:
                        existing.title = sa.title
                        existing.url = sa.url
                        existing.description = sa.description
                        existing.starts_at = sa.starts_at
                        existing.ends_at = sa.ends_at
                        session.add(existing)
                        auction_id = existing.id
                    else:
                        auction = AuctionModel(
                            external_id=sa.external_id,
                            source=sa.source,
                            title=sa.title,
                            url=sa.url,
                            description=sa.description,
                            starts_at=sa.starts_at,
                            ends_at=sa.ends_at,
                        )
                        session.add(auction)
                        await session.flush()
                        auction_id = auction.id

                    for sl in sa.lots:
                        lot_result = await session.execute(
                            select(LotModel).where(
                                LotModel.auction_id == auction_id,
                                LotModel.external_id == sl.external_id,
                            )
                        )
                        if lot_result.scalar_one_or_none() is None:
                            session.add(
                                LotModel(
                                    auction_id=auction_id,
                                    external_id=sl.external_id,
                                    title=sl.title,
                                    description=sl.description,
                                    category=sl.category,
                                    minimum_bid=sl.minimum_bid,
                                    current_bid=sl.current_bid,
                                    reference_value=sl.reference_value,
                                    url=sl.url,
                                    raw_data=sl.raw_data,
                                )
                            )
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Erro no scraper {scraper.source_name}: {e}")
            await asyncio.sleep(1)  # Respeito entre fontes
    await engine.dispose()
    print("Scrapers concluídos.")


if __name__ == "__main__":
    asyncio.run(run_all())
