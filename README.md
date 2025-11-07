# Playwright Scrapers Collection

A collection of web scrapers built with Playwright (mostly), featuring scraping tools with a unified CLI interface.

## Overview

This project provides a robust collection of web scrapers powered by Playwright, designed for various data extraction needs. Each scraper is built with stealth capabilities, rate limiting, and browser management features.

## Features

- **CLI Interface**: Easy-to-use command-line interface for running scrapers
- **Stealth Mode**: Built-in stealth capabilities to avoid detection
- **Rate Limiting**: Configurable request rate limiting
- **User Agent Rotation**: Automatic user agent rotation for better anonymity
- **Proxy Support**: Optional proxy configuration
- **Browser Management**: Intelligent browser context management and rotation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd leads-scrapers
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Command Line Interface

The project uses an interactive CLI architecture where each scraper defines its own questionary-based interface:

```bash
# Interactive CLI menu
python cli.py
```

#### CLI Architecture

- **Main CLI (`cli.py`)**: Interactive scraper selection with questionary prompts
- **Scraper-specific CLIs**: Each scraper defines its own parameter collection interface
- **Static Configuration**: All scrapers are explicitly defined in the main CLI
- **Modular Design**: Easy to add new scrapers by updating the static list

### Available Scrapers

| Scraper | Description | Status | Documentation |
|---------|-------------|--------|---------------|
| Gelbeseiten | Scrapes business listings from Gelbeseiten.de | ✅ Active | [README](scrapers/gelbeseiten/README.md) |
| Google Maps | Scrapes business listings from Google Maps | ✅ Active | [README](scrapers/googlemaps/README.md) |
| Imprint Data | Extracts company data from German imprint pages | ⚠️ Outdated | [README](scrapers/imprint_data/README.md) |
| Bundesanzeiger API | Enriches companies with financial data from Bundesanzeiger | ⚠️ Outdated | [README](scrapers/bundesanzeiger/README.md) |
| [Add your scrapers here] | | | |

> **Note**: All scrapers support rate limiting, proxy usage, and stealth features through the unified browser management system.

### Configuration

Configure scraper behavior through environment variables or configuration files:

- `HEADLESS`: Run browser in headless mode (default: True)
- `REQUESTS_PER_MINUTE`: Rate limiting (default: 30)
- `VIEWPORT_WIDTH`: Browser viewport width (default: 1920)
- `VIEWPORT_HEIGHT`: Browser viewport height (default: 1080)

## Architecture

### Core Components

- **BrowserManager**: Handles browser lifecycle, context rotation, and stealth features
- **RateLimiter**: Controls request frequency to avoid being blocked
- **ScraperConfig**: Centralized configuration management
- **CLI**: Command-line interface for easy scraper execution

### Browser Features

- Automatic user agent rotation
- Stealth mode to bypass basic bot detection
- Context refresh at configurable intervals
- Geolocation spoofing (Berlin, Germany)
- Custom headers and locale settings

## Development

### Adding New Scrapers

Follow these steps to add a new scraper, using the Google Maps and Gelbeseiten scrapers as reference examples:

1. **Create the scraper directory structure**:
```
scrapers/[scraper_name]/
├── __init__.py          # Package marker
├── scraper.py           # Main scraping logic
├── config.py            # Scraper configuration
├── cli.py               # CLI interface
├── README.md            # Scraper documentation
└── data/                # Output data directory
```

2. **Implement the core scraper** (`scraper.py`):
   - Create a scraper class that handles data extraction
   - Use the BrowserManager for stealth and browser management
   - Implement proper error handling and logging
   - Return structured data (typically JSON)

3. **Create configuration** (`config.py`):
   - Define INPUT_PARAMS for CLI prompts
   - Set scraper-specific settings
   - Example: `INPUT_PARAMS = [("search_term", "Search term"), ("location", "Location")]`

4. **Implement CLI interface** (`cli.py`):
   - Inherit from `ScraperCLI` from `config.base_cli`
   - Implement required properties: `name`, `description`
   - Implement `get_cli_params()` for user input collection
   - Implement `build_command()` for command generation
   - See `scrapers/googlemaps/cli.py` or `scrapers/gelbeseiten/cli.py` as examples

5. **Add to main CLI**: Import and add your scraper to the static list in `cli.py`

6. **Create documentation**: Add a comprehensive README.md explaining your scraper


### Project Structure

The project follows a modular architecture designed for scalability and maintainability:

```
├── cli.py                  # Main entry point - interactive scraper selection
├── config/                 # Core infrastructure components
│   ├── browser.py          # Browser management, stealth, and rotation
│   ├── config.py           # Global configuration and settings
│   ├── rate_limiter.py     # Request rate limiting
│   └── base_cli.py         # Base classes for CLI interfaces
├── scrapers/               # Individual scraper modules
│   └── [scraper_name]/     # Each scraper has its own directory
│       ├── scraper.py      # Core scraping logic
│       ├── config.py       # Scraper-specific configuration
│       ├── cli.py          # Interactive CLI interface
│       ├── README.md       # Scraper documentation
│       └── data/           # Output data storage
└── utils/                  # Shared utilities
    ├── db.py              # Database operations
    ├── logging.py         # Logging configuration
    └── store_data_json_helper.py  # Data persistence helpers
```

**Key Design Principles**:
- **Modular**: Each scraper is self-contained with its own configuration and CLI
- **Unified Infrastructure**: Shared browser management, rate limiting, and utilities
- **CLI-First**: Interactive questionary-based interfaces for ease of use
- **Extensible**: Simple structure for adding new scrapers

## Requirements

- Python 3.8+
- Playwright
- playwright-stealth
- Additional dependencies in requirements.txt


## Disclaimer

This tool is for educational and research purposes. Always respect robots.txt files and website terms of service. Use responsibly and in accordance with applicable laws and regulations.

## Error Handling

The scraper includes comprehensive error handling and logging:
- Rate limiting errors
- Network issues
- Parsing failures
- Invalid responses

All errors are logged with appropriate context for debugging.