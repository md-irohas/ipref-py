# -*- coding: utf-8 -*-


import logging
import os

import yaml

# See config.yaml.orig for the full documentation.
DEFAULT_CONFIG = {
    "dns": {
        "enable_reverse_lookup": False,
        "timeout": 5,
        "num_workers": 100,
    },
    "geoip": {
        "city": None,
        "anonymous_ip": None,
        "asn": None,
        "connection_type": None,
        "domain": None,
        "enterprise": None,
        "isp": None,
    },
    "columns": [
        # Meta
        "meta.ip_address",
        "meta.ip_address_types",
    ],
}


log = logging.getLogger(__name__)


class Config(dict):

    CONFIG_FILEPATHS = [
        "~/.config/ipref.yaml",
        "~/.config/ipref.yml",
        "~/.ipref.yaml",
        "~/.ipref.yml",
    ]

    def __init__(self):
        super().__init__()
        self.update(**DEFAULT_CONFIG)

    # TODO: 'update' method does not update nested data. Therefore, it is
    # needed to be implemented.

    def _load(self, filename):
        if not os.path.exists(filename):
            log.info("load config: %s (not-found)", filename)
            return

        log.info("load config: %s", filename)
        with open(filename) as f:
            data = yaml.safe_load(f)
            self.update(**data)

    def load(self, filename=None):
        for filepath in self.CONFIG_FILEPATHS:
            self._load(filepath)
        if filename:
            self._load(filename)

        log.info("config: %s", self)
