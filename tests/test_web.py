# -*- coding: utf-8 -*-


import pytest

from ipref.web import create_app, escape_column, get_header_name


def test_create_app():
    create_app()
    create_app(debug=True)


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
