import json
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from utils.request_helpers import get_with_retry
from random import uniform
from utils import log_config
import logging

# ----------------------------------
# Setup logger
# ----------------------------------
logger = logging.getLogger("scraper")


# Read company slugs

def load_slugs(filepath="data/company_slugs.json"):
    with open(filepath, "r") as f:
        return json.load(f)

# Build base URLs

def build_lever_urls(slugs):
    return [f"https://jobs.lever.co/{slug}" for slug in slugs]

def build_greenhouse_urls(slugs):
    return [f"https://boards.greenhouse.io/{slug}" for slug in slugs]

# Send requests and parse HTML

def fetch_jobs_from_lever(company_url):
    response = get_with_retry(company_url)
    if not response:
        logger.warning(f"Failed to fetch jobs from {company_url}") 
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for posting in soup.select("div.posting"):
        title = posting.select_one("h5")
        location = posting.select_one("span.sort-by-location")
        url = posting.find("a", href=True)

        if title and url:
            jobs.append({
                "title": title.text.strip(),
                "location": location.text.strip() if location else "",
                "url": f"{url['href']}",
                "source": "lever"
            })

    return jobs

def load_existing_jobs(filepath):
    if Path(filepath).exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return []

DATA_KEYWORDS = [
    "data", "analytics", "analyst", "business intelligence", "bi", "machine learning", "ml", "ai", "artificial intelligence", \
    "forecasting", "nlp", "computer vision", "modeling", "natural language processing", "scientist", "etl", "visualization"
]

def is_data_role(title):
    title = title.lower()
    return any(kw in title for kw in DATA_KEYWORDS)

if __name__ == "__main__":
    slugs = load_slugs()
    lever_urls = build_lever_urls(slugs["lever"])

    existing_jobs = load_existing_jobs("data/lever_jobs.json")
    existing_urls = {job["url"] for job in existing_jobs}
    
    all_jobs = existing_jobs.copy()

    for url in lever_urls:
        logger.info(f"Scraping {url}")
        jobs = fetch_jobs_from_lever(url)
        new_jobs = [
            job for job in jobs
            if job["url"] not in existing_urls and is_data_role(job["title"])
        ]
        all_jobs.extend(new_jobs)
        time.sleep(uniform(1.5, 3.0)) # Random delay between 1.5 to 3 seconds

    logger.info(f"Collected {len(all_jobs)} total jobs.")

    # Save to file:
    with open("data/lever_jobs.json", "w") as f:
        json.dump(all_jobs, f, indent=2)