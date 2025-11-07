class GelbeseitenConfig:
    BASE_URL = "https://www.gelbeseiten.de"

    PROXY = None

    # Input parameters ("Name", "Label")
    INPUT_PARAMS = [
        ("query", "Search term"),
        ("location", "Location"),
        ("max_entries", "Maximum entries"),
        ("requests_per_minute", "Requests per minute"),
    ]

    DEFAULT_VALUES = {
        "query": "friseur",
        "location": "berlin",
        "max_entries": 10,
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
        "company_article": "article.mod",
        "company_name": "h2[data-wipe-name='Titel']",
        "company_address": "div.mod-AdresseKompakt__adress-text",
        "company_phone": "a.mod-TelefonnummerKompakt__phoneNumber",
        "company_website": "span.mod-WebseiteKompakt__text",
        "next_page": "a[data-wipe-name='PaginationArrowNext']",
        "load_more": "#mod-LoadMore--button",
    }
