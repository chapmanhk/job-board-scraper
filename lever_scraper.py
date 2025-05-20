from dotenv import load_dotenv
from serpapi import GoogleSearch
import os

load_dotenv()

def serpapi_lever_search(query, api_key, max_results=20, timeframe="w"):
    params = {
        "engine": "google",
        "q": query,
        "num": max_results,
        "api_key": api_key,
        "tbs": f"qdr:{timeframe}"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    links = []
    for result in results.get("organic_results", []):
        url = result.get("link")
        links.append(url)

    return list(set(links))

if __name__ == "__main__":
    query = '("data analyst" OR "analytics engineer" OR "data engineer" OR "data scientist") remote (site:jobs.lever.co OR site:boards.greenhouse.io)'
    serpapi_key = os.environ.get("SERPAPI_KEY")
    links = serpapi_lever_search(query, serpapi_key, max_results=20, timeframe="m")

    print(f"Found {len(links)} Lever job links from the past month:")
    for link in links:
        print(link)