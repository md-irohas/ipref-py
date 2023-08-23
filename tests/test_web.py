# -*- coding: utf-8 -*-


import io
from pathlib import Path

import pytest
from flask import request

from ipref.web import (
    apiv1_columns,
    apiv1_data_in_request,
    apiv1_render_as_csv,
    apiv1_search,
    columns_in_request,
    create_app,
    data_in_request,
    escape_column,
    get_header_name,
    get_metadata,
    make_flag,
)

from .conftest import TEST_IP_LIST


def test_create_app():
    create_app()


############################################################################
# Context Processors
############################################################################


def test_get_header_name(app):
    with app.app_context():
        assert get_header_name("meta.raw_input") == "Input"

        with pytest.raises(ValueError):
            get_header_name("not-found")


def test_escape_column():
    assert escape_column(None) == "-"
    assert escape_column({"foo", "bar"}) in (
        "foo bar",
        "bar foo",
    )  # the order of "foo" "bar" is undefined
    assert escape_column(["foo", "bar"]) == "foo bar"
    assert escape_column("foo") == "foo"


def test_make_flag():
    assert make_flag(None) == ""
    assert make_flag("JP") == "🇯🇵"


############################################################################
# Routes
############################################################################


def test_columns_in_request(app):
    with app.test_request_context(
        "/search",
        method="POST",
        data={
            "data": "a,b,c",
            "misc.include_national_flags": "on",
            "meta.raw_input": "on",
        },
    ):
        assert columns_in_request() == ["meta.raw_input"]


def test_data_in_request(app):
    with app.test_request_context(
        "/search",
        method="POST",
        data={
            "data": "a, b,c , d ,",
        },
    ):
        assert data_in_request() == ["a", "b", "c", "d"]


def test_get_metadata(app):
    meta = get_metadata()
    assert "nameservers" in meta
    assert "city" in meta
    assert "anonymous_ip" not in meta


def test_web_index_get(client):
    res = client.get("/")
    assert res.headers["Location"] == "/search"


def test_web_search_get(client):
    assert client.get("/search").status_code == 200


def test_web_search_post(client):
    res = client.post(
        "/search",
        data={
            "data": "1.1.1.1 192.0.2.0 not-ip",
            "meta.raw_input": "on",
            "meta.ip_address_types": "on",
        },
    )
    assert res.status_code == 200
    assert "public" in res.text
    assert "private" in res.text
    assert "error" in res.text


def test_web_search_post_with_skip_dns_lookup_reverse_name(client_full):
    res = client_full.post(
        "/search",
        data={
            "data": "1.1.1.1",
            "meta.raw_input": "on",
            "dns.reverse_name": "on",
        },
    )
    assert res.status_code == 200
    assert "one.one.one.one." in res.text

    # TODO: check if dns lookups are skipped (no way to check in unittest...)
    # res = client_full.post(
    #     "/search",
    #     data={
    #         "data": "1.1.1.1",
    #         "meta.raw_input": "on",
    #     },
    # )
    # assert res.status_code == 200
    # assert "one.one.one.one." not in res.text


def test_web_search_post_with_full_client(client_full):
    res = client_full.post(
        "/search",
        data={
            "data": " ".join(TEST_IP_LIST),
            "meta.raw_input": "on",
            "meta.ip_address": "on",
            "meta.ip_address_types": "on",
            "dns.reverse_name": "on",
            "geoip.country.continent.names.en": "on",
            "geoip.country.country.iso_code": "on",
            "geoip.country.country.names.en": "on",
            "geoip.city.continent.names.en": "on",
            "geoip.city.country.iso_code": "on",
            "geoip.city.country.names.en": "on",
            "geoip.city.city.names.en": "on",
            "geoip.city.postal.code": "on",
            "geoip.city.location.latitude": "on",
            "geoip.city.location.longitude": "on",
            "geoip.anonymous_ip.is_anonymous": "on",
            "geoip.anonymous_ip.is_anonymous_vpn": "on",
            "geoip.anonymous_ip.is_hosting_provider": "on",
            "geoip.anonymous_ip.is_public_proxy": "on",
            "geoip.anonymous_ip.is_residential_proxy": "on",
            "geoip.anonymous_ip.is_tor_exit_node": "on",
            "geoip.connection_type.connection_type": "on",
            "geoip.domain.domain": "on",
            "geoip.enterprise.country.iso_code": "on",
            "geoip.enterprise.country.name": "on",
            "geoip.enterprise.city.name": "on",
            "geoip.enterprise.postal.code": "on",
            "geoip.enterprise.location.latitude": "on",
            "geoip.enterprise.location.longitude": "on",
            "geoip.isp.autonomous_system_number": "on",
            "geoip.isp.autonomous_system_organization": "on",
            "geoip.isp.isp": "on",
            "geoip.isp.organization": "on",
            "geoip.asn.autonomous_system_number": "on",
            "geoip.asn.autonomous_system_organization": "on",
            "misc.include_national_flags": "on",
        },
    )
    assert res.status_code == 200
    for word in [
        # Meta
        "nameservers: 8.8.8.8, 8.8.4.4",
        "country: 2021-11-15",
        # Results
        "public",
        "in-addr.arpa",
        "Asia",
        "JP",
        "Japan",
        "🇯🇵",
        "35.68536",
        "139.75309",
        "True",
        "False",
        "Cable/DSL",
        "15169",
        "Google Inc.",
        "maxmind.com",
        "Europe",
        "GB",
        "United Kingdom",
        "Boxford",
        "OX1",
        "1221",
        "Telstra Pty Ltd",
        "Telstra Internet",
        "error",
    ]:
        assert word in res.text


