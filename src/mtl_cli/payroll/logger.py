# logger_config.py

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

BASE_DIR = Path(__file__).parent.parent.parent.parent
log_dir = os.path.join(BASE_DIR, 'log')
os.makedirs(log_dir, exist_ok=True)

# File paths
stdout_log_path = os.path.join(log_dir, "stdout.log")
stderr_log_path = os.path.join(log_dir, "stderr.log")
events_log_path = os.path.join(log_dir, "events.log")

# Create the main logger
logger = logging.getLogger("multi_output_logger")
logger.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handlers
stdout_handler = RotatingFileHandler(stdout_log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
stdout_handler.setLevel(logging.INFO)
stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)
stdout_handler.setFormatter(formatter)

stderr_handler = RotatingFileHandler(stderr_log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(formatter)

event_handler = TimedRotatingFileHandler(events_log_path, when="midnight", interval=1, backupCount=7)
event_handler.setLevel(logging.DEBUG)
event_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)
logger.addHandler(event_handler)

# Export logger
__all__ = ['logger']