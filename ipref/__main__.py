# -*- coding: utf-8 -*-


import logging
from logging import Formatter, StreamHandler

from . import __version__
from .lookup import INPUT_TYPES, OUTPUT_FORMATS, run

LOG_FORMAT = "[%(asctime)s]: %(levelname)s: %(name)s: %(message)s"


def setup_logger(level=logging.INFO):
    stream_logger = StreamHandler()
    stream_logger.setLevel(level)
    stream_logger.setFormatter(Formatter(LOG_FORMAT))
    logger = logging.getLogger(__name__.split(".")[0])
    logger.setLevel(level)
    logger.addHandler(stream_logger)


def parse_args():
    import argparse

    # fmt: off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version=__version__, help="show version and exit.")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging to stderr.")
    parser.add_argument("-c", "--config", default=None, help="path to config file.")
    parser.add_argument("-I", "--input-type", default="ip", choices=INPUT_TYPES, help="input type.")
    parser.add_argument("-O", "--output-format", default="json", choices=OUTPUT_FORMATS, help="output format.")
    parser.add_argument("--csv-columns", default=None, help="[csv|tsv] output columns separated by comma (,).")
    parser.add_argument("--csv-exclude-header", action="store_true", help="[csv|tsv] exclude a csv header.")
    parser.add_argument("--csv-escape-comma", action="store_true", help="[csv|tsv] replace commas (,) to <comma> (useful when using commands such as 'cut').")  # noqa: E501
    parser.add_argument("items", type=str, nargs="*", help="IP addresses or filenames. if input_type is file and the items are empty, stdin is used.")  # noqa: E501
    # fmt: on

    return parser.parse_args()


def main():
    args = parse_args()

    if args.debug:
        setup_logger()

    if args.csv_columns:
        csv_columns = args.csv_columns.split(",")
    else:
        csv_columns = None

    run(
        args.items,
        config_file=args.config,
        input_type=args.input_type,
        output_format=args.output_format,
        csv_columns=csv_columns,
        csv_include_header=not args.csv_exclude_header,
        csv_escape_comma=args.csv_escape_comma,
    )
