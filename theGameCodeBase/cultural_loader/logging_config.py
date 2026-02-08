# logging_config.py
import logging
import os

def setup_logging(default_level: str = "INFO") -> None:
    """
    Configure logging for the project.

    Reads the LOGLEVEL environment variable (if set) to override the default
    log level. Adjusts the format to include timestamp, level, module name, and message.
    """
    loglevel = os.getenv("LOGLEVEL", default_level).upper()
    logging.basicConfig(
        level=getattr(logging, loglevel, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )
