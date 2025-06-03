import logging
import os
def setup_logger(name, log_file, level=logging.INFO)
    """Set up and return a logger that writes to a specific file."""
    os.makedirs("logs", exist_ok=True)
    filepath = os.path.join("logs", log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        handler = logging.FileHandler(filepath)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
