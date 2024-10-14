import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)

# Create formatters
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create and configure handlers
info_handler = RotatingFileHandler(os.path.join(log_dir, 'info.log'), maxBytes=1024*1024, backupCount=5)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(file_formatter)

warning_handler = RotatingFileHandler(os.path.join(log_dir, 'warning.log'), maxBytes=1024*1024, backupCount=5)
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(file_formatter)

error_handler = RotatingFileHandler(os.path.join(log_dir, 'error.log'), maxBytes=1024*1024, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# Add handlers to root logger
root_logger.addHandler(info_handler)
root_logger.addHandler(warning_handler)
root_logger.addHandler(error_handler)
root_logger.addHandler(console_handler)

# Inhibit aioice and aiohttp logging
logging.getLogger('aioice').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)
logging.getLogger('aiortc').setLevel(logging.ERROR)

def get_logger(name):
    """
    Get a logger with the specified name.
    
    :param name: The name of the logger (usually __name__)
    :return: A configured logger instance
    """
    return logging.getLogger(name)

