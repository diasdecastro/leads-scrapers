# Lead Scraper

A Python-based web scraping tool that uses Playwright to extract business listings from various business directories. Currently supports scraping from Gelbeseiten.de.

## Features

- Automated web scraping using Playwright
- Rate limiting and request management
- User agent rotation
- Proxy support
- Configurable batch sizes
- JSON output format
- Detailed logging
- Command-line interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lead-scraper.git
cd lead-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The scraper can be run from the command line with various options:

```bash
python main.py --query "friseur" --city "berlin" --max-entries 100 --output "results.json" --proxy "http://your-proxy:8080"
```

Available options:
- `--query`, `-q`: Search term (default from config)
- `--city`, `-c`: City to search in (default from config)
- `--max-entries`, `-m`: Maximum number of entries to fetch (default: all available)
- `--output`, `-o`: Output JSON file path (default: results.json)
- `--proxy`, `-p`: Proxy server to use (default: none)

### Python API

You can also use the scraper in your Python code:

```python
from playwright_scrapers.scrapers.gelbeseiten.scraper import GelbeseitenScraper

# Initialize the scraper
scraper = GelbeseitenScraper(proxy="http://your-proxy:8080")  # proxy is optional

# Run the scraper
results = scraper.scrape(
    query="friseur",
    city="berlin",
    max_entries=100  # optional, will fetch all available if not specified
)

# Process the results
for entry in results:
    print(f"Business: {entry['name']}")
```

## Project Structure

```
lead-scraper/
├── config/
│   ├── browser.py         # Browser management and configuration
│   ├── browser_config.py  # Browser-specific settings
│   └── config.py         # General configuration
├── playwright_scrapers/
│   └── scrapers/
│       └── gelbeseiten/
│           ├── config.py  # Gelbeseiten-specific configuration
│           └── scraper.py # Gelbeseiten scraper implementation
├── main.py               # Command-line interface
└── requirements.txt      # Project dependencies
```

## Configuration

The scraper behavior can be customized through various configuration files:

### Browser Configuration (config/browser_config.py)
- User agents for rotation
- Browser headers
- Viewport settings
- Rate limiting parameters

### Scraper Configuration (playwright_scrapers/scrapers/gelbeseiten/config.py)
- Default search parameters
- Site-specific selectors
- Request settings

## Output Format

The scraper outputs JSON files with the following structure:

```json
[
  {
    "name": "Business Name",
    "id": "unique-identifier",
    "position": 1,
    "industry": "Search Query"
  },
  // ... more entries
]
```

## Error Handling

The scraper includes comprehensive error handling and logging:
- Rate limiting errors
- Network issues
- Parsing failures
- Invalid responses

All errors are logged with appropriate context for debugging.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
