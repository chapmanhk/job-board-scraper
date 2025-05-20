# Import libraries
from serpapi import GoogleSearch # Serpapi client to make Google queries
from urllib.parse import urlparse # Breaks URLs into components like domain and path
import re
import os # Used to check for environment variables and file existence
import json # used to save and load the slug list as a .json file
import logging # Create logs for auditing

# Basic log configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(), # Log to console
        logging.FileHandler("logs/discovery.log") # Log to file
    ]
)

# Identifies the source and extracts the first part of the path (company slug)
def extract_company_slug(url):
    parsed = urlparse(url) # Break the URL into parts (host, path, etc.)
    host = parsed.netloc # e.g. jobs.lever.co
    path_parts = parsed.path.strip("/").split("/") # Break /airtable/12345 into ['airtable', '12345']

    if "jobs.lever.co" in host and len(path_parts) >= 2:
        return ("lever", path_parts[0]) # Return the slug 'airtable'
    elif "boards.greenhouse.io" in host and len(path_parts) >= 2:
        return ("greenhouse", path_parts[0])
    return (None, None) # Return nothing if the format doesn't match

# Runs a SerpAPI search for job posts and extracts company slugs
def discover_company_slugs(query, api_key, max_results=100, timeframe="w"):
    params = {
        "engine": "google", # Tell SerpAPI to use Google Search
        "q": query, # Your search term (e.g. 'site:jobs.lever.co')
        "num": max_results, # Up to 100 results per query
        "api_key": api_key,
        "tbs": f"qdr:{timeframe}" # 'qdr:w' = past week, 'qdr:d' = past day
    }

    # Perform the search
    search = GoogleSearch(params)
    results = search.get_dict()

    # Initialize the slug sets (sets are used to automatically remove duplicates)
    slugs = {"lever": set(), "greenhouse": set()}

    # Go through each search result
    for result in results.get("organic_results", []):
        url = result.get("link") # The actual job link
        source, slug = extract_company_slug(url) # Get platform + company
        if source and slug:
            slugs[source].add(slug) # Add it to the right category

    return slugs

# Saves the new slugs, combining them with anything you already saved before
def save_slugs(slugs, filepath="company_slugs.json"):
    if os.path.exists(filepath): # Check if the file already exists
        with open(filepath, "r") as f:
            existing = json.load(f) # If it does, load the existing slugs from the file
    else:
        existing = {"lever": [], "greenhouse": []} # If not, initialize with empty lists for each source

    for source in ["lever", "greenhouse"]: # Loop through both Lever and Greenhouse to update their slug lists
        existing_set = set(existing.get(source, [])) # Looks up existing list of slugs as a set
        new_slugs = slugs[source]

        # Find which slugs are new
        new = new_slugs - existing_set
        if new:
            logging.info(f"New {source.title()} companies discovered: {', '.join(sorted(new))}")
        else:
            logging.info(f"No new {source.title()} companies discovered.")
        updated = existing_set | new_slugs # Merge new slugs with existing ones using a set union (removes duplicates)
        existing[source] = sorted(updated) # Save the sorted list of updated slugs

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2) # Write the updated slug dictionary back to the file
        logging.info(f"Saved {len(existing['lever'])} Lever slugs and {len(existing['greenhouse'])} Greenhouse slugs to {filepath}")


if __name__ == "__main__": # Entry point
    API_KEY = os.environ.get("SERPAPI_KEY") # Get the serpAPI key from the environment variables
    if not API_KEY: 
        logging.error("Missing SERPAPI_KEY. Exiting.")
        raise Exception("Please set your SERPAPI_KEY in environment variables.") # Raise an error if the API key is missing
    
    query = 'site:jobs.lever.co OR site:boards.greenhouse.io' # Define the search query for Lever and Greenhouse job posts
    new_slugs = discover_company_slugs(query, API_KEY, max_results=100, timeframe="w") # Discover new company slugs from the search results
    save_slugs(new_slugs) # Save the updated list of slugs to a JSON file