#!/usr/bin/env python3
"""
Google Maps Scraper - Business listings from Google Maps

This scraper extracts business listings from Google Maps with location-based search.
It provides a CLI interface for data extraction.
"""

import argparse
import json
import logging
import sys
import os

# Add parent directories to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from scrapers.googlemaps.scraper import GoogleMapsScraper
from scrapers.googlemaps.config import GoogleMapsConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cli_scrape(args):
    """Handle CLI scraping command."""
    try:
        logger.info(
            f"CLI Scrape: {args.query} in {args.location} (radius: {args.radius_meters}m)"
        )

        scraper = GoogleMapsScraper(
            requests_per_minute=args.requests_per_minute, proxy=args.proxy
        )

        results = scraper.scrape(
            query=args.query,
            location=args.location,
            radius_meters=args.radius_meters,
            max_entries=args.max_entries,
        )

        # Save results
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {args.output}")

        # Print summary
        print(f"\n🎉 Google Maps Scraping Complete!")
        print(f"📊 Results: {len(results)} businesses found")
        print(f"🔍 Query: {args.query}")
        print(f"📍 Location: {args.location}")
        print(f"📐 Radius: {args.radius_meters} meters")

        if args.output:
            print(f"💾 Saved to: {args.output}")
        else:
            print("\n📋 Results:")
            for i, business in enumerate(results, 1):
                print(
                    f"{i}. {business.get('name', 'N/A')} - {business.get('address', 'N/A')}"
                )

        return results

    except Exception as e:
        logger.error(f"CLI scraping failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Google Maps Scraper - Extract business listings from Google Maps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "restaurant" --location "berlin" --max-entries 25
  %(prog)s --query "hotel" --location "munich" --radius-meters 2000
  %(prog)s --query "cafe" --location "hamburg" --output results.json
        """,
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=GoogleMapsConfig.DEFAULT_QUERY,
        help=f"Search term (default: {GoogleMapsConfig.DEFAULT_QUERY})",
    )
    parser.add_argument(
        "--location",
        "-l",
        type=str,
        default=GoogleMapsConfig.DEFAULT_LOCATION,
        help=f"Location to search in (default: {GoogleMapsConfig.DEFAULT_LOCATION})",
    )
    parser.add_argument(
        "--max-entries",
        "-m",
        type=int,
        default=15,
        help="Maximum entries to scrape (default: 15)",
    )
    parser.add_argument(
        "--radius-meters",
        "-rad",
        type=int,
        default=GoogleMapsConfig.DEFAULT_RADIUS_METERS,
        help=f"Search radius in meters (default: {GoogleMapsConfig.DEFAULT_RADIUS_METERS})",
    )
    parser.add_argument(
        "--requests-per-minute",
        "-r",
        type=int,
        default=GoogleMapsConfig.REQUESTS_PER_MINUTE,
        help=f"Rate limit (default: {GoogleMapsConfig.REQUESTS_PER_MINUTE})",
    )
    parser.add_argument(
        "--proxy", "-p", type=str, default=None, help="Proxy server URL (optional)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output JSON file (optional, prints to console if not specified)",
    )

    args = parser.parse_args()
    cli_scrape(args)


if __name__ == "__main__":
    main()
