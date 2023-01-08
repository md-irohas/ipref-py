# -*- coding: utf-8 -*-

import logging

import click
from flask import Blueprint, Flask, render_template, request
from flask.cli import FlaskGroup

from .__main__ import setup_logger
from .config import Config
from .data.geoip import GeoIPDB
from .lookup import Runner
from .util import get_dot_item, split_data, unixtime_to_datetime

bp = Blueprint("main", __name__)
config = Config()
log = logging.getLogger(__name__)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_prefixed_env()

    if app.config["DEBUG"] or test_config:
        setup_logger()
    if test_config is not None:
        app.config.from_mapping(test_config)

    app.config["IPREF"] = config

    config_file = app.config.get("IPREF_CONF")
    if config_file:
        config.load(config_file)
    if not config.is_loaded():
        app.logger.warning("no config file is loaded. default config is used.")

    app.register_blueprint(bp)

    geoip_db = GeoIPDB.instance()
    geoip_db.setup_dbs(**config["geoip"]["dbs"])

    return app


############################################################################
# Context Processors
############################################################################


def get_header_name(s):
    for data in config["web"]["search"]:
        for item in data["items"]:
            if item["data"] == s:
                return item["label"]

    raise ValueError("invalid 'data' value in web.search: %s" % (s))


def escape_column(s):
    if s is None:
        return "-"
    if isinstance(s, set) or isinstance(s, list):
        return " ".join(s)
    return s


@bp.app_context_processor
def register_context_processor():
    return dict(
        get_dot_item=get_dot_item,
        get_header_name=get_header_name,
        escape_column=escape_column,
    )


############################################################################
# Routes
############################################################################


def columns_in_request():
    return [
        key for key, value in request.form.items() if key != "data" and value == "on"
    ]


def data_in_request():
    return split_data(request.form["data"])


def get_metadata():
    data = {}

    geoip_db = GeoIPDB().instance()
    for k, v in geoip_db.metadata.items():
        if v is None:
            data[k] = None
        else:
            data[k] = unixtime_to_datetime(v.build_epoch).isoformat()

    return data


@bp.route(
    "/search",
    methods=(
        "GET",
        "POST",
    ),
)
def search():
    metadata = get_metadata()
    columns = None
    results = None

    if request.method == "POST":
        columns = columns_in_request()
        data = data_in_request()
        runner = Runner(config)
        results = runner.lookup(data)

    return render_template(
        "search.html", metadata=metadata, columns=columns, results=results
    )


@click.group(cls=FlaskGroup, create_app=create_app)
def run_dev():  # pragma: no cover
    pass
