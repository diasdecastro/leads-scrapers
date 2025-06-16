import json
import logging
import argparse
import os
from dotenv import load_dotenv

from playwright_scrapers.scrapers.gelbeseiten.scraper import GelbeseitenScraper
from playwright_scrapers.scrapers.gelbeseiten.config import GelbeseitenConfig
from playwright_scrapers.scrapers.googlemaps.scraper import GoogleMapsScraper
from playwright_scrapers.scrapers.googlemaps.config import GoogleMapsConfig
from utils.db import insert_raw_company, get_connection  # add get_connection import
from apis.bundesanzeiger import run_enrichment  # add this import

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()  # Load .env variables before accessing them

    parser = argparse.ArgumentParser(
        description="Scrape business listings from supported sources or enrich data"
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    # Scrape subcommand (default)
    scrape_parser = subparsers.add_parser("scrape", help="Scrape business listings")
    scrape_parser.add_argument(
        "--source",
        "-s",
        type=str,
        choices=["gelbeseiten", "googlemaps"],
        default="gelbeseiten",
        help="Source to scrape from: 'gelbeseiten' or 'googlemaps' (default: gelbeseiten)",
    )
    scrape_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="results.json",
        help="Output JSON file path (default: results.json)",
    )
    scrape_parser.add_argument(
        "--requests-per-minute",
        "-r",
        type=int,
        default=None,
        help="Rate limit in requests per minute (default: source-specific)",
    )
    scrape_parser.add_argument(
        "--proxy",
        "-p",
        type=str,
        default=None,
        help="Proxy server to use (default: none)",
    )
    scrape_parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Search term (default: source-specific)",
    )
    scrape_parser.add_argument(
        "--location",
        type=str,
        help="Location to search in (default: source-specific)",
    )
    scrape_parser.add_argument(
        "--max-entries",
        "-m",
        type=int,
        help="Maximum number of entries to fetch (default: all available)",
    )
    scrape_parser.add_argument(
        "--radius-meters",
        type=int,
        help="Search radius in meters (Google Maps only, default: source-specific)",
    )

    # Enrich subcommand
    enrich_parser = subparsers.add_parser(
        "enrich-bundesanzeiger", help="Enrich companies with Bundesanzeiger API"
    )
    enrich_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of companies to enrich (default: 50)",
    )
    enrich_parser.add_argument(
        "--test",
        action="store_true",
        help="Run enrichment test with Deutsche Bahn AG",
    )

    args = parser.parse_args()

    if args.command == "enrich-bundesanzeiger":
        if getattr(args, "test", False):
            from apis.bundesanzeiger import test_enrich_deutsche_bahn

            test_enrich_deutsche_bahn()
        else:
            run_enrichment(limit=args.limit)
        return

    # Default to scrape if no command is given (for backward compatibility)
    if args.command is None or args.command == "scrape":
        try:
            if args.source == "gelbeseiten":
                scraper = GelbeseitenScraper(
                    requests_per_minute=args.requests_per_minute
                    or GelbeseitenConfig.REQUESTS_PER_MINUTE,
                    proxy=args.proxy,
                )
                results = scraper.scrape(
                    query=args.query or GelbeseitenConfig.DEFAULT_QUERY,
                    location=args.location or GelbeseitenConfig.DEFAULT_CITY,
                    max_entries=args.max_entries,
                )
            elif args.source == "googlemaps":
                scraper = GoogleMapsScraper(
                    requests_per_minute=args.requests_per_minute
                    or GoogleMapsConfig.REQUESTS_PER_MINUTE,
                    proxy=args.proxy,
                )
                results = scraper.scrape(
                    query=args.query or GoogleMapsConfig.DEFAULT_QUERY,
                    location=args.location or GoogleMapsConfig.DEFAULT_LOCATION,
                    radius_meters=args.radius_meters
                    or GoogleMapsConfig.DEFAULT_RADIUS_METERS,
                    max_entries=args.max_entries,
                )
            else:
                raise ValueError("Unknown source selected.")

            # Save to database in a transaction
            conn = get_connection()
            try:
                cursor = conn.cursor()
                for entry in results:
                    insert_raw_company(entry, conn=conn, cursor=cursor)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
                conn.close()

            # Save results to file only if output flag is present
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(
                    f"Successfully scraped {len(results)} entries. Results saved to {args.output}"
                )
            else:
                logger.info(
                    f"Successfully scraped {len(results)} entries. Results saved to database."
                )

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise


if __name__ == "__main__":
    main()
