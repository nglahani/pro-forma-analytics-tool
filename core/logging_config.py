"""
Logging Configuration

Centralized logging setup for the pro forma analytics tool.
"""

import logging
import logging.handlers
import platform
import sys
from pathlib import Path


def setup_logging(
    name: str = "pro_forma_analytics",
    level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up centralized logging configuration.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        max_bytes: Maximum size per log file
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """

    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    )

    simple_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File handler - use simple FileHandler for Windows to avoid file locking issues
    if platform.system() == "Windows":
        # Use simple FileHandler to avoid Windows file locking issues with rotation
        file_handler = logging.FileHandler(log_path / f"{name}.log", encoding="utf-8")
    else:
        # Use RotatingFileHandler for Unix/Linux systems
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{name}.log", maxBytes=max_bytes, backupCount=backup_count
        )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # Error file handler
    error_handler = logging.FileHandler(log_path / f"{name}_errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        module_name: Name of the module (usually __name__)

    Returns:
        Logger instance
    """
    # Extract just the module name from full path
    if "." in module_name:
        module_name = module_name.split(".")[-1]

    return logging.getLogger(f"pro_forma_analytics.{module_name}")


# Global logger instance
main_logger = setup_logging()
