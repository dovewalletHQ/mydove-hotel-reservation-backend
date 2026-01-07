import logging
import sys
import os
import json
from logging.handlers import RotatingFileHandler
from typing import Any, Set, Union

# Define keys that are considered sensitive and should be redacted
SENSITIVE_KEYS: Set[str] = {
    # Personal Identifiers
    "password", "token", "access_token", "refresh_token", "secret", "client_secret",
    "authorization", "api_key", "key", 
    "credit_card", "card_number", "cvv", "expiration_date",
    "ssn", "social_security_number", "national_id", "passport_number", "driver_license",
    
    # Contact Info
    "phone", "phone_number", "mobile", "email", "address", 
    
    # Names
    "first_name", "last_name", "full_name", "name",
    
    # IDs (Context dependent, but generally PII in this context)
    "user_id", "customer_id", "account_number", "routing_number", "pin"
}

class SensitiveDataFormatter(logging.Formatter):
    """
    Custom Formatter that identifies and redacts sensitive data from log records.
    It expects log messages to be dictionaries (for structured logging) or strings.
    If a dictionary is passed or args are dictionaries, they will be traversed and sanitized.
    """
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def _sanitize(self, data: Any) -> Any:
        """
        Recursively sanitizes data.
        """
        if isinstance(data, dict):
            return {
                k: "***REDACTED***" if isinstance(k, str) and k.lower() in SENSITIVE_KEYS else self._sanitize(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._sanitize(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(self._sanitize(item) for item in data)
        return data

    def format(self, record: logging.LogRecord) -> str:
        # 1. Sanitize the main message if it is a dictionary (Structured Log)
        if isinstance(record.msg, (dict, list)):
            record.msg = self._sanitize(record.msg)
            # Convert to JSON string for the final textual log output
            if not isinstance(record.msg, str):
                try:
                    record.msg = json.dumps(record.msg, default=str)
                except Exception:
                    record.msg = str(record.msg)

        # 2. Sanitize arguments if provided (e.g. logger.info("Params: %s", params_dict))
        if record.args:
            # We need to act on a copy or modify carefully because record.args is a tuple or dict
            clean_args = self._sanitize(record.args)
            record.args = clean_args

        return super().format(record)

def setup_logger(
    name: str = "app_logger", 
    log_dir: str = "logs", 
    log_level: int = logging.INFO,
    to_console: bool = True,
    to_file: bool = True
) -> logging.Logger:
    """
    Sets up a secured logger with both console and file handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # If logger already has handlers, assume it's set up to avoid duplicate logs
    if logger.hasHandlers():
        return logger

    # Format that includes timestamp, name, level, and the message
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = SensitiveDataFormatter(log_format)

    # 1. File Handler (Rotating)
    if to_file:
        try:
            # Ensure log directory exists relative to project root (or absolute)
            # Assuming this is run from project root, or we use absolute path.
            # We'll use absolute path based on current file location if needed, 
            # but for now relative 'logs' is standard.
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, "application.log")
            
            file_handler = RotatingFileHandler(
                log_file_path, 
                maxBytes=10*1024*1024, # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to console if file handling fails
            sys.stderr.write(f"Failed to setup file logger: {e}\n")

    # 2. Console Handler
    if to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)

    return logger

# Initialize a default logger instance for easy import
# Usage: from app.core.logger import logger
# logger.info({"user_id": 1, "password": "secure"})
logger = setup_logger()
