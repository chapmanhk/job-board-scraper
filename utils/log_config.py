import logging
from pathlib import Path
from utils.config import LOGS_DIR # Import shared paths

LOGS_DIR.mkdir(exist_ok=True) # Ensure logs folder exists

def setup_logger(name: str, log_file: str, level=logging.INFO):
    log_path = LOGS_DIR / log_file
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
