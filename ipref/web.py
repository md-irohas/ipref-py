# -*- coding: utf-8 -*-

import logging

import click
import flag
from flask import Blueprint, Flask, render_template, request, redirect, url_for
from flask.cli import FlaskGroup

from .__main__ import setup_logger
from .config import Config
from .data.dns import get_nameservers, set_nameservers
from .data.geoip import GeoIPDB
from .lookup import Runner
from .util import get_dot_item, split_data, unixtime_to_datetime, is_in

bp = Blueprint("main", __name__)
config = Config()
log = logging.getLogger(__name__)


def create_app(debug=False, test_config=None):
    app = Flask(__name__)

    if debug or app.config["DEBUG"]:    # pragma: no cover
        setup_logger()
    if test_config is not None:
        app.config.from_mapping(test_config)

    app.config["IPREF"] = config

    config.load()
    if not config.is_loaded():
        app.logger.warning("no config file is loaded. the default config is used.")

    nameservers = config["dns"]["reverse_name"]["nameservers"]
    if nameservers:
        set_nameservers(nameservers)
        log.info("Set nameservers: %s", get_nameservers())
    else:
        log.info("The default nameservers are used: %s", get_nameservers())

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


def make_flag(cc):
    if cc is None:
        return ""
    return flag.flag(cc)


@bp.app_context_processor
def register_context_processor():
    return dict(
        get_dot_item=get_dot_item,
        get_header_name=get_header_name,
        escape_column=escape_column,
        make_flag=make_flag,
    )


############################################################################
# Routes
############################################################################


def columns_in_request():
    return [
        key for key, value in request.form.items() if key != "data" and not key.startswith("misc.") and value == "on"
    ]


def data_in_request():
    return split_data(request.form["data"])


def get_metadata():
    data = {}

    # DNS
    if config["dns"]["reverse_name"]["enabled"]:
        data["nameservers"] = ", ".join(get_nameservers())

    # GeoIP
    geoip_db = GeoIPDB().instance()
    for k, v in geoip_db.metadata.items():
        data[k] = unixtime_to_datetime(v.build_epoch).isoformat()

    return data


@bp.route("/")
def index():
    return redirect(url_for("main.search"))


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
        skip_dns_lookup_reverse_name = not is_in("dns.reverse_name", columns)
        runner = Runner(config)
        results = runner.lookup(data, skip_dns_lookup_reverse_name=skip_dns_lookup_reverse_name)

    return render_template(
        "search.html", metadata=metadata, columns=columns, results=results
    )


@click.group(cls=FlaskGroup, create_app=create_app)
def run_dev():  # pragma: no cover
    pass
