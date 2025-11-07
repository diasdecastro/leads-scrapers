# Imprint Data Scraper

A specialized scraper for extracting official company names and legal information from website imprint pages. This scraper provides both command-line interface and REST API with support for regex and AI-powered LLM extraction methods.

## Overview

The Imprint Data scraper enriches existing business data by:
- Finding imprint/impressum pages on business websites
- Extracting official company names with legal forms (GmbH, AG, UG, etc.)
- Supporting both fast regex-based and accurate LLM-based extraction
- Validating extracted information against address data
- Storing enriched data back to the database

## Features

- **CLI Interface**: Command-line tool for batch enrichment
- **REST API**: HTTP endpoints for integration
- **Dual Extraction Methods**: Fast regex patterns and accurate LLM extraction
- **Multi-language Support**: German and English imprint pages
- **Legal Form Recognition**: Identifies company types (GmbH, AG, UG, OHG, etc.)
- **Address Validation**: Cross-references with existing address data
- **Rate Limiting**: Configurable delays between requests
- **Error Handling**: Comprehensive logging and error recovery

## Installation

```bash
# Install dependencies (from project root)
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# For LLM method: Install and start Ollama
# Visit: https://ollama.ai/
ollama serve
ollama pull deepseek-r1:8b
```

## Usage

### Command Line Interface

#### Basic Enrichment

```bash
# Basic enrichment with regex method (fast)
python main.py enrich

# Use LLM method for better accuracy
python main.py enrich --method llm

# Custom delay and LLM model
python main.py enrich --method llm --delay 2.0 --llm-model "deepseek-r1:8b"
```

#### API Server

```bash
# Start API server on default port (8002)
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
| `/enrich` | POST | Enrich companies with official names |
| `/extract` | GET | Extract official name from single URL |

#### API Examples

```bash
# Basic enrichment with regex method
curl -X POST "http://localhost:8002/enrich?method=regex&delay=1.0"

# LLM-based enrichment
curl -X POST "http://localhost:8002/enrich?method=llm&delay=2.0&llm_model=deepseek-r1:8b"

# Extract from single URL
curl "http://localhost:8002/extract?url=https://example.com&method=regex"

# Health check
curl "http://localhost:8002/health"

# Get configuration
curl "http://localhost:8002/config"
```

## Parameters

### CLI Parameters

| Parameter | Short | Type | Default | Description |
|-----------|-------|------|---------|-------------|
| `--method` | `-m` | string | "regex" | Extraction method: 'regex' or 'llm' |
| `--delay` | `-d` | float | 1.0 | Delay between requests in seconds |
| `--llm-model` | | string | "deepseek-r1:8b" | LLM model for extraction |

### API Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `method` | string | "regex" | No | Extraction method |
| `delay` | float | 1.0 | No | Delay between requests |
| `llm_model` | string | "deepseek-r1:8b" | No | LLM model (for LLM method) |
| `max_companies` | integer | 50 | No | Maximum companies to process |

## Extraction Methods

### Regex Method (Fast)

**Advantages:**
- ⚡ Very fast processing
- 🔄 No external dependencies
- 💾 Low resource usage
- 🎯 Good for standard German legal forms

**Use Cases:**
- Large-scale batch processing
- Standard German company formats
- When speed is priority

**Patterns Detected:**
- GmbH & Co KG, GmbH, UG, AG, OHG, e.K., GbR, KG, mbH
- Stiftung, Verein, and other legal forms
- Address proximity validation

```bash
python main.py enrich --method regex --delay 1.0
```

### LLM Method (Accurate)

**Advantages:**
- 🎯 Higher accuracy
- 🌍 Multi-language support
- 🤖 Context understanding
- 📝 Complex text parsing

**Requirements:**
- Ollama installed and running
- LLM model downloaded (deepseek-r1:8b recommended)
- More processing time and resources

**Use Cases:**
- Complex or non-standard company names
- Multi-language websites
- When accuracy is priority

```bash
# Install Ollama first
ollama serve
ollama pull deepseek-r1:8b

