# -*- coding: utf-8 -*-


import csv
import ipaddress
import json
import logging
import sys
from types import SimpleNamespace

from . import __version__
from .config import Config
from .data.dns import set_nameservers, get_nameservers, dns_reverse_lookups
from .data.geoip import GeoIPDB
from .util import get_dot_item, ip_address_types, is_ip_address, split_data, is_in

INPUT_TYPES = {"ip", "file"}
OUTPUT_FORMATS = {"json", "jsonl", "csv", "tsv"}

log = logging.getLogger(__name__)
geoip_db = GeoIPDB.instance()


def is_valid_input_type(s):
    return s in INPUT_TYPES


def is_valid_output_format(s):
    return s in OUTPUT_FORMATS


def _get_geoip_raw_data(record):
    if record:
        return record.raw
    else:
        return None


def escape_csv_column(col, escape_comma=False):
    if isinstance(col, set) or isinstance(col, list):
        col = " ".join(col)

    if escape_comma:
        if isinstance(col, str):
            col = col.replace(",", "<comma>")

    return col


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
        self.geoip.country = None
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

    def to_row(self, columns, escape_comma=False):
        return [
            escape_csv_column(self[column], escape_comma=escape_comma)
            for column in columns
        ]

    def to_dict(self):
        return {
            "meta": {
                "version": __name__.split(".")[0] + "-" + __version__,
                "raw_input": self.meta.raw_input,
                "ip_address": self.meta.ip_address,
                "ip_address_types": self.meta.ip_address_types,
            },
            "dns": {
                "reverse_name": self.dns.reverse_name,
            },
            "geoip": {
                "city": _get_geoip_raw_data(self.geoip.city),
                "country": _get_geoip_raw_data(self.geoip.country),
                "anonymous_ip": _get_geoip_raw_data(self.geoip.anonymous_ip),
                "asn": _get_geoip_raw_data(self.geoip.asn),
                "connection_type": _get_geoip_raw_data(self.geoip.connection_type),
                "domain": _get_geoip_raw_data(self.geoip.domain),
                "enterprise": _get_geoip_raw_data(self.geoip.enterprise),
                "isp": _get_geoip_raw_data(self.geoip.isp),
            },
        }


def _lookup_geoip_db(dbname, ip):
    if geoip_db.has_db(dbname):
        return geoip_db.lookup(dbname, ip)
    else:
        return None


class Runner:
    def __init__(self, config):
        self.config = config

    def _init_results(self, ips):
        return [Result(ip) for ip in ips]

    def _lookup_dns(self, results, skip_dns_lookup_reverse_name=False):
        dns_config = self.config["dns"]
        if not dns_config["reverse_name"]["enabled"]:
            log.info("Skip reverse name lookup (dns.reverse_name.enabled=False)")
            return False
        if skip_dns_lookup_reverse_name:
            log.info("Skip reverse name lookup (skip_dns_lookup_reverse_name=True)")
            return False

        ips = [str(result.ip) for result in results]
        ips = filter(is_ip_address, ips)
        uniq_ips = set(ips)

        hostnames = dns_reverse_lookups(
            uniq_ips,
            timeout=dns_config["reverse_name"]["timeout"],
            num_workers=dns_config["reverse_name"]["num_workers"],
        )

        for result in results:
            if result.ip is None:
                continue

            ip = str(result.ip)
            if ip in hostnames:
                result.dns.reverse_name = hostnames[ip]

        return True

    def _lookup_geoip_dbs(self, results):
        for res in results:
            if res.ip:
                res.geoip.city = _lookup_geoip_db("city", res.ip)
                res.geoip.country = _lookup_geoip_db("country", res.ip)
                res.geoip.anonymous_ip = _lookup_geoip_db("anonymous_ip", res.ip)
                res.geoip.asn = _lookup_geoip_db("asn", res.ip)
                res.geoip.connection_type = _lookup_geoip_db("connection_type", res.ip)
                res.geoip.domain = _lookup_geoip_db("domain", res.ip)
                res.geoip.enterprise = _lookup_geoip_db("enterprise", res.ip)
                res.geoip.isp = _lookup_geoip_db("isp", res.ip)

        return True

    def lookup(self, ips, skip_dns_lookup_reverse_name=False):
        log.info("Lookup %d input.", len(ips))
        results = self._init_results(ips)

        log.info("Lookup in GeoIP databases.")
        self._lookup_geoip_dbs(results)

        log.info("Lookup in DNS.")
        self._lookup_dns(results, skip_dns_lookup_reverse_name=skip_dns_lookup_reverse_name)

        log.info("Lookup done.")
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
        delimiter=",",
        include_header=True,
        escape_comma=False,
    ):
        if columns is None:
            columns = self.config["output"]["columns"]

        writer = csv.writer(
            fp, dialect="unix", quoting=csv.QUOTE_MINIMAL, delimiter=delimiter
        )
        if include_header:
            writer.writerow(columns)

        for result in results:
            writer.writerow(result.to_row(columns, escape_comma))

    def dump(
        self,
        results,
        fp=sys.stdout,
        output_format="json",
        csv_columns=None,
        csv_include_header=True,
        csv_escape_comma=False,
    ):
        if output_format == "json":
            self.dump_as_json(results, fp=fp)
        elif output_format == "jsonl":
            self.dump_as_json_lines(results, fp=fp)
        elif output_format == "csv" or output_format == "tsv":
            if output_format == "csv":
                delimiter = ","
            else:
                delimiter = "\t"

            self.dump_as_csv(
                results,
                fp=fp,
                columns=csv_columns,
                delimiter=delimiter,
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
    fp=sys.stdout,
    output_format="json",
    csv_columns=None,
    csv_include_header=True,
    csv_escape_comma=False,
):
    config = Config()
    config.load(filename=config_file)

    geoip_db = GeoIPDB.instance()
    geoip_db.setup_dbs(**config["geoip"]["dbs"])

    data = parse_input_data(input_data, input_type)
    log.info("# of input data: %d", len(data))

    if len(data) == 0:
        log.warning("no input data found.")
        return

    nameservers = config["dns"]["reverse_name"]["nameservers"]
    if nameservers:
        set_nameservers(nameservers)
        log.info("Set nameservers: %s", get_nameservers())
    else:
        log.info("The default nameservers are used: %s", get_nameservers())

    skip_dns_lookup_reverse_name = not is_in("dns.reverse_name", csv_columns, config["output"]["columns"])

    r = Runner(config)
    results = r.lookup(data, skip_dns_lookup_reverse_name=skip_dns_lookup_reverse_name)
    r.dump(
        results,
        fp=fp,
        output_format=output_format,
        csv_columns=csv_columns,
        csv_include_header=csv_include_header,
        csv_escape_comma=csv_escape_comma,
    )
