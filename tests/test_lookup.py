# -*- coding: utf-8 -*-


import io
import json

import pytest

from ipref.data.geoip import GeoIPDB
from ipref.lookup import (
    INPUT_TYPES,
    OUTPUT_FORMATS,
    Result,
    ResultJSONEncoder,
    Runner,
    _get_geoip_raw_data,
    escape_csv_column,
    is_valid_input_type,
    is_valid_output_format,
    parse_input_data,
    run,
)


def test_is_valid_input_type():
    for input_type in INPUT_TYPES:
        assert is_valid_input_type(input_type) is True

    assert is_valid_input_type("invalid-type") is False


def test_is_valid_output_format():
    for output_format in OUTPUT_FORMATS:
        assert is_valid_output_format(output_format) is True

    assert is_valid_output_format("invalid-format") is False


def test__get_geoip_raw_data():
    db = GeoIPDB()
    db.setup_dbs(city="tests/data/GeoIP2-City-Test.mmdb")

    assert _get_geoip_raw_data(db.lookup("city", "2001:218::")) is not None
    assert _get_geoip_raw_data(db.lookup("city", "192.0.2.0")) is None


@pytest.fixture
def result_ip():
    return Result("192.0.2.0")


@pytest.fixture
def result_ip6():
    return Result("2001:db8::")


@pytest.fixture
def result_not_ip():
    return Result("not-ip")


def test_result__init__(result_ip, result_ip6, result_not_ip):
    assert result_ip.meta.ip_address_types == {"private"}
    assert result_ip6.meta.ip_address_types == {"private"}
    assert result_not_ip.meta.ip_address_types == {"error"}


def test_result_ip(result_ip, result_ip6, result_not_ip):
    assert result_ip.ip is not None
    assert result_ip6.ip is not None
    assert result_not_ip.ip is None


def test_result__getitem__(result_ip):
    assert result_ip["meta.ip_address"] == result_ip.meta.ip_address


def test_result_to_dict(result_ip, result_ip6, result_not_ip):
    # TODO: The dict data need to be checked.
    result_ip.to_dict()
    result_ip6.to_dict()
    result_not_ip.to_dict()


def test_result_json_encoder(result_ip, result_ip6, result_not_ip):
    assert json.dumps(result_ip, cls=ResultJSONEncoder) is not None
    assert json.dumps(result_ip6, cls=ResultJSONEncoder) is not None
    assert json.dumps(result_not_ip, cls=ResultJSONEncoder) is not None

    with pytest.raises(TypeError):
        json.dumps(object(), cls=ResultJSONEncoder)


def test_escape_csv_column():
    assert escape_csv_column(["a", "b"]) == "a b"
    assert escape_csv_column(0) == 0
    assert escape_csv_column("a,b,c") == "a,b,c"
    assert escape_csv_column("a,b,c", escape_comma=True) == "a<comma>b<comma>c"


@pytest.fixture
def runner(config):
    db = GeoIPDB.instance()
    db.setup_dbs(**config["geoip"]["dbs"])

    yield Runner(config)

    db.clear_dbs()


@pytest.fixture
def ips():
    return ["192.0.2.0", "not-ip"]


@pytest.fixture
def results(ips):
    return [Result(ip) for ip in ips]


def test_runner__init_results(runner, ips):
    assert len(runner._init_results(ips)) == 2


def test_runner__lookup_dns(runner, results):
    runner.config["dns"]["reverse_name"]["enabled"] = False
    assert runner._lookup_dns(results) is False

    runner.config["dns"]["reverse_name"]["enabled"] = True
    assert runner._lookup_dns(results) is True


def test_runner__lookup_geoip_dbs(runner, results):
    assert runner._lookup_geoip_dbs(results) is True


def test_runner_lookup(runner, ips):
    runner.lookup(ips)


def test_runner_dump_as_json(runner, results):
    runner.dump_as_json(results)


def test_runner_dump_as_json_lines(runner, results):
    runner.dump_as_json_lines(results)


def test_runner_dump_as_csv(runner, results):
    runner.dump_as_csv(results)


def test_runner_dump(runner, results):
    runner.dump(results, output_format="json")
    runner.dump(results, output_format="jsonl")
    runner.dump(results, output_format="csv")
    runner.dump(results, output_format="tsv")

    with pytest.raises(ValueError):
        runner.dump(results, output_format="not-supported")


def test_parse_input_data(capsys, monkeypatch):
    # ip
    assert parse_input_data(["a", "b", "c"], "ip") == ["a", "b", "c"]

    # files
    assert parse_input_data(
        ["tests/data/ip1.txt", "tests/data/ip2.txt", "tests/data/ip3.txt"], "file"
    ) == ["a", "b", "c", "d"]

    # file (stdin)
    monkeypatch.setattr("sys.stdin", io.StringIO("a b c"))
    assert parse_input_data([], "file") == ["a", "b", "c"]

    with pytest.raises(ValueError):
        parse_input_data([], "not-supported")


def test_run():
    run(["192.0.2.0", "not-ip"], input_type="ip")
    run([], input_type="ip")
