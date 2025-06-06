# Google Maps-specific configuration (stub)

class GoogleMapsConfig:
    DEFAULT_QUERY = "restaurant"
    DEFAULT_LOCATION = "berlin"
    DEFAULT_RADIUS_METERS = 1000
    REQUESTS_PER_MINUTE = 30

    SELECTORS = {
        "card": 'a[aria-label][href^="https://www.google.com/maps/place/"]',
        "main": 'div[role="main"]',
        "accept_cookies": 'button[aria-label^="Alle akzeptieren"]',
        "address_btn": 'button[data-item-id="address"]',
        "phone_btn": 'button[data-item-id^="phone:tel:"]',
        "website_link": 'a[data-item-id="authority"]',
        "results_feed": 'div[role="feed"]',
    }
