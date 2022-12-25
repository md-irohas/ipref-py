# -*- coding: utf-8 -*-


import logging
from logging import Formatter, StreamHandler

from . import __version__
from .lookup import INPUT_TYPES, OUTPUT_FORMATS, run

LOG_FORMAT = "[%(asctime)s]: %(levelname)s: %(module)s: %(message)s"


def parse_args():
    import argparse

    # fmt: off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version=__version__, help="show version and exit.")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging to stderr.")
    parser.add_argument("-c", "--config", default=None, help="path to config file.")
    parser.add_argument("-I", "--input-type", default="ip", choices=INPUT_TYPES, help="input type.")
    parser.add_argument("-O", "--output-format", default="json", choices=OUTPUT_FORMATS, help="output format.")
    parser.add_argument("--csv-columns", default=None, help="[csv] CSV columns separated by comma (,).")
    parser.add_argument("--csv-exclude-header", action="store_true", help="[csv] exclude a csv header.")
    parser.add_argument("--csv-escape-comma", action="store_true", help="[csv] escape commas (,) to <comma> (useful when using commands such as 'cut').")
    parser.add_argument("items", type=str, nargs="*", help="IP addresses or filenames. if input_type is file and the items are empty, stdin is used.")
    # fmt: on

    return parser.parse_args()


def setup_logger():
    stream_logger = StreamHandler()
    stream_logger.setLevel(logging.DEBUG)
    stream_logger.setFormatter(Formatter(LOG_FORMAT))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_logger)


def main():
    args = parse_args()

    if args.debug:
        setup_logger()

    run(
        args.items,
        config_file=args.config,
        input_type=args.input_type,
        output_format=args.output_format,
        csv_columns=args.csv_columns,
        csv_include_header=not args.csv_exclude_header,
        csv_escape_comma=args.csv_escape_comma,
    )
