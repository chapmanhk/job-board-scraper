# Import libraries
from serpapi import GoogleSearch # Serpapi client to make Google queries
from urllib.parse import urlparse # Breaks URLs into components like domain and path
import os # Used to check for environment variables and file existence
import json # used to save and load the slug list as a .json file
from utils.log_config import setup_logger
from utils.config import DATA_DIR


# ------------------------------------
# Logger Setup
# ------------------------------------
logger = setup_logger("discovery", "discovery.log")

# ------------------------------------
# Extract company slug from URL
# ------------------------------------
def extract_company_slug(url):
    parsed = urlparse(url) # Break the URL into parts (host, path, etc.)
    host = parsed.netloc # e.g. jobs.lever.co
    path_parts = parsed.path.strip("/").split("/") # Break /airtable/12345 into ['airtable', '12345']

    if "jobs.lever.co" in host and len(path_parts) >= 2:
        return ("lever", path_parts[0]) # Return the slug 'airtable'
    elif "boards.greenhouse.io" in host and len(path_parts) >= 2:
        return ("greenhouse", path_parts[0])
    return (None, None) # Return nothing if the format doesn't match

# ------------------------------------
# Run a single platform query
# ------------------------------------
def run_slug_query(source, query, api_key, max_results=100, timeframe="w"):
    params = {
        "engine": "google",
        "q": query,
        "num": max_results,
        "api_key": api_key,
        "tbs": f"qdr:{timeframe}" # time filter
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    slugs = set()
    for result in results.get("organic_results", []):
        url = result.get("link")
        parsed_source, slug = extract_company_slug(url)
        if parsed_source == source and slug:
            slugs.add(slug)

    logger.info(f"{source.title()} query returned {len(slugs)} unique slugs.")
    return slugs
'''
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
'''
# ------------------------------------
# Save slugs to a JSON file
# ------------------------------------
# Saves the new slugs, combining them with anything you already saved before
def save_slugs(slugs, filepath=DATA_DIR / "company_slugs.json"):
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
            logger.info(f"New {source.title()} companies discovered: {', '.join(sorted(new))}")
        else:
            logger.info(f"No new {source.title()} companies discovered.")
        updated = existing_set | new_slugs # Merge new slugs with existing ones using a set union (removes duplicates)
        existing[source] = sorted(updated) # Save the sorted list of updated slugs

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2) # Write the updated slug dictionary back to the file
        logger.info(f"Saved {len(existing['lever'])} Lever slugs and {len(existing['greenhouse'])} Greenhouse slugs to {filepath}")

# ------------------------------------
# Main execution block
# ------------------------------------
if __name__ == "__main__": # Entry point
    API_KEY = os.environ.get("SERPAPI_KEY") # Get the serpAPI key from the environment variables
    if not API_KEY: 
        logger.error("Missing SERPAPI_KEY. Exiting.")
        raise Exception("Please set your SERPAPI_KEY in environment variables.") # Raise an error if the API key is missing
    
    slugs = {
        "lever": run_slug_query("lever", "site:jobs.lever.co", API_KEY),
        "greenhouse": run_slug_query("greenhouse", "site:boards.greenhouse.io", API_KEY)
    }
    save_slugs(slugs) # Save the updated list of slugs to a JSON file