# Lead Scraper

A Python-based web scraping tool that uses Playwright to extract business listings from various business directories. Currently supports scraping from Gelbeseiten.de and Google Maps.

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

The scraper can be run from the command line with various options.  
**You must now specify the source with `--source` or `-s`:**

```bash
python main.py scrape --source gelbeseiten --query "friseur" --location "berlin" --max-entries 400 --output "results_gs.json"
python main.py scrape --source googlemaps --query "GmbH" --location "berlin" --max-entries 15 --radius-meters 1000 --output "results_gm.json"
python main.py enrich-bundesanzeiger --limit 100
```

Available options:
- `scrape`: Scrape business listings (default command)
- `enrich-bundesanzeiger`: Enrich companies in the database with Bundesanzeiger API data
- `--source`, `-s`: Source to scrape from (`gelbeseiten` or `googlemaps`, default: `gelbeseiten`)
- `--query`, `-q`: Search term (default from source config)
- `--location`: Location to search in
- `--radius-meters`: Search radius in meters (Google Maps only, default from config)
- `--max-entries`, `-m`: Maximum number of entries to fetch (default: all available)
- `--output`, `-o`: Output JSON file path (default: results.json)
- `--proxy`, `-p`: Proxy server to use (default: none)
- `--requests-per-minute`, `-r`: Rate limit in requests per minute (default: source-specific)
- `--limit`: (for `enrich-bundesanzeiger`) Number of companies to enrich (default: 50)

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
│       ├── gelbeseiten/
│       │   ├── config.py      # Gelbeseiten-specific configuration
│       │   └── scraper.py     # Gelbeseiten scraper implementation
│       └── googlemaps/
│           ├── config.py      # Google Maps-specific configuration
│           └── scraper.py     # Google Maps scraper implementation
├── main.py                   # Command-line interface
└── requirements.txt          # Project dependencies
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

## Upcoming: Google Maps Scraper

We are planning to add a Google Maps scraper alongside the existing Gelbeseiten scraper. This will involve:

- Adding a new scraper under `playwright_scrapers/scrapers/googlemaps/`.
- Supporting Google Maps-specific configuration and arguments.
- Updating `main.py` to allow selecting which scraper to use (e.g., via a `--source` argument).
- Each scraper may require different CLI arguments (e.g., Google Maps may need API keys, radius, etc.).

**Note:** The CLI interface will be updated to support multiple sources and their specific parameters in a user-friendly way.

# Interessante Queries
| Branche                       | Begründung                                         |
| ----------------------------- | -------------------------------------------------- |
| **Steuerberater**             | oft mehrere Angestellte, gut verdienend            |
| **Hausverwaltungen**          | viele Objekte = hoher Umsatz                       |
| **Pflegedienste**             | Personalintensiv, oft >20 MA                       |
| **Physiotherapie-Zentren**    | >10 MA häufig bei großen Praxen                    |
| **Autohäuser & Werkstätten**  | ab 2 Hebebühnen meist >10 MA                       |
| **Bauunternehmen**            | Umsatz meist >2 Mio bei >3 Baustellen gleichzeitig |
| **Sanitär & Heizung**         | viele Installateure = viele MA                     |
| **Rechtsanwälte (Kanzleien)** | große Kanzleien mit mehreren Anwälten              |
| **Logistik / Speditionen**    | fast immer mittelständisch                         |
| **IT-Systemhäuser**           | Software, Netzwerke, Wartung = >10 MA üblich       |
| **Maschinenbau / Produktion** | hohe Fixkosten → hoher Umsatz                      |

## Enrichment with Bundesanzeiger API

You can enrich your scraped company data with official information from the Bundesanzeiger using:

```bash
python main.py enrich-bundesanzeiger --limit 100
```

This will attempt to match and enrich up to 100 companies in your database with data such as revenue, employee count, and more, using the Bundesanzeiger API.