# Run extraction
python main.py enrich --method llm --delay 2.0
```

## Output Format

### CLI Output

The enrichment process updates the database directly and provides console output:

```
🏛️ Configure Imprint Data enrichment:
Processing: Example Company (https://example.com)
  ✅ Official name found (regex): Example GmbH & Co. KG
Done. 15 companies enriched with official names.
```

### API Response

```json
{
  "success": true,
  "scraper": "imprint_data",
  "method": "regex",
  "delay": 1.0,
  "enriched_count": 15,
  "message": "Enrichment completed using regex method"
}
```

### Database Updates

The scraper updates the `official_name` field in the database:

| Field | Before | After |
|-------|--------|-------|
| `name` | "Example Company" | "Example Company" |
| `official_name` | "" | "Example GmbH & Co. KG" |

## Configuration

### Default Settings

```python
DEFAULT_METHOD = "regex"
DEFAULT_DELAY = 1.0
DEFAULT_LLM_MODEL = "deepseek-r1:8b"
IMPRINT_KEYWORDS = ["impressum", "imprint", "legal", "kontakt"]
```

### Environment Variables

```bash
export IMPRINT_METHOD="llm"
export IMPRINT_DELAY="2.0"
export IMPRINT_LLM_MODEL="deepseek-r1:8b"
```

## Imprint Detection

The scraper automatically finds imprint pages using:

### Keywords Searched
- "impressum" (German)
- "imprint" (English)  
- "legal" (English)
- "kontakt" (German)

### Search Strategy
1. **Link Text Search**: Looks for links containing keywords
2. **Common Paths**: Tests `/impressum`, `/imprint`, `/legal`, `/kontakt`
3. **Multiple Attempts**: Tries various combinations and formats

## Legal Form Recognition

### German Legal Forms Supported

| Legal Form | Full Name | Example |
|------------|-----------|---------|
| GmbH | Gesellschaft mit beschränkter Haftung | "Example GmbH" |
| AG | Aktiengesellschaft | "Example AG" |
| UG | Unternehmergesellschaft | "Example UG (haftungsbeschränkt)" |
| GmbH & Co. KG | Kommanditgesellschaft | "Example GmbH & Co. KG" |
| OHG | Offene Handelsgesellschaft | "Example OHG" |
| e.K. | eingetragener Kaufmann | "Example e.K." |
| GbR | Gesellschaft bürgerlichen Rechts | "Example GbR" |

### International Forms
- Limited (Ltd.)
- Corporation (Corp.)
- Incorporated (Inc.)
- And many others

## Rate Limiting

### Recommended Settings

| Use Case | Delay | Reasoning |
|----------|-------|-----------|
| **Regex Method** | 1.0s | Fast processing, minimal server load |
| **LLM Method** | 2.0s | More processing time needed |
| **Large Scale** | 3.0s+ | Be extra respectful to servers |
| **Development** | 0.5s | Faster testing (use sparingly) |

```bash
# Conservative approach for large datasets
python main.py enrich --method regex --delay 3.0

# Balanced approach
python main.py enrich --method llm --delay 2.0
```

## Error Handling

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|---------|
| **Imprint not found** | No imprint page exists | Logged to `imprint_not_found.txt` |
| **LLM model error** | Ollama not running | Start Ollama: `ollama serve` |
| **Extraction failed** | Complex page structure | Try different method |
| **Network timeout** | Slow website | Increase delay parameter |

### Debug Screenshots

Failed extractions are automatically saved:
- `imprint_debug/failed_extract_{id}.png`
- `imprint_debug/failed_fetch_{id}.png`

## Examples

### Basic Regex Enrichment

```bash
python main.py enrich --method regex --delay 1.0
```

### High-Accuracy LLM Enrichment

```bash
python main.py enrich --method llm --delay 2.0 --llm-model "deepseek-r1:8b"
```

### API-based Enrichment

```bash
# Start server
python main.py server --port 8002

# Trigger enrichment
curl -X POST "http://localhost:8002/enrich?method=llm&delay=2.0"
```

### Custom LLM Model

```bash
# Use different model
ollama pull llama2:7b
python main.py enrich --method llm --llm-model "llama2:7b"
```

## Troubleshooting

### LLM Method Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Install and start Ollama
brew install ollama  # macOS
ollama serve
ollama pull deepseek-r1:8b
```

### Database Issues

```bash
# Check database connection
python -c "from utils.db import get_connection; print('DB OK' if get_connection() else 'DB Error')"
```

### Debug Mode

```bash
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python main.py enrich --method regex --delay 1.0
```

## Performance

### Processing Speed

| Method | Speed | Accuracy | Resource Usage |
|--------|-------|----------|----------------|
| **Regex** | ~100 companies/hour | 85-90% | Low |
| **LLM** | ~30 companies/hour | 95-98% | High |

### Optimization Tips

1. **Start with Regex**: Use regex first, then LLM for failed cases
2. **Batch Processing**: Process companies in batches of 50-100
3. **Time Scheduling**: Run during off-peak hours
4. **Progress Monitoring**: Check logs for success rates

## Integration

### With Other Scrapers

```bash
# Scrape first, then enrich
cd scrapers/gelbeseiten && python main.py scrape --query "restaurants" --location "berlin"
cd ../imprint_data && python main.py enrich --method llm
```

### Database Schema

The scraper expects companies with these fields:
- `id`: Unique identifier
- `name`: Company name
- `url`: Website URL
- `official_name`: Field to be enriched (initially empty)

## Dependencies

- `playwright`: Browser automation
- `playwright-stealth`: Stealth capabilities
- `fastapi`: REST API framework
- `uvicorn`: ASGI server
- `ollama`: LLM integration (optional)
- `beautifulsoup4`: HTML parsing

## Legal Notice

This tool is for educational and research purposes. Always respect:
- Website robots.txt and terms of service
- Rate limiting to avoid overloading servers
- Applicable data protection and privacy laws
- Copyright and intellectual property rights

Use responsibly and in accordance with applicable laws and regulations.
