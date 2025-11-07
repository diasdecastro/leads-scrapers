#!/usr/bin/env python3
"""
Imprint Data Enricher - Extract official company names from website imprint pages

This enricher extracts official company names and legal information from website imprint pages.
It provides a CLI interface with regex and LLM-based extraction methods.
"""

import argparse
import logging
import sys
import os

# Add parent directories to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from scrapers.imprint_data.scraper import OfficialNameExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cli_enrich(args):
    """Handle CLI enrichment command."""
    try:
        logger.info(f"CLI Enrichment: method={args.method}, delay={args.delay}")

        extractor = OfficialNameExtractor(llm_model=args.llm_model)

        # Validate method
        if args.method not in ["regex", "llm"]:
            print("❌ Error: Method must be 'regex' or 'llm'")
            sys.exit(1)

        # Check Ollama for LLM method
        if args.method == "llm":
            print(f"🤖 Using LLM method with model: {args.llm_model}")
            print("💡 Make sure Ollama is running: ollama serve")
            print(f"💡 Make sure model is available: ollama pull {args.llm_model}")

        print(f"\n🏛️ Configure Imprint Data enrichment:")
        enriched_count = extractor.run_enrichment(delay=args.delay, method=args.method)

        print(f"\n🎉 Imprint Data Enrichment Complete!")
        print(f"📊 Method: {args.method}")
        print(f"⏱️ Delay: {args.delay} seconds")
        print(
            f"✅ Companies enriched: {enriched_count if enriched_count else 'Unknown'}"
        )

        return enriched_count

    except Exception as e:
        logger.error(f"CLI enrichment failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Imprint Data Enricher - Extract official company names from imprint pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --method regex --delay 1.0
  %(prog)s --method llm --llm-model "deepseek-r1:8b" --delay 2.0
        """,
    )

    parser.add_argument(
        "--method",
        "-m",
        type=str,
        choices=["regex", "llm"],
        default="regex",
        help="Extraction method: 'regex' (fast) or 'llm' (accurate, requires Ollama)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default="deepseek-r1:8b",
        help="LLM model to use for extraction (default: deepseek-r1:8b)",
    )

    args = parser.parse_args()
    cli_enrich(args)


if __name__ == "__main__":
    main()
