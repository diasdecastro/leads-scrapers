import questionary
from typing import List
from config.base_cli import ScraperCLI
from scrapers.gelbeseiten.cli import GelbeseitenCLI
from scrapers.googlemaps.cli import GoogleMapsCLI

# from scrapers.imprint_data.cli import ImprintDataCLI
# from scrapers.bundesanzeiger.cli import BundesanzeigerCLI


def get_available_scrapers() -> List[ScraperCLI]:
    """Return the static list of all available scrapers."""
    return [
        GelbeseitenCLI(),
        GoogleMapsCLI(),
        # ImprintDataCLI(),
        # BundesanzeigerCLI(),
    ]


def main():
    """Main CLI entry point - handles action selection only."""
    print("Scrapers CLI")
    print("=" * 50)

    # Get available scrapers from static list
    scrapers = get_available_scrapers()

    print(f"Available tools ({len(scrapers)}):")
    for scraper in scrapers:
        print(f"   • {scraper.name}: {scraper.description}")

    print("\n")
    # Create choices for questionary
    choices = []
    for scraper in scrapers:
        choices.append(
            questionary.Choice(
                title=f"{scraper.name} - {scraper.description}", value=scraper
            )
        )
    choices.append(questionary.Choice("Exit", "exit"))

    # Let user select action
    selected = questionary.select("\nWhat would you like to do?", choices=choices).ask()

    if selected == "exit" or selected is None:
        print("Goodbye!")
        return

    # Execute the selected scraper
    try:
        selected.execute()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
