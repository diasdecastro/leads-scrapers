import sys
import os
import questionary
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from config.base_cli import EnricherCLI


class BundesanzeigerCLI(EnricherCLI):
    """CLI interface for Bundesanzeiger API enrichment."""

    @property
    def name(self) -> str:
        return "Bundesanzeiger API Enricher"

    @property
    def description(self) -> str:
        return "Enriches company data with official financial information from German Federal Gazette"

    def get_cli_params(self) -> Dict[str, Any]:
        """Get parameters for Bundesanzeiger enrichment."""
        print("\n🏛️ Configure Bundesanzeiger data enrichment:")
        print(
            "💡 This will enrich existing companies in your database with financial data"
        )

        # Choose between test mode and batch processing
        mode = questionary.select(
            "Select enrichment mode:",
            choices=[
                questionary.Choice("batch", "Batch process companies from database"),
                questionary.Choice(
                    "test", "Test with a specific company (Deutsche Bahn AG)"
                ),
                questionary.Choice("single", "Enrich a single company by name"),
            ],
        ).ask()

        if mode is None:
            return None

        params = {"mode": mode}

        if mode == "batch":
            limit = questionary.text(
                "Maximum number of companies to process:", default="50"
            ).ask()

            if limit is None:
                return None

            params["limit"] = limit

            # Warning about API rate limits
            print("\n⚠️ Important notes:")
            print("• This will make API calls to Bundesanzeiger")
            print("• Rate limiting is built-in to respect API constraints")
            print("• Processing may take several minutes")

            confirm = questionary.confirm(
                "Continue with batch processing?", default=True
            ).ask()

            if not confirm:
                return None

        elif mode == "single":
            company_name = questionary.text(
                "Company name to enrich:", default="Deutsche Bahn AG"
            ).ask()

            if company_name is None:
                return None

            params["company_name"] = company_name

        return params

    def build_command(self, params: Dict[str, Any]) -> list:
        """Build command for Bundesanzeiger enrichment."""
        if params["mode"] == "test":
            command = [sys.executable, "main.py", "enrich-bundesanzeiger", "--test"]
        elif params["mode"] == "batch":
            command = [
                sys.executable,
                "main.py",
                "enrich-bundesanzeiger",
                "--limit",
                params["limit"],
            ]
        else:  # single company
            command = [
                sys.executable,
                "-c",
                f"""
import sys
import os
sys.path.append(os.getcwd())
from scrapers.bundesanzeiger.bundesanzeiger import BundesanzeigerScraper

scraper = BundesanzeigerScraper()
scraper.store_report_data_to_db("{params['company_name']}")
""",
            ]

        return command
