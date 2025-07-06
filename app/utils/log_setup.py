import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import colorlog


def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    Setup logger with both colored console and file handlers

    Args:
        name: Logger name
        log_dir: Directory to store log files
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        reset=True,
        style="%",
    )

    # File handler - daily rotating file
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/{name}_{today}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console handler with colors
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = setup_logger("my_app")

    # Log some messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # You can also create separate loggers for different modules
    db_logger = setup_logger("my_app.database")
    db_logger.info("Connected to database")
    db_logger.error("Database connection failed")
