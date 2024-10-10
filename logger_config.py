# logger_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os

class LoggerConfig:
    @staticmethod
    def initialize_logger(logger_name='WellnifyLogger', log_dir='debug_logs', log_file='recommendation_system.log'):
        # Create the logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure TimedRotatingFileHandler to create new log file every day
        log_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, log_file),
            when='midnight',
            interval=1,
            backupCount=30  # Keep logs for 30 days
        )
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Initialize logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)

        return logger
