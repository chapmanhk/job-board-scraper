import json
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from utils.request_helpers import get_with_retry
from random import uniform

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

if __name__ == "__main__":
    slugs = load_slugs()
    lever_urls = build_lever_urls(slugs["lever"])

    all_jobs = []
    for url in lever_urls:
        print(f"Scraping {url}")
        jobs = fetch_jobs_from_lever(url)
        all_jobs.extend(jobs)
        time.sleep(uniform(1.5, 3.0)) # Random delay between 1.5 to 3 seconds

    print(f"Collected {len(all_jobs)} jobs.")

    # Save to file:
    with open("data/lever_jobs.json", "w") as f:
        json.dump(all_jobs, f, indent=2)