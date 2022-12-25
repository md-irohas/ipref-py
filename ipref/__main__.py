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
    parser.add_argument("-v", "--version", action="version", version=__version__, help="Show version and exit.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable logging for debug.")
    parser.add_argument("-c", "--config", type=str, default=None, help="")
    parser.add_argument("-I", "--input-type", type=str, default="ip", choices=INPUT_TYPES, help="Input type [ip, file]")
    parser.add_argument("-O", "--output-format", type=str, default="json", choices=OUTPUT_FORMATS, help="Output format [json, jsonl, csv, tsv]")
    parser.add_argument("--csv-columns", type=str, default=None, help="[CSV] CSV columns.")
    parser.add_argument("--csv-exclude-header", action="store_true", help="[CSV] Exclude a header in the CSV results.")
    parser.add_argument("--csv-escape-comma", action="store_true", help="[CSV] Escape commas (,) to <comma>. This is useful when you process the CSV results in commands such as 'cut'.")
    parser.add_argument("items", type=str, nargs="*", help="IP addresses or filenames.")
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
