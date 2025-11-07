import sys
import os
import questionary
from typing import Dict, Any
from config.base_cli import ScraperCLI
from scrapers.googlemaps.config import GoogleMapsConfig
from scrapers.googlemaps.scraper import GoogleMapsScraper
from utils.db import DatabaseManager
from utils.store_data_json_helper import store_data_as_json


class GoogleMapsCLI(ScraperCLI):
    """CLI interface for Google Maps scraper."""

    @property
    def name(self) -> str:
        return "Google Maps Scraper"

    @property
    def description(self) -> str:
        return "Scrapes business listings from Google Maps with location-based search"

    def get_cli_params(self) -> Dict[str, Any]:
        """Get parameters specific to Google Maps scraper."""
        print("\n Configure Google Maps scraping parameters:")

        params = {}

        for param, label in GoogleMapsConfig.INPUT_PARAMS:
            value = questionary.text(
                f"{label}:",
                default=str(GoogleMapsConfig.DEFAULT_VALUES.get(param, "")),
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
        """Run the Google Maps scraper with the provided parameters."""
        try:
            print(f"\nStarting Google Maps scraping...")
            print(f"Query: {params['query']}")
            print(f"Location: {params['location']}")

            scraper = GoogleMapsScraper()

            results = scraper.scrape(
                query=params["query"],
                location=params["location"],
                max_entries=int(params["max_entries"]),
                requests_per_minute=int(params.get("requests_per_minute")),
            )

            print(f"\nScraping completed. Total entries scraped: {len(results)}")

            storage_type = params.get("storage_type", "both")

            if storage_type in ("database", "both"):
                db = DatabaseManager()
                for result in results:
                    db.store_data("googlemaps_companies", result)
                print(f"✅ Stored {len(results)} entries in database")

            if storage_type in ("json", "both"):
                data_dir = os.path.join(os.path.dirname(__file__), "data")
                store_data_as_json(results, data_dir, "googlemaps")

            return True

        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            return False
