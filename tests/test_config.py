# -*- coding: utf-8 -*-


import pytest

from ipref.config import Config


@pytest.fixture(name="config")
def make_config():
    return Config()


def test_config__load(config):
    # not found
    config._load("not-found")

    # found
    config._load("tests/etc/test-config.yaml")
    assert config["geoip"]["city"] == "tests/data/GeoIP2-City-Test.mmdb"


def test_config_load(config):
    # without filename
    config.load()

    # with filename
    config.load("tests/etc/test-config.yaml")
