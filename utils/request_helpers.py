import requests
import time
import logging
import os
from random import uniform

# Setup logger specifically for request activity
log_path = os.path.join("logs", "requests.log")
logging.basicConfig(
    filename=log_path,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def get_with_retry(url, headers=None, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logging.info(f"Success: {url}")
            return response
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt} failed for {url}: {e}")
            time.sleep(delay)
    logging.error(f"Failed after {retries} attempts: {url}")
    return None