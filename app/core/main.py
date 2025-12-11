import asyncio
import logging
import signal
import sys

from aiohttp import ClientSession

from app.api.kpi import KpiAPI
from app.api.premium import PremiumAPI
from app.core.auth import authenticate
from app.core.config import settings
from app.core.scheduler import scheduler
from app.services.logger import setup_logging
from app.tasks.employees import fill_birthdays
from app.tasks.kpi import fill_kpi
from app.tasks.premium import fill_specialists_premium

logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Received shutdown signal. Stopping scheduler...")
    scheduler.shutdown()
    sys.exit(0)


async def main():
    setup_logging()

    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        session = ClientSession(base_url=settings.OKC_BASE_URL)
        await authenticate(
            username=settings.OKC_USERNAME,
            password=settings.OKC_PASSWORD,
            session=session,
        )

        scheduler.add_job(
            fill_birthdays,
            "cron",
            hour="12",
            args=[session],
        )

        premium_api = PremiumAPI(session)
        kpi_api = KpiAPI(session)

        await fill_kpi(kpi_api)
        await fill_specialists_premium(premium_api)

        # await fill_kpi(session)
        scheduler.add_job(
            fill_specialists_premium,
            "interval",
            hours=12,
            args=[premium_api],
        )
        scheduler.start()

        # Keep the program running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")
            scheduler.shutdown()

    except Exception as e:
        logger.error(f"Error in main: {e}")
        if scheduler.running:
            scheduler.shutdown()
        raise


if __name__ == "__main__":
    asyncio.run(main())
