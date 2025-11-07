from datetime import datetime
from typing import Optional
from config.browser import BrowserManager
from .config import GoogleMapsConfig
import logging
import time

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy

    def scrape(
        self,
        query,
        location,
        max_entries=None,
        requests_per_minute=30,
    ):
        results = []
        search_url = f"{GoogleMapsConfig.BASE_URL}/search/{query} {location}/".replace(
            " ", "+"
        )
        logger.info(f"Navigating to: {search_url}")

        with BrowserManager(requests_per_minute, self.proxy) as browser:
            page = browser.get_page()
            logger.info("Opening search URL...")
            page.goto(search_url, timeout=60000)
            # Handle consent popup if present
            try:
                logger.info("Checking for consent popup...")
                consent_btn = page.query_selector(
                    GoogleMapsConfig.SELECTORS["accept_cookies"]
                )
                if consent_btn:
                    logger.info("Consent popup found. Clicking accept.")
                    consent_btn.click()
                    time.sleep(2)
                else:
                    logger.info("No consent popup found.")
            except Exception as e:
                logger.warning(f"Error handling consent popup: {e}")

            logger.info("Waiting for main results container to load...")
            page.wait_for_selector(GoogleMapsConfig.SELECTORS["main"], timeout=15000)

            entries_seen = set()
            scroll_round = 0
            while True:
                cards = page.query_selector_all(GoogleMapsConfig.SELECTORS["card"])
                logger.info(
                    f"Scroll round {scroll_round}: Found {len(cards)} business cards on the page."
                )
                # Take a screenshot for debugging at each scroll round
                # try:
                #     page.screenshot(path=f"debug_gmaps_scroll_{scroll_round}.png")
                #     logger.info(
                #         f"Screenshot saved: debug_gmaps_scroll_{scroll_round}.png"
                #     )
                # except Exception as e:
                #     logger.warning(f"Could not take screenshot: {e}")
                if not cards:
                    logger.warning(
                        "No business cards found. The page structure may have changed or results are empty."
                    )
                for card in cards:
                    href = card.get_attribute("href")
                    if not href or not href.startswith(
                        "https://www.google.com/maps/place/"
                    ):
                        logger.debug("Skipping card with invalid or missing href.")
                        continue
                    # Open the business details in a new tab
                    details_page = page.context.new_page()
                    try:
                        logger.info(
                            f"Opening details page for: {card.get_attribute('aria-label')}"
                        )
                        details_page.goto(href, timeout=20000)
                        details_page.wait_for_selector(
                            GoogleMapsConfig.SELECTORS["main"], timeout=10000
                        )
                        details_main = details_page.query_selector(
                            GoogleMapsConfig.SELECTORS["main"]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to open details page for {href}: {e}")
                        details_page.close()
                        continue

                    # Name from the new details panel
                    name = ""
                    try:
                        name = details_main.get_attribute("aria-label") or ""
                    except Exception as e:
                        logger.warning(f"Could not extract name: {e}")
                        name = ""
                    if not name or name in entries_seen:
                        logger.debug(f"Skipping duplicate or empty name: {name}")
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
                            if address.startswith("Adresse: "):
                                address = address[len("Adresse: ") :]
                            address = address.strip()
                    except Exception as e:
                        logger.warning(f"Could not extract address for {name}: {e}")
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
                    except Exception as e:
                        logger.warning(f"Could not extract phone for {name}: {e}")
                        phone = ""

                    # Website
                    url = ""
                    try:
                        url_elem = details_main.query_selector(
                            GoogleMapsConfig.SELECTORS["website_link"]
                        )
                        if url_elem:
                            url = url_elem.get_attribute("href") or ""
                    except Exception as e:
                        logger.warning(f"Could not extract website for {name}: {e}")
                        url = ""

                    result = {
                        "metadata": {
                            "search_query": query,
                            "datetime": datetime.now().isoformat(),
                        },
                        "company_name": name,
                        "company_website": url or "",
                        "address": address or "",
                        "phone": phone or "",
                        "source": "google.com/maps",
                    }
                    results.append(result)
                    logger.info(f"Scraped: {name} ({address})")
                    entries_seen.add(name)
                    details_page.close()
                    if max_entries and len(results) >= max_entries:
                        logger.info("Reached max_entries limit.")
                        break

                if max_entries and len(results) >= max_entries:
                    logger.info("Reached max_entries limit after scrolling.")
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
                            logger.info(
                                "Scrolling results feed to load more entries..."
                            )
                            page.evaluate(
                                "(el) => { el.scrollBy(0, el.scrollHeight) }", main_div
                            )
                        else:
                            logger.warning("Could not find results feed to scroll.")
                    except Exception as e:
                        logger.warning(f"Error while scrolling results feed: {e}")

                    max_scroll_attempts = 3
                    for attempt in range(max_scroll_attempts):
                        logger.info(
                            f"Scroll attempt {attempt + 1}/{max_scroll_attempts} waiting for new cards..."
                        )
                        time.sleep(2)  # Warte auf Nachladen
                        new_cards = page.query_selector_all(
                            GoogleMapsConfig.SELECTORS["card"]
                        )
                        if len(new_cards) > prev_count:
                            logger.info(
                                f"New cards loaded: {len(new_cards) - prev_count}"
                            )
                            break
                        else:
                            logger.info("No new cards yet...")

                    # Wait for more cards to load
                    new_cards = page.query_selector_all(
                        GoogleMapsConfig.SELECTORS["card"]
                    )
                    logger.info(f"After scrolling: {len(new_cards)} cards found.")
                    # If no new cards loaded or all cards already seen, stop scrolling
                    if len(new_cards) == prev_count:
                        logger.info(
                            "No new cards loaded after multiple scroll attempts. Stopping."
                        )
                        break
                else:
                    logger.info("Max entries reached, stopping scroll.")
                    break

                scroll_round += 1

        logger.info(f"Scraping finished. Total results: {len(results)}")
        return results
