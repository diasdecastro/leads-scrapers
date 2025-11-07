# Gelbeseiten Scraper

Technical documentation for the Gelbeseiten.de business directory scraper.

## Overview

Extracts business listings from Gelbeseiten.de (German Yellow Pages) with support for pagination and rate limiting. Built with Playwright for JavaScript-heavy sites.

## Usage

### CLI Interface

```bash
# From project root
python cli.py
# Select "Gelbeseiten Scraper" and follow prompts
```

### Direct Import

```python
from scrapers.gelbeseiten.scraper import GelbeseitenScraper

scraper = GelbeseitenScraper(requests_per_minute=30)
results = scraper.scrape(
    query="friseur",
    location="berlin", 
    max_entries=50
)
```

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | "friseur" | Search term (business type, service) |
| `location` | string | "berlin" | City or location |
| `max_entries` | integer | 10 | Maximum entries to scrape |
| `requests_per_minute` | integer | 30 | Rate limiting |

## Output Format

Returns `List[Dict]` with following structure:

```python
[
    {
        "metadata": {
            "search_query": "friseur",
            "location": "berlin",
            "datetime": "2024-11-07T14:30:22.123456"
        },
        "company_name": "Friseursalon Beispiel",
        "company_website": "https://www.beispiel-friseur.de",
        "address": "Beispielstraße 123, 10115 Berlin",
        "phone": "+49 30 12345678",
        "source": "gelbeseiten.de"
    }
]
```