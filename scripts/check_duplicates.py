#!/usr/bin/env python3
"""Check universities.json for duplicate domains and university names."""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="universities.json")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        universities = json.load(f)["universities"]

    errors = []

    seen_domains = {}
    for uni in universities:
        for domain in uni["domains"]:
            if domain in seen_domains:
                errors.append(
                    f"Duplicate domain '{domain}': appears in both "
                    f"'{seen_domains[domain]}' and '{uni['name']}'"
                )
            else:
                seen_domains[domain] = uni["name"]

    seen_names = {}
    for uni in universities:
        key = uni["name"].strip().lower()
        if key in seen_names:
            errors.append(
                f"Duplicate name '{uni['name']}': already exists as '{seen_names[key]}'"
            )
        else:
            seen_names[key] = uni["name"]

    if errors:
        print("Duplicate check failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print(f"No duplicates found ({len(universities)} universities, {len(seen_domains)} domains)")


if __name__ == "__main__":
    main()
