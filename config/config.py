from typing import Dict, Optional


class ScraperConfig:
    # General settings
    DEFAULT_TIMEOUT = 30000  # milliseconds
    SELECTOR_TIMEOUT = 10000  # milliseconds
    RETRY_DELAY = 60  # seconds

    # Rate limiting
    DEFAULT_REQUESTS_PER_MINUTE = 30

    # Delays
    MIN_DELAY = 2  # seconds
    MAX_DELAY = 5  # seconds

    # Browser settings
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    HEADLESS = True  # Set to False to see the browser window

    # Context management
    CONTEXT_REFRESH_INTERVAL = 5  # Create new context every N requests
    CLEAR_COOKIES_ON_REFRESH = True  # Whether to clear cookies when refreshing context

    DEFAULT_PROXY: Optional[str] = None

    # Common user agents to rotate through
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    ]

    # Common browser headers
    BROWSER_HEADERS: Dict[str, str] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
