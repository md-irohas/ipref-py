# -*- coding: utf-8 -*-


import pytest

from ipref.web import create_app, escape_column, get_header_name

from .conftest import TEST_IP_LIST


def test_create_app():
    create_app()


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
        },
    )
    assert res.status_code == 200
    for word in [
        "public",
        "in-addr.arpa",
        "Asia",
        "JP",
        "Japan",
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
