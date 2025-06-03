import requests
import time
import logging
from random import uniform

# Use a named logger configured in log_config.py
logger = logging.getLogger("requests")

def get_with_retry(url, headers=None, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Success: {url}")
            return response
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt} failed for {url}: {e}")
            time.sleep(delay + uniform(0.5, 1.5))
    logger.error(f"Failed after {retries} attempts: {url}")
    return None