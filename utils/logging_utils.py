import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir="./logs", debug_modules=None):
    """
    Enhance existing logging configuration to add file logging for DEBUG level
    while maintaining existing loggers
    
    Args:
        log_dir: Directory to store log files
        debug_modules: List of module names to set to DEBUG level (e.g., ["train.chartseg"])
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S"
    )
    
    # Create file handler (DEBUG level)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "debug.log"),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Set specific modules to DEBUG level if specified
    if debug_modules:
        for module_name in debug_modules:
            module_logger = logging.getLogger(module_name)
            module_logger.setLevel(logging.DEBUG)
    
    # Get a logger for this function
    setup_logger = logging.getLogger("logging_setup")
    
    # Log the configuration
    setup_logger.info(f"Enhanced logging configured: DEBUG+ logs will also go to {os.path.join(log_dir, 'debug.log')}")
    if debug_modules:
        setup_logger.info(f"DEBUG level enabled for modules: {', '.join(debug_modules)}")