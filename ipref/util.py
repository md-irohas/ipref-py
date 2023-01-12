# -*- coding: utf-8 -*-


import datetime
import ipaddress
import re


def is_ip_address(s):
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False


def ip_address_types(ip):
    if ip is None:
        return {"error"}

    # see http://docs.python.jp/3/library/ipaddress.html.
    ret = set()
    if ip.is_multicast:
        ret.add("multicast")
    if ip.is_private:
        ret.add("private")
    if ip.is_unspecified:
        ret.add("unspecified")
    if ip.is_reserved:
        ret.add("reserved")
    if ip.is_loopback:
        ret.add("loopback")
    if ip.is_link_local:
        ret.add("linklocal")

    if len(ret) == 0:
        ret.add("public")

    return ret


def get_dot_item(obj, dot_key):
    for item in dot_key.split("."):
        if isinstance(obj, dict):
            obj = obj.get(item, None)
        else:
            obj = getattr(obj, item, None)
    return obj


def split_data(s):
    data = re.split(" |,|\t|\r|\n|\r\n", s)
    data = map(lambda x: x.strip(), data)
    data = filter(len, data)
    return list(data)


def unixtime_to_datetime(ts, tz=None):
    if ts is None:
        return None
    if tz is None:
        tz = datetime.timezone.utc

    return datetime.datetime.fromtimestamp(ts, tz=tz)


def is_in(val, *args):
    for arg in args:
        if arg:
            return val in arg
    return False