def test_web_search_post_with_full_client_without_national_flags(client_full):
    res = client_full.post(
        "/search",
        data={
            "data": " ".join(TEST_IP_LIST),
            "geoip.country.country.iso_code": "on",
        },
    )
    assert res.status_code == 200
    assert "🇯🇵" not in res.text


############################################################################
# API (v1)
############################################################################


def test_apiv1_columns(app):
    # with columns data
    with app.test_request_context(
        "/api/v1/search",
        method="POST",
        data={"columns": "meta.raw_input,meta.ip_address_types"},
    ):
        assert apiv1_columns() == ["meta.raw_input", "meta.ip_address_types"]

    # without columns data
    with app.test_request_context(
        "/api/v1/search",
        method="POST",
    ):
        assert apiv1_columns() == [
            "meta.raw_input",
            "meta.ip_address_types",
            "geoip.city.country.iso_code",
            "geoip.city.country.names.en",
            "geoip.city.city.names.en",
            "geoip.connection_type.connection_type",
            "geoip.domain.domain",
            "geoip.isp.autonomous_system_number",
            "geoip.isp.autonomous_system_organization",
            "geoip.isp.isp",
        ]


def test_apiv1_data_in_request(app):
    path = Path("tests/data/ip1.txt")
    with path.open("rb") as f:
        with app.test_request_context(
            "/api/v1/search", method="POST", data={"data": f}
        ):
            assert apiv1_data_in_request() == ["a"]


def test_apiv1_render_as_csv(app):
    with app.test_request_context():
        resp = apiv1_render_as_csv(
            ["meta.raw_input", "meta.ip_address_types"],
            ["192.0.2.0", "192.0.2.1"],
            skip_dns_lookup_reverse_name=False,
            include_header=True,
            escape_comma=True,
        )
        assert resp.mimetype == "text/csv"
        assert (
            resp.get_data(as_text=True)
            == "meta.raw_input,meta.ip_address_types\n192.0.2.0,private\n192.0.2.1,private\n"
        )


def test_apiv1_search(client):
    path = Path("tests/data/ip-list.txt")
    with path.open("rb") as f:
        resp = client.post(
            "/api/v1/search?csv_noheader=0&csv_nocomma=0",
            data={
                "data": f,
                "columns": "meta.raw_input,meta.ip_address_types"
            },
        )
        assert resp.status_code == 200
        assert (
            resp.get_data(as_text=True)
            == "meta.raw_input,meta.ip_address_types\n192.0.2.0,private\n192.0.2.1,private\n"
        )


def test_apiv1_search_noheader(client):
    path = Path("tests/data/ip-list.txt")
    with path.open("rb") as f:
        resp = client.post(
            "/api/v1/search?csv_noheader=1",
            data={
                "data": f,
                "columns": "meta.raw_input,meta.ip_address_types"
            },
        )
        assert resp.status_code == 200
        assert (
            resp.get_data(as_text=True)
            == "192.0.2.0,private\n192.0.2.1,private\n"
        )


def test_apiv1_search_invalid_output_format(client):
    path = Path("tests/data/ip-list.txt")
    with path.open("rb") as f:
        resp = client.post(
            "/api/v1/search?format=json",
            data={
                "data": f,
                "columns": "meta.raw_input,meta.ip_address_types"
            },
        )
        assert resp.status_code == 400
