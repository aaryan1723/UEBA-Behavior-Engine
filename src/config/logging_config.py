"""
Centralized Logging Configuration

Provides structured logs with function names and line numbers
for faster debugging and traceability.

Author: Aryan Patel
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Log format includes:
    - Timestamp
    - Log Level
    - Module
    - Function
    - Line Number
    - Message
    """

    logger = logging.getLogger(name)

    if not logger.handlers:

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

        logger.setLevel(logging.INFO)

    return logger