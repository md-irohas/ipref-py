# -*- coding: utf-8 -*-


import os

import pytest

from ipref.config import Config
from ipref.web import create_app

os.environ["FLASK_IPREF_CONF"] = "tests/etc/test-config.yaml"


@pytest.fixture
def config():
    conf = Config()
    conf.load("tests/etc/test-config.yaml")
    return conf


@pytest.fixture
def app():
    app = create_app(
        test_config={
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
