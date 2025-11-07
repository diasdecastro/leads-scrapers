from abc import ABC, abstractmethod
from typing import Dict, Any


class ScraperCLI(ABC):
    """Base class for scraper CLI interfaces."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for the scraper in CLI menu."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the scraper does."""
        pass

    @abstractmethod
    def get_cli_params(self) -> Dict[str, Any]:
        """
        Present questionary prompts to get user input.
        Returns a dictionary with parameter names and values.
        """
        pass

    def execute(self, params: Dict[str, Any] = None) -> bool:
        """Execute the scraper with user-provided parameters."""
        print(f"\nStarting {self.name}...")
        print(f"{self.description}")

        # Get parameters from user if not provided
        if params is None:
            params = self.get_cli_params()
            if params is None:
                print("❌ Operation cancelled.")
                return False

        if hasattr(self, "run_scraper") and callable(getattr(self, "run_scraper")):
            try:
                return self.run_scraper(params)
            except Exception as e:
                print(f"❌ Direct execution failed: {e}")
                return False


# Keep EnricherCLI as an alias for backward compatibility
EnricherCLI = ScraperCLI
