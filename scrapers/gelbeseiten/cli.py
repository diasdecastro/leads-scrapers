from datetime import datetime
import sys
import os
import questionary
import json
from typing import Dict, Any
from config.base_cli import ScraperCLI
from scrapers.gelbeseiten.scraper import GelbeseitenScraper
from scrapers.gelbeseiten.config import GelbeseitenConfig
from utils.db import DatabaseManager
from utils.store_data_json_helper import store_data_as_json


class GelbeseitenCLI(ScraperCLI):
    """CLI interface for Gelbeseiten scraper."""

    @property
    def name(self) -> str:
        return "Gelbeseiten Scraper"

    @property
    def description(self) -> str:
        return "Scrapes business listings from Gelbeseiten.de (German Yellow Pages)"

    def get_cli_params(self) -> Dict[str, Any]:
        """Get parameters specific to Gelbeseiten scraper."""
        print("\nConfigure Gelbeseiten scraping parameters:")

        params = {}

        for param, label in GelbeseitenConfig.INPUT_PARAMS:
            value = questionary.text(
                f"{label}:",
                default=str(GelbeseitenConfig.DEFAULT_VALUES.get(param, "")),
            ).ask()
            if value is None:
                return None
            params[param] = value

        storage_choice = questionary.select(
            "Where would you like to store the scraped data?",
            choices=[
                questionary.Choice("Save to database", "database"),
                questionary.Choice("Save as JSON file", "json"),
                questionary.Choice("Save to both database and JSON file", "both"),
            ],
            default="both",
        ).ask()

        if storage_choice is None:
            return None

        params["storage_type"] = storage_choice

        return params

    def run_scraper(self, params: Dict[str, Any]) -> bool:
        try:
            print(f"\nStarting Gelbeseiten scraping...")
            print(f"Query: {params['query']}")
            print(f"Location: {params['location']}")
            print(f"Max entries: {params['max_entries']}")
            print(f"Storage: {params.get('storage_type', 'both')}")

            scraper = GelbeseitenScraper(
                proxy=GelbeseitenConfig.PROXY,
            )

            # Execute scraping
            results = scraper.scrape(
                query=params["query"],
                location=params["location"],
                max_entries=int(params["max_entries"]),
                requests_per_minute=int(params.get("requests_per_minute")),
            )

            if not results:
                print("❌ No results found")
                return False

            # Store results based on user preference
            storage_type = params.get("storage_type", "both")
            if storage_type in ("database", "both"):
                print(f"Storing {len(results)} entries in database...")
                db = DatabaseManager()
                for result in results:
                    db.store_data("gelbeseiten_companies", result)
                print(f"✅ Stored {len(results)} entries in database")
            if storage_type in ("json", "both"):
                data_dir = os.path.join(os.path.dirname(__file__), "data")

                store_data_as_json(results, data_dir, "gelbeseiten")

            return True

        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            return False
