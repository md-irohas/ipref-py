# -*- coding: utf-8 -*-

import io
import logging

import click
import flag
from flask import (
    Blueprint,
    Flask,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.cli import FlaskGroup

from .__main__ import setup_logger
from .config import Config
from .data.dns import get_nameservers, set_nameservers
from .data.geoip import GeoIPDB
from .lookup import Runner
from .util import get_dot_item, is_in, split_data, unixtime_to_datetime

bp = Blueprint("main", __name__)
apiv1_bp = Blueprint("apiv1", __name__, url_prefix="/api/v1")
config = Config()
log = logging.getLogger(__name__)


def create_app(debug=False, test_config=None):
    app = Flask(__name__)

    if debug or app.config["DEBUG"]:  # pragma: no cover
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
    app.register_blueprint(apiv1_bp)

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
        key
        for key, value in request.form.items()
        if key != "data" and not key.startswith("misc.") and value == "on"
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
        results = runner.lookup(
            data, skip_dns_lookup_reverse_name=skip_dns_lookup_reverse_name
        )

    return render_template(
        "search.html", metadata=metadata, columns=columns, results=results
    )


############################################################################
# API (v1)
############################################################################


def apiv1_columns():
    if "columns" in request.form:
        columns = request.form["columns"].split(",")
        columns = map(lambda x: x.strip(), columns)
        return list(columns)
    else:
        columns = []
        for category in config["web"]["search"]:
            for item in category["items"]:
                if item["data"].startswith("misc."):
                    continue
                if item["checked"]:
                    columns.append(item["data"])
        return columns


def apiv1_data_in_request():
    # NOTE: The read data is a bytes object.
    return split_data(request.files["data"].read().decode("utf-8"))


def apiv1_render_as_csv(
    columns, data, skip_dns_lookup_reverse_name, include_header, escape_comma
):
    runner = Runner(config)
    results = runner.lookup(
        data, skip_dns_lookup_reverse_name=skip_dns_lookup_reverse_name
    )

    buffer = io.StringIO()
    runner.dump_as_csv(
        results,
        fp=buffer,
        columns=columns,
        include_header=include_header,
        escape_comma=escape_comma,
    )

    resp = make_response(buffer.getvalue(), 200)
    resp.mimetype = "text/csv"
    return resp


@apiv1_bp.route("/search", methods=("POST",))
def apiv1_search():
    columns = apiv1_columns()
    data = apiv1_data_in_request()
    output_format = request.args.get("format", "csv")
    skip_dns_lookup_reverse_name = not is_in("dns.reverse_name", columns)
    csv_include_header = False if int(request.args.get("csv_noheader", 0)) else True
    csv_escape_comma = True if int(request.args.get("csv_nocomma", 0)) else False

    if output_format == "csv":
        return apiv1_render_as_csv(
            columns,
            data,
            skip_dns_lookup_reverse_name=skip_dns_lookup_reverse_name,
            include_header=csv_include_header,
            escape_comma=csv_escape_comma,
        )
    else:
        abort(400)


############################################################################
# Run
############################################################################


@click.group(cls=FlaskGroup, create_app=create_app)
def run_dev():  # pragma: no cover
    pass
