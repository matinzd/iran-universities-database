#!/usr/bin/env python3
"""Verify that all domains in universities.json have valid DNS/MX records."""

import argparse
import dns.resolver
import glob
import json
import sys

# Public resolvers used in order; falls back down the list on failure
_RESOLVERS = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1"]
_RETRIES = 3


def _query(domain, rtype):
    """Query domain/rtype trying each public resolver up to _RETRIES times."""
    for nameserver in _RESOLVERS:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [nameserver]
        resolver.timeout = 5
        resolver.lifetime = 10
        for _ in range(_RETRIES):
            try:
                resolver.resolve(domain, rtype)
                return True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                break  # definitive negative — try next resolver
            except dns.exception.Timeout:
                continue  # transient — retry same resolver
    return False


def check_domain(domain):
    """Return (has_mx, has_a) for a domain."""
    has_mx = _query(domain, "MX")
    has_a = False
    if not has_mx:
        has_a = _query(domain, "A") or _query(domain, "AAAA")
    return has_mx, has_a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--universities-dir", default="universities",
                        help="Directory containing per-country JSON files")
    parser.add_argument(
        "--changed-only",
        metavar="DOMAIN",
        nargs="+",
        help="Only verify these specific domains (for PR checks)",
    )
    args = parser.parse_args()

    universities = []
    for path in sorted(glob.glob(f"{args.universities_dir}/*.json")):
        with open(path, encoding="utf-8") as f:
            universities.extend(json.load(f)["universities"])

    if args.changed_only:
        domains_to_check = set(args.changed_only)
    else:
        domains_to_check = {d for u in universities for d in u["domains"]}

    domain_to_uni = {d: u["name"] for u in universities for d in u["domains"]}
    iran_only_domains = {d for u in universities if u.get("dns_iran_only") for d in u["domains"]}

    failures = []
    warnings = []
    skipped = []

    sorted_domains = sorted(domains_to_check)
    total = len(sorted_domains)

    for i, domain in enumerate(sorted_domains, 1):
        uni_name = domain_to_uni.get(domain, domain)
        print(f"[{i}/{total}] Checking {domain} ...", flush=True)

        if domain in iran_only_domains:
            print(f"  SKIP     {domain}  ({uni_name}) [dns_iran_only]")
            skipped.append(f"{domain} ({uni_name}): nameservers only reachable from within Iran")
            continue

        has_mx, has_a = check_domain(domain)

        if has_mx:
            print(f"  OK (MX)  {domain}  ({uni_name})")
        elif has_a:
            print(f"  OK (A)   {domain}  ({uni_name})")
            warnings.append(f"{domain} ({uni_name}): resolves but has no MX record")
        else:
            print(f"  FAIL     {domain}  ({uni_name})")
            failures.append(f"{domain} ({uni_name}): no MX or A/AAAA records found")

    print()

    if skipped:
        print("Skipped (dns_iran_only — nameservers unreachable outside Iran):")
        for s in skipped:
            print(f"  - {s}")
        print()

    if warnings:
        print("Warnings (domain resolves but no MX record):")
        for w in warnings:
            print(f"  - {w}")
        print()

    if failures:
        print("Failed domains (no DNS records found):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"All {len(domains_to_check) - len(skipped)} domain(s) verified ({len(skipped)} skipped).")


if __name__ == "__main__":
    main()
