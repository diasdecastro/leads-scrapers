import json
import logging
import argparse

from playwright_scrapers.scrapers.gelbeseiten.scraper import GelbeseitenScraper
from playwright_scrapers.scrapers.gelbeseiten.config import GelbeseitenConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Parse command line arguments and run the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape business listings from Gelbeseiten.de"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=GelbeseitenConfig.DEFAULT_QUERY,
        help=f"Search term (default: {GelbeseitenConfig.DEFAULT_QUERY})",
    )

    parser.add_argument(
        "--city",
        "-c",
        type=str,
        default=GelbeseitenConfig.DEFAULT_CITY,
        help=f"City to search in (default: {GelbeseitenConfig.DEFAULT_CITY})",
    )

    parser.add_argument(
        "--max-entries",
        "-m",
        type=int,
        default=None,
        help="Maximum number of entries to fetch (default: all available)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="results.json",
        help="Output JSON file path (default: results.json)",
    )

    parser.add_argument(
        "--requests-per-minute",
        "-r",
        type=int,
        default=GelbeseitenConfig.REQUESTS_PER_MINUTE,
        help=f"Rate limit in requests per minute (default: {GelbeseitenConfig.REQUESTS_PER_MINUTE})",
    )

    parser.add_argument(
        "--proxy",
        "-p",
        type=str,
        default=None,
        help="Proxy server to use (default: none)",
    )

    args = parser.parse_args()

    try:
        # Initialize and run scraper
        scraper = GelbeseitenScraper(
            requests_per_minute=args.requests_per_minute, proxy=args.proxy
        )
        results = scraper.scrape(
            query=args.query, city=args.city, max_entries=args.max_entries
        )

        # Save results
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Successfully scraped {len(results)} entries. Results saved to {args.output}"
        )

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise


if __name__ == "__main__":
    main()
