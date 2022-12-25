# -*- coding: utf-8 -*-


import csv
import ipaddress
import json
import sys
from types import SimpleNamespace

from . import __version__
from .config import Config
from .data.dns import dns_reverse_lookups
from .data.geoip import GeoIPDB
from .util import get_dot_item, ip_address_types, is_ip_address, split_data

INPUT_TYPES = {"ip", "file"}
OUTPUT_FORMATS = {"json", "jsonl", "csv"}


def is_valid_input_type(s):
    return s in INPUT_TYPES


def is_valid_output_format(s):
    return s in OUTPUT_FORMATS


def _get_geoip_raw_data(record):
    if record:
        return record.raw
    else:
        return None


class Result:
    def __init__(self, raw_input):
        # Meta data
        self.meta = SimpleNamespace()
        self.meta.raw_input = raw_input
        try:
            self.meta.ip_address = ipaddress.ip_address(raw_input)
        except ValueError:
            self.meta.ip_address = None
        self.meta.ip_address_types = ip_address_types(self.meta.ip_address)

        # DNS data
        self.dns = SimpleNamespace()
        self.dns.reverse_name = None

        # GeoIP
        self.geoip = SimpleNamespace()
        self.geoip.city = None
        self.geoip.anonymous_ip = None
        self.geoip.asn = None
        self.geoip.connection_type = None
        self.geoip.domain = None
        self.geoip.enterprise = None
        self.geoip.isp = None

    @property
    def ip(self):
        return self.meta.ip_address

    def __getitem__(self, key):
        return get_dot_item(self, key)

    def to_dict(self):
        return {
            "meta": {
                "version": "ipref-" + __version__,
                "ip_address": self.meta.ip_address,
                "ip_address_types": self.meta.ip_address_types,
            },
            "geoip": {
                "city": _get_geoip_raw_data(self.geoip.city),
                "anonymous_ip": _get_geoip_raw_data(self.geoip.anonymous_ip),
                "asn": _get_geoip_raw_data(self.geoip.asn),
                "connection_type": _get_geoip_raw_data(self.geoip.connection_type),
                "domain": _get_geoip_raw_data(self.geoip.domain),
                "enterprise": _get_geoip_raw_data(self.geoip.enterprise),
                "isp": _get_geoip_raw_data(self.geoip.isp),
            },
        }


class ResultJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Result):
            return obj.to_dict()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, ipaddress.IPv4Address):
            return str(obj)
        if isinstance(obj, ipaddress.IPv6Address):
            return str(obj)
        # NOTE: This will raise TypeError.
        return json.JSONEncoder.default(self, obj)


def escape_csv_column(col, escape_comma=False):
    if isinstance(col, set) or isinstance(col, list):
        col = " ".join(col)

    if escape_comma:
        if isinstance(col, str):
            col = col.replace(",", "<comma>")

    return col


class Runner:
    def __init__(self, config):
        self.config = config

    def _init_results(self, ips):
        return [Result(ip) for ip in ips]

    def _lookup_dns(self, results):
        dns_config = self.config["dns"]
        if not dns_config["enable_reverse_lookup"]:
            return False

        ips = [str(result.ip) for result in results]
        ips = filter(is_ip_address, ips)
        uniq_ips = set(ips)

        hostnames = dns_reverse_lookups(
            uniq_ips,
            timeout=dns_config["timeout"],
            num_workers=dns_config["num_workers"],
        )

        for result in results:
            if result.ip is None:
                continue

            ip = str(result.ip)
            if ip in hostnames:
                result.dns.reverse_name = hostnames[ip]

        return True

    def _lookup_geoip_dbs(self, results):
        geoip_db = GeoIPDB.instance()
        for res in results:
            if res.ip:
                res.geoip.city = geoip_db.lookup("city", res.ip)
                res.geoip.anonymous_ip = geoip_db.lookup("anonymous_ip", res.ip)
                res.geoip.asn = geoip_db.lookup("asn", res.ip)
                res.geoip.connection_type = geoip_db.lookup("connection_type", res.ip)
                res.geoip.domain = geoip_db.lookup("domain", res.ip)
                res.geoip.enterprise = geoip_db.lookup("enterprise", res.ip)
                res.geoip.isp = geoip_db.lookup("isp", res.ip)

        return True

    def lookup(self, ips):
        results = self._init_results(ips)
        self._lookup_geoip_dbs(results)
        self._lookup_dns(results)
        return results

    def dump_as_json(self, results, fp=sys.stdout):
        json.dump(results, fp, cls=ResultJSONEncoder)

    def dump_as_json_lines(self, results, fp=sys.stdout):
        for result in results:
            print(json.dumps(result, cls=ResultJSONEncoder), file=fp)

    def dump_as_csv(
        self,
        results,
        fp=sys.stdout,
        columns=None,
        include_header=True,
        escape_comma=False,
    ):
        if columns is None:
            columns = self.config["columns"]

        writer = csv.writer(fp, dialect="unix", quoting=csv.QUOTE_MINIMAL)

        if include_header:
            writer.writerow(columns)

        for result in results:
            row = [
                escape_csv_column(result[column], escape_comma=escape_comma)
                for column in columns
            ]
            writer.writerow(row)

    def dump(
        self,
        results,
        output_format="json",
        csv_columns=None,
        csv_include_header=True,
        csv_escape_comma=False,
    ):
        if output_format == "json":
            self.dump_as_json(results)
        elif output_format == "jsonl":
            self.dump_as_json_lines(results)
        elif output_format == "csv":
            self.dump_as_csv(
                results,
                columns=csv_columns,
                include_header=csv_include_header,
                escape_comma=csv_escape_comma,
            )
        else:
            raise ValueError("Invalid output_format: %s" % (output_format))


def parse_input_data(input_data, input_type):
    if input_type == "ip":
        return input_data
    elif input_type == "file":
        if len(input_data) > 0:
            # Read data from files.
            data = ""
            for filename in input_data:
                with open(filename) as f:
                    data += f.read() + "\n"
        else:
            # Read data from stdin.
            data = sys.stdin.read()
        return split_data(data)
    else:
        raise ValueError("Invalid input_type: %s" % (input_type))


def run(
    input_data,
    config_file=None,
    input_type="ip",
    output_format="json",
    csv_columns=None,
    csv_include_header=True,
    csv_escape_comma=False,
):
    config = Config()
    config.load(filename=config_file)

    geoip_db = GeoIPDB.instance()
    geoip_db.setup_dbs(**config["geoip"])

    data = parse_input_data(input_data, input_type)

    r = Runner(config)
    results = r.lookup(data)
    r.dump(
        results,
        output_format=output_format,
        csv_include_header=csv_include_header,
        csv_escape_comma=csv_escape_comma,
    )