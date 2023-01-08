# -*- coding: utf-8 -*-


import logging
import os

import yaml

# See config.yaml.orig for the full documentation.
DEFAULT_CONFIG = {
    "dns": {
        "enable_reverse_lookup": False,
        "timeout": 5,
        "num_workers": 10,
    },
    "geoip": {
        "dbs": {
        }
    },
    "output": {
        "columns": [
            "meta.raw_input",
            "meta.ip_address_types",
        ],
    },
    "web": {
        "title": "ipref",
        "search": [
            {
                "name": "Meta",
                "items": [
                    {
                        "label": "Input",
                        "checked": True,
                        "data": "meta.raw_input",
                    },
                    {
                        "label": "IP Addr.",
                        "checked": False,
                        "data": "meta.ip_address",
                    },
                    {
                        "label": "IP Types",
                        "checked": True,
                        "data": "meta.ip_address_types",
                    },
                ],
            },
        ],
    },
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
        self._is_loaded = False
        self.update(**DEFAULT_CONFIG)

    # TODO: 'update' method does not update nested data. Therefore, it is
    # needed to be implemented.

    def _load(self, filename, silent=True):
        if not os.path.exists(filename):
            if silent:
                log.info("load config: %s (not-found)", filename)
            else:
                log.error("load config: %s (not-found)", filename)
            return

        log.info("load config: %s", filename)
        with open(filename) as f:
            data = yaml.safe_load(f)
            self.update(**data)

        self._is_loaded = True

    def is_loaded(self):
        return self._is_loaded

    def load(self, filename=None, silent=False):
        for filepath in self.CONFIG_FILEPATHS:
            self._load(filepath, silent=True)
        if filename:
            self._load(filename, silent=silent)

        log.info("config: %s", self)
