# -*- coding: utf-8 -*-
"""A helper module for MaxMind's GeoIP databases."""


import logging

from geoip2.database import MODE_MEMORY, Reader
from geoip2.errors import AddressNotFoundError

log = logging.getLogger(__name__)


class GeoIPDB:

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = GeoIPDB()
        return cls._instance

    def __init__(self, **kwargs):
        self._dbpaths = {}
        self._dbs = {}

        self.setup_dbs(**kwargs)

    @property
    def metadata(self):
        return {k: v.metadata() if v else None for k, v in self._dbs.items()}

    def setup_dbs(self, **kwargs):
        self.clear_dbs()

        for dbname, dbpath in kwargs.items():
            self._dbpaths[dbname] = dbpath

        self.reload_dbs()

    def _close_dbs(self):
        for dbname, db in self._dbs.items():
            if db is not None:
                db.close()

    def clear_dbs(self):
        self._close_dbs()
        self._dbpaths.clear()
        self._dbs.clear()

    def reload_dbs(self):
        self._close_dbs()

        for dbname, dbpath in self._dbpaths.items():
            log.info("load GeoIP2 database: %s: %s", dbname, dbpath)
            if dbpath:
                self._dbs[dbname] = Reader(dbpath, mode=MODE_MEMORY)
            else:
                self._dbs[dbname] = None

    def has_db(self, dbname):
        return dbname in self._dbs

    def lookup(self, dbname, addr):
        if dbname not in self._dbs:
            raise ValueError("db not found: %s" % (dbname))

        db = self._dbs[dbname]
        if db is None:
            return None

        try:
            return getattr(db, dbname)(addr)
        except AddressNotFoundError:
            return None
