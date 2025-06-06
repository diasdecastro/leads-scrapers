import json
import logging
import argparse

from playwright_scrapers.scrapers.gelbeseiten.scraper import GelbeseitenScraper
from playwright_scrapers.scrapers.gelbeseiten.config import GelbeseitenConfig
from playwright_scrapers.scrapers.googlemaps.scraper import GoogleMapsScraper
from playwright_scrapers.scrapers.googlemaps.config import GoogleMapsConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Parse command line arguments and run the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape business listings from supported sources"
    )

    parser.add_argument(
        "--source",
        "-s",
        type=str,
        choices=["gelbeseiten", "googlemaps"],
        default="gelbeseiten",
        help="Source to scrape from: 'gelbeseiten' or 'googlemaps' (default: gelbeseiten)",
    )

    # Common arguments
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
        default=None,
        help="Rate limit in requests per minute (default: source-specific)",
    )
    parser.add_argument(
        "--proxy",
        "-p",
        type=str,
        default=None,
        help="Proxy server to use (default: none)",
    )

    # Gelbeseiten arguments
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Search term (default: source-specific)",
    )
    parser.add_argument(
        "--city",
        "-c",
        type=str,
        help="City to search in (default: source-specific)",
    )
    parser.add_argument(
        "--max-entries",
        "-m",
        type=int,
        help="Maximum number of entries to fetch (default: all available)",
    )

    # Google Maps arguments
    parser.add_argument(
        "--location",
        type=str,
        help="Location to search in (Google Maps only, default: source-specific)",
    )
    parser.add_argument(
        "--radius-meters",
        type=int,
        help="Search radius in meters (Google Maps only, default: source-specific)",
    )

    args = parser.parse_args()

    try:
        if args.source == "gelbeseiten":
            scraper = GelbeseitenScraper(
                requests_per_minute=args.requests_per_minute or GelbeseitenConfig.REQUESTS_PER_MINUTE,
                proxy=args.proxy,
            )
            results = scraper.scrape(
                query=args.query or GelbeseitenConfig.DEFAULT_QUERY,
                city=args.city or GelbeseitenConfig.DEFAULT_CITY,
                max_entries=args.max_entries,
            )
        elif args.source == "googlemaps":
            scraper = GoogleMapsScraper(
                requests_per_minute=args.requests_per_minute or GoogleMapsConfig.REQUESTS_PER_MINUTE,
                proxy=args.proxy,
            )
            results = scraper.scrape(
                query=args.query or GoogleMapsConfig.DEFAULT_QUERY,
                location=args.location or GoogleMapsConfig.DEFAULT_LOCATION,
                radius_meters=args.radius_meters or GoogleMapsConfig.DEFAULT_RADIUS_METERS,
                max_entries=args.max_entries,
            )
        else:
            raise ValueError("Unknown source selected.")

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
