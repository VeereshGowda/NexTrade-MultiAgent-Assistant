"""
Centralized logging configuration for the NexTrade Multi-Agent Trading System.

This module provides structured logging with different levels, formatters,
and handlers for development and production environments.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


# Custom JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "agent"):
            log_data["agent"] = record.agent
        if hasattr(record, "tool"):
            log_data["tool"] = record.tool
        
        return json.dumps(log_data)


# Custom console formatter with colors
class ColoredFormatter(logging.Formatter):
    """Format log records with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format: [LEVEL] module.function:line - message
        formatted = (
            f"{color}[{record.levelname}]{self.RESET} "
            f"{record.module}.{record.funcName}:{record.lineno} - "
            f"{record.getMessage()}"
        )
        
        # Add exception traceback if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = False,
    app_name: str = "nextrade"
) -> logging.Logger:
    """
    Set up centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to log to console
        enable_file: Whether to log to file
        enable_json: Whether to use JSON format for file logs
        app_name: Application name for log file naming
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    if enable_file:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
    
    # File handler (rotating)
    if enable_file:
        log_file = os.path.join(log_dir, f"{app_name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        if enable_json:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(module)s.%(funcName)s:%(lineno)d - %(message)s"
                )
            )
        logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors)
    if enable_file:
        error_log_file = os.path.join(log_dir, f"{app_name}_errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        
        if enable_json:
            error_handler.setFormatter(JSONFormatter())
        else:
            error_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(module)s.%(funcName)s:%(lineno)d - %(message)s\n"
                    "%(exc_info)s"
                )
            )
        logger.addHandler(error_handler)
    
    # Set lower log level for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.INFO)
    logging.getLogger("langgraph").setLevel(logging.INFO)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter for adding contextual information.
    
    Usage:
        logger = LoggerAdapter(logging.getLogger(__name__), {"user_id": "user123"})
        logger.info("User action", extra={"action": "place_order"})
    """
    
    def process(self, msg, kwargs):
        """Add extra context to log records."""
        # Merge extra fields
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


# Performance logging decorator
def log_performance(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_performance()
        def my_function():
            pass
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                _logger.info(
                    f"Function '{func.__name__}' executed in {execution_time:.4f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                _logger.error(
                    f"Function '{func.__name__}' failed after {execution_time:.4f}s: {e}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# Exception logging decorator
def log_exceptions(logger: Optional[logging.Logger] = None):
    """
    Decorator to automatically log exceptions.
    
    Usage:
        @log_exceptions()
        def my_function():
            pass
    """
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _logger.error(
                    f"Exception in '{func.__name__}': {e}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    }
                )
                raise
        
        return wrapper
    return decorator


# Initialize default logging configuration
def init_logging():
    """Initialize default logging configuration based on environment."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_dir = os.getenv("LOG_DIR", "logs")
    enable_json = os.getenv("LOG_FORMAT", "text").lower() == "json"
    
    setup_logging(
        log_level=log_level,
        log_dir=log_dir,
        enable_console=True,
        enable_file=True,
        enable_json=enable_json
    )
    
    logger = get_logger(__name__)
    logger.info(
        f"Logging initialized: level={log_level}, format={'JSON' if enable_json else 'text'}"
    )


# Auto-initialize on import
if __name__ != "__main__":
    # Only auto-initialize if not running as main module
    try:
        init_logging()
    except Exception as e:
        # Fallback to basic logging if initialization fails
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.error(f"Failed to initialize advanced logging: {e}")
