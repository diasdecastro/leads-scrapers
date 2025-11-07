class GoogleMapsConfig:
    BASE_URL = "https://www.google.com/maps"

    PROXY = None

    INPUT_PARAMS = [
        ("query", "Search term"),
        ("location", "Location"),
        ("max_entries", "Maximum entries"),
        ("requests_per_minute", "Requests per minute"),
    ]

    DEFAULT_VALUES = {
        "query": "restaurant",
        "location": "berlin",
        "max_entries": 30,
        "requests_per_minute": 30,
    }

    OUTPUT_FIELDS = [
        "metadata",
        "company_name",
        "address",
        "phone",
        "company_website",
    ]

    SELECTORS = {
        "card": 'a[aria-label][href^="https://www.google.com/maps/place/"]',
        "main": 'div[role="main"]',
        "accept_cookies": 'button[aria-label^="Alle akzeptieren"]',
        "address_btn": 'button[data-item-id="address"]',
        "phone_btn": 'button[data-item-id^="phone:tel:"]',
        "website_link": 'a[data-item-id="authority"]',
        "results_feed": 'div[role="feed"]',
    }
