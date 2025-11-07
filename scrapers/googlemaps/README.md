# Google Maps Scraper

A powerful scraper for extracting business listings from Google Maps with location-based search capabilities. This scraper provides both command-line interface and REST API for easy integration.

## Overview

The Google Maps scraper extracts comprehensive business information including:
- Company names
- Addresses  
- Phone numbers
- Website URLs
- Geographic location data
- Search metadata

## Features

- **CLI Interface**: Command-line tool for direct scraping
- **REST API**: HTTP endpoints for integration
- **Location-based Search**: Radius-based geographical search
- **Rate Limiting**: Built-in rate limiting to respect server resources
- **Proxy Support**: Optional proxy configuration
- **Stealth Mode**: Browser stealth capabilities to avoid detection
- **Scrolling Support**: Automatic scrolling to load more results

## Installation

```bash
# Install dependencies (from project root)
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage

### Command Line Interface

#### Basic Scraping

```bash
# Basic scraping with defaults
python main.py scrape

# Search for specific business type in a city
python main.py scrape --query "restaurant" --location "berlin" --max-entries 25

# Save results to file
python main.py scrape --query "hotel" --location "munich" --output results.json

# Use custom radius and rate limiting
python main.py scrape --query "cafe" --location "hamburg" --radius-meters 2000 --requests-per-minute 20
```

#### API Server

```bash
# Start API server on default port (8001)
python main.py server

# Start on custom host/port with auto-reload
python main.py server --host 0.0.0.0 --port 8080 --reload
```

### REST API

#### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check |
| `/config` | GET | Get default configuration values |
| `/scrape` | GET | Scrape business listings |

#### API Examples

```bash
# Basic scraping
curl "http://localhost:8001/scrape?query=restaurant&location=berlin&max_entries=15"

# With custom radius and parameters
curl "http://localhost:8001/scrape?query=hotel&location=munich&max_entries=30&radius_meters=2000"

# Health check
curl "http://localhost:8001/health"

# Get configuration
curl "http://localhost:8001/config"
```

## Parameters

### CLI Parameters

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `--query` | `-q` | string | "restaurant" | Search term (business type, service, etc.) |
| `--location` | `-l` | string | "berlin" | City or location to search in |
| `--max-entries` | `-m` | integer | 15 | Maximum number of businesses to scrape |
| `--radius-meters` | `-rad` | integer | 1000 | Search radius in meters |
| `--requests-per-minute` | `-r` | integer | 30 | Rate limiting (requests per minute) |
| `--proxy` | `-p` | string | None | Proxy server URL (optional) |
| `--output` | `-o` | string | None | Output JSON file (prints to console if not specified) |

### API Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `query` | string | "restaurant" | No | Search term |
| `location` | string | "berlin" | No | Location to search |
| `max_entries` | integer | 15 | No | Maximum entries to scrape |
| `radius_meters` | integer | 1000 | No | Search radius in meters |
| `requests_per_minute` | integer | 30 | No | Rate limiting |
| `proxy` | string | None | No | Proxy server URL |

## Output Format

### CLI Output

When using `--output`, results are saved as JSON:

```json
[
  {
    "name": "Restaurant Beispiel",
    "search_query": "restaurant",
    "url": "https://www.beispiel-restaurant.de",
    "address": "Beispielstraße 123, 10115 Berlin",
    "phone": "+49 30 12345678",
    "source": "google.com/maps",
    "official_name": ""
  }
]
```

### API Response

```json
{
  "success": true,
  "scraper": "googlemaps",
  "query": "restaurant",
  "location": "berlin",
  "radius_meters": 1000,
  "total_results": 20,
  "results": [
    {
      "name": "Restaurant Beispiel",
      "search_query": "restaurant",
      "url": "https://www.beispiel-restaurant.de",
      "address": "Beispielstraße 123, 10115 Berlin",
      "phone": "+49 30 12345678",
      "source": "google.com/maps",
      "official_name": ""
    }
  ]
}
```

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Business name as displayed on Google Maps |
| `search_query` | string | The search term used |
| `url` | string | Business website URL (if available) |
| `address` | string | Full business address |
| `phone` | string | Phone number (if available) |
| `source` | string | Always "google.com/maps" |
| `official_name` | string | Official company name (initially empty, can be enriched) |

## Configuration

### Default Settings

```python
DEFAULT_QUERY = "restaurant"
DEFAULT_LOCATION = "berlin"
DEFAULT_RADIUS_METERS = 1000
REQUESTS_PER_MINUTE = 30
```

### Environment Variables

You can override defaults using environment variables:

```bash
export GOOGLEMAPS_QUERY="hotel"
export GOOGLEMAPS_LOCATION="munich"
export GOOGLEMAPS_RADIUS="2000"
export GOOGLEMAPS_RATE_LIMIT="20"
```

## Search Radius

The scraper supports location-based search with configurable radius:

- **Default**: 1000 meters (1km)
- **Range**: 100m to 50,000m (50km)
- **Usage**: Larger radius finds more businesses but may take longer

### Radius Examples

```bash
# Search within 500m
python main.py scrape --query "cafe" --location "berlin" --radius-meters 500

