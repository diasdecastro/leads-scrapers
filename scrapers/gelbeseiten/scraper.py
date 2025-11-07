from datetime import datetime
import logging
import base64
from typing import List, Dict, Optional

from config.browser import BrowserManager
from .config import GelbeseitenConfig

# TODO: Stop processing further entries once max_entries is reached

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GelbeseitenScraper:
    """Scraper for Gelbeseiten.de business listings."""

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy

    def scrape(
        self,
        query: str = GelbeseitenConfig.DEFAULT_VALUES["query"],
        location: str = GelbeseitenConfig.DEFAULT_VALUES["location"],
        max_entries: Optional[int] = None,
        requests_per_minute=30,
    ) -> List[Dict]:
        """Scrape business listings from Gelbeseiten.de."""
        base_url = GelbeseitenConfig.BASE_URL
        url = f"{base_url}/{query}/{location}"
        results = []

        with BrowserManager(requests_per_minute, self.proxy) as browser:
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

            if max_entries is not None and len(initial_results) > max_entries:
                initial_results = initial_results[:max_entries]
                logger.info(
                    f"Limited initial results to {max_entries} entries as requested"
                )

            results.extend(initial_results)
            logger.info(f"Extracted {len(initial_results)} initial entries")

            # Calculate how many additional entries we need
            remaining_entries = max_entries - len(initial_results)
            current_position = len(initial_results)
            ENTRIES_PER_REQUEST = 10  # Gelbeseiten only allows 10 entries per request

            # Load more entries in batches
            while remaining_entries > 0:
                # Calculate entries to fetch in this batch
                batch_size = min(ENTRIES_PER_REQUEST, remaining_entries)

                # Prepare form data for the batch request
                form_data = {
                    "umkreis": "-1",
                    "verwandt": "false",
                    "WAS": query,
                    "WO": location,
                    "position": str(current_position),
                    "startIndex": str(current_position),
                    "anzahl": str(batch_size),
                }

                logger.info(
                    f"Requesting batch of {batch_size} entries starting from position {current_position}"
                )

                response = self._fetch_ajax_html(page, form_data, base_url)
                if response and "html" in response:
                    try:
                        new_entries = self._extract_entries_from_html(
                            page, response["html"], current_position
                        )
                        logger.info(f"Received {len(new_entries)} new entries")

                        if len(new_entries) == 0:
                            logger.info("No more entries available")
                            break

                        results.extend(new_entries)
                        logger.info(f"Processed entries {len(results)}/{max_entries}")

                        # Update counters
                        current_position += len(new_entries)
                        remaining_entries -= len(new_entries)

                    except Exception as e:
                        logger.error(f"Error processing HTML response: {e}")
                        break
                else:
                    logger.error("Invalid response format")
                    break

            logger.info(f"Finished scraping. Total entries collected: {len(results)}")
            return results

    def _fetch_ajax_html(self, page, form_data, base_url):
        """Send AJAX POST request and return the JSON response."""
        return page.evaluate(
            """async ([formData, baseUrl]) => {
                const response = await fetch(baseUrl + '/ajaxsuche', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new URLSearchParams(formData)
                });
                return await response.json();
            }""",
            [form_data, base_url],
        )

    def _extract_entries_from_html(self, page, html_string, current_position):
        """Extract company entries from AJAX-loaded HTML."""
        entry_html_list = page.evaluate(
            """({html, selector}) => {
                const temp = document.createElement('div');
                temp.innerHTML = html;
                return Array.from(temp.querySelectorAll(selector)).map(e => e.outerHTML);
            }""",
            {
                "html": html_string,
                "selector": GelbeseitenConfig.SELECTORS["company_article"],
            },
        )
        search_query = page.url.split("/")[-2].capitalize()
        location = page.url.split("/")[-1].capitalize()
        return [
            self._extract_company_from_html(
                page, entry_html, idx, current_position, search_query, location
            )
            for idx, entry_html in enumerate(entry_html_list, 1)
        ]

    def _extract_company_from_html(
        self, page, entry_html, idx, current_position, search_query, location
    ):
        """Extract a single company from an HTML string using Playwright JS evaluation."""
        return page.evaluate(
            """(args) => {
                const { entryHtml, idx, currentPosition, search_query, location, selectors } = args;
                const temp = document.createElement('div');
                temp.innerHTML = entryHtml;
                const entry = temp.firstElementChild;
                let name = '';
                let url_decoded = '';
                let address = '';
                let phone = '';
                try {
                    name = entry.querySelector(selectors.company_name).textContent.trim();
                } catch {}
                try {
                    const url_container = entry.querySelector(selectors.company_website);
                    if (url_container) {
                        const url_encoded = url_container.getAttribute('data-webseitelink');
                        url_decoded = url_encoded ? atob(url_encoded) : '';
                    }
                } catch {}
                try {
                    const address_elem = entry.querySelector(selectors.company_address);
                    if (address_elem) {
                        const address_lines = address_elem.textContent.split('\\n').map(l => l.trim()).filter(Boolean);
                        let address_parts = [];
                        if (address_lines.length > 0) {
                            address_parts.push(address_lines[0]);
                        }
                        if (address_lines.length > 1) {
                            const postal_location = address_lines[1].split(',')[0].trim();
                            address_parts.push(postal_location);
                        }
                        address = address_parts.join(', ').replace(',,', ',').replace(', ,', ',').trim();
                    }
                } catch {}
                try {
                    const phone_elem = entry.querySelector(selectors.company_phone);
                    phone = phone_elem ? phone_elem.textContent.trim() : '';
                } catch {}
                return {
                    company_name: name,
                    search_query,
                    url: url_decoded,
                    address,
                    phone,
                    source: "gelbeseiten.de",
                };
            }""",
            {
                "entryHtml": entry_html,
                "idx": idx,
                "currentPosition": current_position,
                "search_query": search_query,
                "location": location,
                "selectors": GelbeseitenConfig.SELECTORS,
            },
        )

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
                    url_decoded = ""

                address_elem = entry.query_selector(
                    GelbeseitenConfig.SELECTORS["company_address"]
                )
                if address_elem:
                    address_lines = [
                        line.strip()
                        for line in address_elem.text_content().splitlines()
                        if line.strip()
                    ]
                    address_parts = []
                    if len(address_lines) > 0:
                        address_parts.append(address_lines[0])
                    if len(address_lines) > 1:
                        postal_location = address_lines[1].split(",")[0].strip()
                        address_parts.append(postal_location)
                    address = ", ".join(address_parts)
                    address = address.replace(",,", ",").replace(", ,", ",").strip()
                else:
                    address = ""

                # Extract phone number
                phone_elem = entry.query_selector(
                    GelbeseitenConfig.SELECTORS["company_phone"]
                )
                phone = phone_elem.text_content().strip() if phone_elem else ""

                company = {
                    "metadata": {
                        "search_query": page.url.split("/")[-2].capitalize(),
                        "datetime": datetime.now().isoformat(),
                    },
                    "company_name": name.strip(),
                    "company_website": url_decoded,
                    "address": address,
                    "phone": phone,
                    "source": "gelbeseiten.de",
                }
                results.append(company)
                logger.info(
                    f"Processed entry {idx}/{total_entries}: {company['company_name']}"
                )
            except Exception as e:
                logger.error(f"Error processing entry {idx}/{total_entries}: {e}")

        return results
