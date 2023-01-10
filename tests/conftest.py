# -*- coding: utf-8 -*-


import os

import pytest

from ipref.config import Config
from ipref.web import create_app


TEST_CONFIG = "tests/etc/config.yaml"
TEST_CONFIG_FULL = "tests/etc/config-full.yaml"


@pytest.fixture
def app():
    os.environ[Config.CONFIG_VARNAME] = TEST_CONFIG
    app = create_app(
        test_config={
            "TESTING": True,
        }
    )

    yield app

    del os.environ[Config.CONFIG_VARNAME]


@pytest.fixture
def app_full():
    os.environ[Config.CONFIG_VARNAME] = TEST_CONFIG_FULL
    app = create_app(
        test_config={
            "TESTING": True,
        }
    )

    yield app

    del os.environ[Config.CONFIG_VARNAME]


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def client_full(app_full):
    return app_full.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
