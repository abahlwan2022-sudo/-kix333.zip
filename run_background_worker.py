"""
Background worker entrypoint (24/7).

Runs the continuous scraper service:
- sync sitemap every 2 hours
- resume-safe pending queue processing
- auto-trigger matcher + Gemini pricing pipeline
"""
from __future__ import annotations

import asyncio
import logging
import os

from utils.async_scraper import run_continuous_scraper_service


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(run_continuous_scraper_service())


if __name__ == "__main__":
    main()

