from fastapi import FastAPI, Query, BackgroundTasks
from playwright_scrapers.scrapers.gelbeseiten.scraper import GelbeseitenScraper
from playwright_scrapers.scrapers.googlemaps.scraper import GoogleMapsScraper
from utils.db import get_all_raw_companies
from apis.bundesanzeiger import BundesanzeigerScraper

app = FastAPI()


@app.get("/scrape/gelbeseiten")
def scrape_gelbeseiten(query: str, location: str, max_entries: int = 10):
    scraper = GelbeseitenScraper()
    results = scraper.scrape(query=query, city=location, max_entries=max_entries)
    return {"results": results}


@app.get("/scrape/googlemaps")
def scrape_googlemaps(query: str, location: str, max_entries: int = 10):
    scraper = GoogleMapsScraper()
    results = scraper.scrape(query=query, location=location, max_entries=max_entries)
    return {"results": results}


@app.get("/companies")
def list_companies():
    return {"companies": get_all_raw_companies()}


@app.post("/enrich/bundesanzeiger")
def enrich_bundesanzeiger(company_name: str):
    scraper = BundesanzeigerScraper()
    scraper.print_jahresabschluss_info(company_name)
    return {"status": "enrichment started"}


# You can add more endpoints for batch enrichment, status, etc.

# To run: uvicorn api_server:app --reload
