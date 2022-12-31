# -*- coding: utf-8 -*-


import datetime
import ipaddress
from types import SimpleNamespace

import pytest

from ipref.util import get_dot_item, ip_address_types, is_ip_address, split_data, unixtime_to_datetime


def test_ip_address():
    # IPv4
    assert is_ip_address("192.0.2.0") is True

    # IPv6
    assert is_ip_address("2001:db8::") is True

    # Not IP
    assert is_ip_address("not-ip") is False


# fmt: off
@pytest.mark.parametrize(
    ("ip", "types",),
    (
        (None, {"error"}, ),
        ("224.0.0.0", {"multicast"}, ),
        ("10.0.0.0", {"private"}, ),
        ("0.0.0.0", {"private", "unspecified"}, ),
        ("240.0.0.0", {"private", "reserved"}, ),
        ("127.0.0.0", {"private", "loopback"}, ),
        ("169.254.0.0", {"private", "linklocal"}, ),
        ("1.1.1.1", {"public"}, ),
    )
)
# fmt: on
def test_ip_address_types(ip, types):
    if ip:
        ip = ipaddress.ip_address(ip)
    assert ip_address_types(ip) == types


def test_get_dot_item():
    obj = SimpleNamespace()
    obj.data1 = {"key-1": "value-1"}
    obj.data2 = SimpleNamespace()
    obj.data2.key_2 = "value_2"

    assert get_dot_item(obj, "data1.key-1") == "value-1"
    assert get_dot_item(obj, "data2.key_2") == "value_2"


def test_split_data():
    assert split_data("a  b,c\r\nd\ne") == ["a", "b", "c", "d", "e"]


def test_unixtime_to_datetime():
    assert unixtime_to_datetime(None) is None
    assert unixtime_to_datetime(0).isoformat() == "1970-01-01T00:00:00+00:00"
