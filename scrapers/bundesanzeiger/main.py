#!/usr/bin/env python3
"""
Bundesanzeiger Financial Data Enricher

A scraper for enriching company data with official financial information
from the German Federal Gazette (Bundesanzeiger).
"""

import argparse
import os
import sys
import traceback
import time

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from scrapers.bundesanzeiger.bundesanzeiger import BundesanzeigerScraper
from utils.db import get_all_company_names


def handle_enrich_command(args):
    """Handle the enrich command."""
    try:
        scraper = BundesanzeigerScraper()

        if args.test:
            print("🧪 Testing with Deutsche Bahn AG...")
            scraper.store_report_data_to_db("Deutsche Bahn AG")
            print("✅ Test completed successfully!")
            return

        if args.company:
            print(f"🏛️ Enriching single company: {args.company}")
            scraper.store_report_data_to_db(args.company)
            print("✅ Company enrichment completed!")
            return

        # Batch enrichment
        print(
            f"🏛️ Starting batch enrichment (limit: {args.limit}, delay: {args.delay}s)"
        )

        companies = get_all_company_names()

        if not companies:
            print("❌ No companies found in database")
            return

        companies_to_process = companies[: args.limit]
        enriched_count = 0

        for i, company in enumerate(companies_to_process, 1):
            try:
                company_name = company["name"]
                print(f"[{i}/{len(companies_to_process)}] Processing: {company_name}")

                # Add delay between requests (except for first)
                if i > 1:
                    time.sleep(args.delay)

                scraper.store_report_data_to_db(company_name)
                enriched_count += 1
                print(f"  ✅ Enriched successfully")

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        print(f"\n🎉 Batch enrichment completed!")
        print(f"📊 Companies processed: {len(companies_to_process)}")
        print(f"✅ Successfully enriched: {enriched_count}")

    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def handle_search_command(args):
    """Handle the search command."""
    try:
        scraper = BundesanzeigerScraper()
        print(f"🔍 Searching for reports: {args.company}")

        report = scraper.get_jahresabschluss_report(args.company)

        if report:
            print(f"✅ Jahresabschluss report found!")
            print(f"📄 Report name: {report.get('name', 'N/A')}")
            print(f"📅 Date: {report.get('date', 'N/A')}")
            print(f"🏢 Company: {report.get('company', 'N/A')}")
        else:
            print(f"❌ No Jahresabschluss report found for {args.company}")

    except Exception as e:
        print(f"❌ Search failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def handle_report_command(args):
    """Handle the report command."""
    try:
        scraper = BundesanzeigerScraper()
        print(f"📊 Getting detailed report: {args.company}")

        if args.save:
            print("💾 Saving report to file...")
            scraper.save_jahresabschluss_to_file(args.company)
        else:
            # Print report information
            scraper.print_jahresabschluss_info(args.company)

    except Exception as e:
        print(f"❌ Report retrieval failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def create_cli_parser():
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Bundesanzeiger Financial Data Enricher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s enrich --limit 50 --delay 2.0
  %(prog)s search --company "Deutsche Bahn AG"
  %(prog)s report --company "Deutsche Bahn AG"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Enrich command
    enrich_parser = subparsers.add_parser(
        "enrich", help="Enrich companies with financial data from Bundesanzeiger"
    )
    enrich_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of companies to process (default: 50)",
    )
    enrich_parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between API calls in seconds (default: 2.0)",
    )
    enrich_parser.add_argument(
        "--test", action="store_true", help="Test with Deutsche Bahn AG only"
    )
    enrich_parser.add_argument(
        "--company", type=str, help="Enrich specific company by name"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for company reports")
    search_parser.add_argument(
        "--company", type=str, required=True, help="Company name to search for"
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report", help="Get detailed report for a company"
    )
    report_parser.add_argument(
        "--company", type=str, required=True, help="Company name to get report for"
    )
    report_parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to file in files/bundesanzeiger_reports/",
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Handle commands
    if args.command == "enrich":
        handle_enrich_command(args)
    elif args.command == "search":
        handle_search_command(args)
    elif args.command == "report":
        handle_report_command(args)


if __name__ == "__main__":
    main()
