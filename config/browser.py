from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import logging
import random
from typing import Optional

from .config import ScraperConfig
from .rate_limiter import RateLimiter

# Add stealth import
from playwright_stealth import stealth_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages Playwright browser with rate limiting and user agent rotation."""

    def __init__(
        self,
        requests_per_minute: int = ScraperConfig.DEFAULT_REQUESTS_PER_MINUTE,
        proxy: Optional[str] = None,
    ):
        self.proxy = proxy
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=ScraperConfig.HEADLESS)
        self.context = None
        self.page = None
        self.request_count = 0

    def _create_context(self) -> BrowserContext:
        """Create a new browser context with rotated user agent and stealth."""
        user_agent = random.choice(ScraperConfig.USER_AGENTS)
        context = self.browser.new_context(
            user_agent=user_agent,
            viewport={
                "width": ScraperConfig.VIEWPORT_WIDTH,
                "height": ScraperConfig.VIEWPORT_HEIGHT,
            },
            proxy=self.proxy,
            extra_http_headers=ScraperConfig.BROWSER_HEADERS,
            locale="de-DE",
            geolocation={"longitude": 13.4050, "latitude": 52.5200},  # Berlin
            permissions=["geolocation"],
        )
        logger.info(f"Created new context with user agent: {user_agent}")
        # Apply stealth to the context's page
        page = context.new_page()
        stealth_sync(page)
        # Close the page after applying stealth, will be reopened in get_page
        page.close()
        return context

    def get_page(self) -> Page:
        """Get or create a page, rotating context if needed."""
        self.request_count += 1

        # Check if we need to refresh the context
        if (
            self.context is None
            or self.page is None
            or self.request_count % ScraperConfig.CONTEXT_REFRESH_INTERVAL == 0
        ):

            # Close existing context if any
            if self.context:
                self.context.close()

            # Create new context and page
            self.context = self._create_context()
            self.page = self.context.new_page()

        # Apply rate limiting
        self.rate_limiter.wait()
        return self.page

    def close(self):
        """Clean up resources."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
