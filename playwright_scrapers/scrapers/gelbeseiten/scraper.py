import json
import logging
import time
import base64
from typing import List, Dict, Optional

from config.browser import BrowserManager
from .config import GelbeseitenConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GelbeseitenScraper:
    """Scraper for Gelbeseiten.de business listings."""

    def __init__(
        self,
        requests_per_minute: int = GelbeseitenConfig.REQUESTS_PER_MINUTE,
        proxy: Optional[str] = None,
    ):
        self.requests_per_minute = requests_per_minute
        self.proxy = proxy

    def scrape(
        self,
        query: str = GelbeseitenConfig.DEFAULT_QUERY,
        city: str = GelbeseitenConfig.DEFAULT_CITY,
        max_entries: Optional[int] = None,
    ) -> List[Dict]:
        """Scrape business listings from Gelbeseiten.de."""
        base_url = "https://www.gelbeseiten.de"
        url = f"{base_url}/{query}/{city}"
        results = []

        with BrowserManager(self.requests_per_minute, self.proxy) as browser:
            page = browser.get_page()

            # Load initial page
            logger.info(f"Loading initial page: {url}")
            page.goto(url)

            # Wait for initial entries and total count element
            logger.info("Waiting for initial entries to load...")
            page.wait_for_selector(GelbeseitenConfig.SELECTORS["company_article"])
            page.wait_for_selector("#loadMoreGesamtzahl")

            # Get initial entries count
            initial_entries = len(
                page.query_selector_all(GelbeseitenConfig.SELECTORS["company_article"])
            )
            logger.info(f"Initial entries loaded: {initial_entries}")

            # Get total available entries from #loadMoreGesamtzahl
            total_count_text = page.evaluate(
                '() => document.querySelector("#loadMoreGesamtzahl").textContent'
            )
            try:
                total_available = int(total_count_text.strip())
                logger.info(f"Total available entries found: {total_available}")

                # If max_entries is None or negative, use total_available
                if max_entries is None or max_entries < 0:
                    max_entries = total_available
                    logger.info(f"Will fetch all {max_entries} available entries")
            except (ValueError, AttributeError) as e:
                logger.error(f"Could not parse total entries count: {e}")
                return results

            # First extract initial entries
            initial_results = self._extract_entries(page)
            results.extend(initial_results)
            logger.info(f"Extracted {len(initial_results)} initial entries")

            # Calculate how many additional entries we need
            remaining_entries = max_entries - initial_entries
            current_position = initial_entries
            ENTRIES_PER_REQUEST = 10  # Gelbeseiten only allows 10 entries per request

            # while remaining_entries > 0:
            #     # Calculate entries to fetch in this batch
            #     batch_size = min(ENTRIES_PER_REQUEST, remaining_entries)

            #     # Prepare form data for the batch request
            #     form_data = {
            #         "umkreis": "-1",
            #         "verwandt": "false",
            #         "WAS": query,
            #         "WO": city,
            #         "position": str(current_position),
            #         "startIndex": str(current_position),
            #         "anzahl": str(batch_size),
            #     }

            #     logger.info(
            #         f"Requesting batch of {batch_size} entries starting from position {current_position}"
            #     )

            #     # Send the POST request and get the response
            #     response = page.evaluate(
            #         """async ([formData, baseUrl]) => {
            #         const response = await fetch(baseUrl + '/ajaxsuche', {
            #             method: 'POST',
            #             headers: {
            #                 'Content-Type': 'application/x-www-form-urlencoded',
            #                 'Accept': 'application/json',
            #                 'X-Requested-With': 'XMLHttpRequest'
            #             },
            #             body: new URLSearchParams(formData)
            #         });
            #         return await response.json();
            #     }""",
            #         [form_data, base_url],
            #     )

            #     if response and "wipePageItemsJson" in response:
            #         try:
            #             # Parse the JSON string containing the entries
            #             new_entries = json.loads(response["wipePageItemsJson"])
            #             logger.info(f"Received {len(new_entries)} new entries")

            #             if len(new_entries) == 0:
            #                 logger.info("No more entries available")
            #                 break

            #             # Process each entry
            #             for entry in new_entries:
            #                 company = {
            #                     "name": entry["na"],
            #                     "id": entry["id"],
            #                     "position": entry["pos"],
            #                     "industry": query.capitalize(),
            #                 }
            #                 results.append(company)
            #                 logger.info(
            #                     f"Processed entry {len(results)}/{max_entries}: {company['name']}"
            #                 )

            #             # Update counters
            #             current_position += len(new_entries)
            #             remaining_entries -= len(new_entries)

            #         except json.JSONDecodeError as e:
            #             logger.error(f"Error parsing JSON response: {e}")
            #             break
            #     else:
            #         logger.error("Invalid response format")
            #         break

            logger.info(f"Finished scraping. Total entries collected: {len(results)}")
            return results

    def _extract_entries(self, page) -> List[Dict]:
        """Extract business entries from the current page."""
        results = []
        entries = page.query_selector_all(
            GelbeseitenConfig.SELECTORS["company_article"]
        )
        total_entries = len(entries)
        logger.info(f"Found {total_entries} entries to process")

        for idx, entry in enumerate(entries, 1):
            try:
                name = entry.query_selector(
                    GelbeseitenConfig.SELECTORS["company_name"]
                ).text_content()

                url_container = entry.query_selector(
                    GelbeseitenConfig.SELECTORS["company_website"]
                )

                if url_container:
                    url_encoded = url_container.get_attribute("data-webseitelink")
                    url_decoded = base64.b64decode(url_encoded).decode("utf-8")
                else:
                    # Some entries may not have a website, handle this case
                    url_decoded = ""

                company = {
                    "name": name.strip(),
                    "position": idx,
                    "industry": page.url.split("/")[-2].capitalize(),
                    "city": page.url.split("/")[-1].capitalize(),
                    "url": url_decoded,
                }
                results.append(company)
                logger.info(f"Processed entry {idx}/{total_entries}: {company['name']}")
            except Exception as e:
                logger.error(f"Error processing entry {idx}/{total_entries}: {e}")

        return results
