import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging() -> None:
    """
    Configures logging to output logs to a file with rotation.
    The log file rotates when it reaches the specified maxBytes,
    keeping a fixed number of backup log files (backupCount).
    """
    log_format = '%(asctime)s / %(name)s / %(funcName)s / %(levelname)s / %(message)s'
    formatter = logging.Formatter(log_format)

    path_logs_save = os.path.join(os.path.dirname(__file__), "app.log")

    # Create a handler that writes logs to a file and rotates when it exceeds 1MB.
    rotating_handler = RotatingFileHandler(
        path_logs_save, maxBytes=1024 * 1024, backupCount=5, encoding='utf-8'
    )
    rotating_handler.setFormatter(formatter)

    # Configure basic logging to include both the rotating file handler and a console handler.
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            rotating_handler,
            logging.StreamHandler()
        ]
    )
