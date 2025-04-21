class GelbeseitenConfig:
    DEFAULT_QUERY = "friseur"
    DEFAULT_CITY = "berlin"
    DEFAULT_MAX_ENTRIES = 10
    DEFAULT_PROXY = None
    REQUESTS_PER_MINUTE = 30

    SELECTORS = {
        "company_article": "article.mod",
        "company_name": "h2[data-wipe-name='Titel']",
        "company_address": "div.mod-AdresseKompakt__adress-text",
        "company_phone": "a.mod-TelefonnummerKompakt__phoneNumber",
        "company_website": "span.mod-WebseiteKompakt__text",
        "next_page": "a[data-wipe-name='PaginationArrowNext']",
        "load_more": "#mod-LoadMore--button",
    }
