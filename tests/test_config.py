# -*- coding: utf-8 -*-


import os

import pytest

from ipref.config import Config

from .conftest import TEST_CONFIG


@pytest.fixture(name="config")
def make_config():
    return Config()


def test_config__load(config):
    # not found (silent)
    config._load("not-found")

    # not found (not silent)
    config._load("not-found", silent=False)

    # found
    config._load(TEST_CONFIG)
    assert "output" in config


def test_config_is_loaded(config):
    assert config.is_loaded() is False

    config._load(TEST_CONFIG)

    assert config.is_loaded() is True


def test_config_load(config):
    # without filename / env
    config.load()

    # with ENV
    os.environ[config.CONFIG_VARNAME] = TEST_CONFIG
    config.load()
    del os.environ[config.CONFIG_VARNAME]

    # with filename
    config.load(TEST_CONFIG)
