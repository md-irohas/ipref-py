# -*- coding: utf-8 -*-


import asyncio

import dns.asyncresolver
import dns.exception
import dns.resolver


resolver = dns.asyncresolver.Resolver()


def set_nameservers(ns):
    resolver.nameservers = ns


def get_nameservers():
    return resolver.nameservers[:]


def dns_reverse_lookups(ips, timeout=5, num_workers=100):
    async def dns_reverse_lookup_async(ip, sem):
        async with sem:
            return await resolver.resolve_address(ip, lifetime=timeout)

    async def dns_reverse_lookups_async(ips_):
        sem = asyncio.Semaphore(num_workers)
        lookups = [dns_reverse_lookup_async(ip, sem) for ip in ips_]
        return await asyncio.gather(*lookups, return_exceptions=True)

    # NOTE: after Python3.7
    lookup_results = asyncio.run(dns_reverse_lookups_async(ips))

    hostnames = dict()
    for ip, result in zip(ips, lookup_results):
        hostnames[ip] = None
        if isinstance(result, dns.resolver.Answer):
            if len(result) > 0:
                hostnames[ip] = result[0].target.to_text()

    return hostnames
