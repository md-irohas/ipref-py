# -*- coding: utf-8 -*-


import pytest

from ipref.data.geoip import GeoIPDB


def test_geoipdb_instance():
    assert GeoIPDB.instance() == GeoIPDB.instance()


@pytest.fixture(name="empty_db")
def geoip_db_empty():
    return GeoIPDB()


@pytest.fixture(name="db")
def geoip_db_setup():
    return GeoIPDB(city="tests/data/GeoIP2-City-Test.mmdb", domain=None)


def test_geoipdb_metadata(db):
    assert db.metadata["city"] is not None


def test_geoipdb_setup_dbs(empty_db):
    empty_db.setup_dbs(city="tests/data/GeoIP2-City-Test.mmdb")

    with pytest.raises(OSError):
        empty_db.setup_dbs(city="not-found")


def test_geoipdb__close_dbs(db):
    db._close_dbs()


def test_geoipdb_clear_dbs(db):
    db.clear_dbs()


def test_geoipdb_reload_dbs(db):
    db.reload_dbs()


def test_geoipdb_lookup(db):
    assert db.lookup("city", "2001:218::") is not None
    assert db.lookup("city", "192.0.2.0") is None

    with pytest.raises(ValueError):
        db.lookup("not-dbname", "192.0.2.0")
