# -*- coding: utf-8 -*-


import pytest

from ipref.data.dns import dns_reverse_lookups


@pytest.mark.parametrize(
    ("ips", "hostnames", "timeout", "num_workers"),
    (
        (
            [
                "1.1.1.1",
                "192.0.2.0",
            ],
            {"1.1.1.1": "one.one.one.one.", "192.0.2.0": None},
            5,
            10,
        ),
        (
            [
                "1.1.1.1",
                "192.0.2.0",
            ],
            {"1.1.1.1": "one.one.one.one.", "192.0.2.0": None},
            5,
            1,
        ),
    ),
)
def test_dns_reverse_lookups(ips, hostnames, timeout, num_workers):
    assert (
        dns_reverse_lookups(ips, timeout=timeout, num_workers=num_workers) == hostnames
    )
