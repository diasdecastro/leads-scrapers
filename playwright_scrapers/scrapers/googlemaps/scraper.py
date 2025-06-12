from config.browser import BrowserManager
from .config import GoogleMapsConfig
import logging
import time

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    def __init__(self, requests_per_minute=30, proxy=None):
        self.requests_per_minute = requests_per_minute
        self.proxy = proxy

    def scrape(self, query, location, radius_meters=None, max_entries=None):
        results = []
        search_url = self._build_search_url(query, location)
        logger.info(f"Navigating to: {search_url}")

        with BrowserManager(self.requests_per_minute, self.proxy) as browser:
            page = browser.get_page()
            page.goto(search_url, timeout=60000)
            # Handle consent popup if present
            try:
                consent_btn = page.query_selector(
                    GoogleMapsConfig.SELECTORS["accept_cookies"]
                )
                if consent_btn:
                    consent_btn.click()
                    time.sleep(2)
            except Exception:
                pass

            page.wait_for_selector(GoogleMapsConfig.SELECTORS["main"], timeout=15000)

            entries_seen = set()
            while True:
                cards = page.query_selector_all(GoogleMapsConfig.SELECTORS["card"])
                for card in cards:
                    href = card.get_attribute("href")
                    if not href or not href.startswith(
                        "https://www.google.com/maps/place/"
                    ):
                        continue
                    # Open the business details in a new tab
                    details_page = page.context.new_page()
                    try:
                        details_page.goto(href, timeout=20000)
                        details_page.wait_for_selector(
                            GoogleMapsConfig.SELECTORS["main"], timeout=10000
                        )
                        details_main = details_page.query_selector(
                            GoogleMapsConfig.SELECTORS["main"]
                        )
                    except Exception:
                        details_page.close()
                        continue

                    # Name from the new details panel
                    name = ""
                    try:
                        name = details_main.get_attribute("aria-label") or ""
                    except Exception:
                        name = ""
                    if not name or name in entries_seen:
                        details_page.close()
                        continue

                    # Address
                    address = ""
                    try:
                        address_btn = details_main.query_selector(
                            GoogleMapsConfig.SELECTORS["address_btn"]
                        )
                        if address_btn:
                            address = address_btn.get_attribute("aria-label") or ""
                    except Exception:
                        address = ""

                    # Phone
                    phone = ""
                    try:
                        phone_btn = details_main.query_selector(
                            GoogleMapsConfig.SELECTORS["phone_btn"]
                        )
                        if phone_btn:
                            data_item_id = phone_btn.get_attribute("data-item-id")
                            if data_item_id and data_item_id.startswith("phone:tel:"):
                                phone = data_item_id.replace("phone:tel:", "")
                    except Exception:
                        phone = ""

                    # Website
                    url = ""
                    try:
                        url_elem = details_main.query_selector(
                            GoogleMapsConfig.SELECTORS["website_link"]
                        )
                        if url_elem:
                            url = url_elem.get_attribute("href") or ""
                    except Exception:
                        url = ""

                    result = {
                        "name": name,
                        "search_query": query,
                        "url": url or "",
                        "address": address or "",
                        "phone": phone or "",
                        "source": "google.com/maps",
                    }
                    results.append(result)
                    logger.info(f"Scraped: {name} ({address})")
                    entries_seen.add(name)
                    details_page.close()
                    if max_entries and len(results) >= max_entries:
                        break

                if max_entries and len(results) >= max_entries:
                    break

                # Scroll the results container (div[role="feed"]) to load more entries,
                # but only if we haven't reached max_entries yet
                if not max_entries or len(results) < max_entries:
                    prev_count = len(cards)
                    try:
                        main_div = page.query_selector(
                            GoogleMapsConfig.SELECTORS["results_feed"]
                        )
                        if main_div:
                            page.evaluate("(el) => { el.scrollBy(0, 2000); }", main_div)
                    except Exception:
                        pass
                    time.sleep(2)
                    # Wait for more cards to load
                    new_cards = page.query_selector_all(
                        GoogleMapsConfig.SELECTORS["card"]
                    )
                    # If no new cards loaded or all cards already seen, stop scrolling
                    if len(new_cards) <= prev_count or all(
                        (card.get_attribute("aria-label") or "") in entries_seen
                        for card in new_cards
                    ):
                        break
                else:
                    break

        return results

    def _build_search_url(self, query, location):
        q = f"{query} {location}".replace(" ", "+")
        return f"https://www.google.com/maps/search/{q}/"
