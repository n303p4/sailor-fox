"""Helper functions for sailor-fox."""

import logging


def create_logger(name: str):
    """Create a logger object."""
    logging.basicConfig(format="%(asctime)-12s %(levelname)s %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


def get_prefix(text: str, prefix: str):
    """
    If a string starts with prefix, return prefix and the text minus the first instance of prefix;
    otherwise return None and the text.
    """
    if text.startswith(prefix):
        return prefix, text[len(prefix):].lstrip()
    return None, text


def to_one_liner(text: str, max_length: int = 75):
    """Truncates a string to a single line for logging"""
    one_liner = " ".join(text.split("\n"))
    if len(one_liner) > max_length:
        one_liner = f"{one_liner[:max_length-1]}…"
    if not one_liner:
        one_liner = "<empty>"
    return one_liner