# Search within 5km
python main.py scrape --query "hotel" --location "munich" --radius-meters 5000

# Wide area search (10km)
python main.py scrape --query "restaurant" --location "hamburg" --radius-meters 10000
```

## Rate Limiting

The scraper includes built-in rate limiting to be respectful to Google Maps:

- **Default**: 30 requests per minute
- **Configurable**: Can be adjusted via `--requests-per-minute` parameter
- **Automatic**: Handles delays between requests automatically
- **Conservative**: Google Maps has stricter rate limits than other sources

## Proxy Support

For enhanced anonymity or to bypass restrictions:

```bash
# HTTP proxy
python main.py scrape --proxy "http://proxy.example.com:8080"

# SOCKS proxy  
python main.py scrape --proxy "socks5://proxy.example.com:1080"
```

## Error Handling

The scraper includes comprehensive error handling:

- **Cookie Consent**: Automatic handling of cookie popups
- **Scrolling Issues**: Robust scrolling mechanism to load more results
- **Network Issues**: Automatic retries with exponential backoff
- **Rate Limiting**: Automatic throttling when limits are reached
- **Parsing Errors**: Graceful handling of unexpected page structures

## Advanced Features

### Dynamic Loading

Google Maps loads results dynamically. The scraper:
- Automatically scrolls to load more results
- Waits for new content to appear
- Stops when no new results are found
- Handles infinite scroll pagination

### Geographic Precision

Search results are filtered by:
- Geographic proximity to search location
- Business relevance to search terms
- Google Maps ranking and popularity

## Examples

### Search for Restaurants in Berlin

```bash
python main.py scrape --query "restaurant" --location "berlin" --max-entries 30 --output berlin_restaurants.json
```

### Search for Hotels in Munich via API

```bash
curl "http://localhost:8001/scrape?query=hotel&location=munich&max_entries=25&radius_meters=2000"
```

### Large Area Search with Rate Limiting

```bash
python main.py scrape --query "cafe" --location "hamburg" --radius-meters 5000 --max-entries 50 --requests-per-minute 15
```

### Multiple Location Search Script

```bash
#!/bin/bash
cities=("berlin" "munich" "hamburg" "cologne")
for city in "${cities[@]}"; do
    python main.py scrape --query "restaurant" --location "$city" --output "${city}_restaurants.json"
done
```

## Troubleshooting

### Common Issues

1. **Cookie Popups**: The scraper automatically handles consent dialogs
2. **Limited Results**: Try increasing `--radius-meters` or reducing `--max-entries`
3. **Rate Limiting**: If getting blocked, reduce `--requests-per-minute` value
4. **Geographic Issues**: Ensure location names are in English or local language

### Debugging

Enable verbose logging:

```bash
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python main.py scrape --query "test" --location "berlin"
```

### Performance Tips

1. **Batch Processing**: Use reasonable `max_entries` values (15-50)
2. **Rate Limiting**: Keep `requests_per_minute` at 30 or lower
3. **Radius Optimization**: Start with smaller radius, increase if needed
4. **Proxy Rotation**: Use different proxies for large-scale scraping

## Comparison with Other Sources

| Feature | Google Maps | Gelbeseiten | Other Sources |
|---------|-------------|-------------|---------------|
| Geographic Search | ✅ Excellent | ❌ City-based only | Varies |
| Data Quality | ✅ High | ✅ High | Varies |
| Rate Limits | ⚠️ Strict | ✅ Moderate | Varies |
| Coverage | ✅ Global | 🇩🇪 Germany only | Varies |
| Real-time Data | ✅ Yes | ⚠️ Limited | Varies |

## Dependencies

- `playwright`: Browser automation
- `playwright-stealth`: Stealth capabilities
- `fastapi`: REST API framework
- `uvicorn`: ASGI server
- `beautifulsoup4`: HTML parsing (via scraper dependencies)

## Legal Notice

This tool is for educational and research purposes. Always respect:
- Google Maps' robots.txt and terms of service
- Rate limiting to avoid overloading servers
- Applicable data protection and privacy laws
- Copyright and intellectual property rights

Use responsibly and in accordance with applicable laws and regulations.
