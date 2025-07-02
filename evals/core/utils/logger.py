import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "evals",
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting across the codebase.
    
    Args:
        name: Logger name (typically __name__ or module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string. If None, uses default format.
        include_timestamp: Whether to include timestamp in log messages
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers to the same logger
    if logger.handlers:
        return logger
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set up format
    if format_string is None:
        if include_timestamp:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            format_string = '%(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    logger.setLevel(level)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str = "evals") -> logging.Logger:
    """
    Get a logger instance. If not already configured, sets up with default settings.
    
    Args:
        name: Logger name (typically __name__ or module name)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger doesn't have handlers, set it up with defaults
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


def set_log_level(level: int) -> None:
    """
    Set the log level for all evals loggers.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get the root evals logger
    root_logger = logging.getLogger("evals")
    root_logger.setLevel(level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    # Update child loggers
    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith("evals"):
            child_logger = logging.getLogger(logger_name)
            child_logger.setLevel(level)
            for handler in child_logger.handlers:
                handler.setLevel(level)


# Initialize the base logger for the evals package
_base_logger = setup_logger("evals")
