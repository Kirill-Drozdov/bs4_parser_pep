import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    DT_FORMAT,
    LOG_FORMAT,
    LOG_DIR,
    LOG_FILE,
    PARSER_DESCRIPTION,
    PARSER_MODE_HELP,
    PARSER_CLEAR_HELP,
    PARSER_OUTPUT_HELP
)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(
        description=PARSER_DESCRIPTION
    )
    parser.add_argument(
        'mode',
        choices=available_modes,
        help=PARSER_MODE_HELP
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help=PARSER_CLEAR_HELP
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help=PARSER_OUTPUT_HELP
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
