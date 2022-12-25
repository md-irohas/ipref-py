# -*- coding: utf-8 -*-


import pytest

from ipref.config import Config


@pytest.fixture
def config():
    conf = Config()
    conf.load("tests/etc/test-config.yaml")
    return conf
