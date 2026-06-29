#!/usr/bin/env python3
"""Verify that all domains in universities.json have valid DNS/MX records."""

import argparse
import dns.resolver
import json
import sys


def check_domain(domain):
    """Return (has_mx, has_a) for a domain."""
    has_mx = False
    has_a = False

    try:
        dns.resolver.resolve(domain, "MX")
        has_mx = True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        pass

    if not has_mx:
        for rtype in ("A", "AAAA"):
            try:
                dns.resolver.resolve(domain, rtype)
                has_a = True
                break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
                pass

    return has_mx, has_a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="universities.json")
    parser.add_argument(
        "--changed-only",
        metavar="DOMAIN",
        nargs="+",
        help="Only verify these specific domains (for PR checks)",
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        universities = json.load(f)["universities"]

    if args.changed_only:
        domains_to_check = set(args.changed_only)
    else:
        domains_to_check = {d for u in universities for d in u["domains"]}

    domain_to_uni = {d: u["name"] for u in universities for d in u["domains"]}

    failures = []
    warnings = []

    sorted_domains = sorted(domains_to_check)
    total = len(sorted_domains)

    for i, domain in enumerate(sorted_domains, 1):
        uni_name = domain_to_uni.get(domain, domain)
        print(f"[{i}/{total}] Checking {domain} ...", flush=True)
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

    print(f"All {len(domains_to_check)} domain(s) verified.")


if __name__ == "__main__":
    main()
