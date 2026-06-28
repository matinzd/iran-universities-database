#!/usr/bin/env python3
"""Generate swot-compatible domains/ tree and domains.txt from universities.json."""

import argparse
import json
import os
import re
import sys


def domain_to_path(domain):
    """Convert a domain like ut.ac.ir to (dir_path, filename) relative to domains/."""
    if domain.endswith(".ac.ir"):
        subdomain = domain[: -len(".ac.ir")]
        return os.path.join("ir", "ac"), f"{subdomain}.txt"
    elif domain.endswith(".ir"):
        subdomain = domain[: -len(".ir")]
        return "ir", f"{subdomain}.txt"
    else:
        raise ValueError(f"Domain must end in .ac.ir or .ir: {domain}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write files")
    parser.add_argument("--input", default="universities.json", help="Input JSON file")
    parser.add_argument("--domains-dir", default="domains", help="Output directory for domain tree")
    parser.add_argument("--domains-txt", default="domains.txt", help="Output flat domain list")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    universities = data["universities"]
    all_domains = []
    errors = []
    files_to_write = {}

    for uni in universities:
        name = uni["name"]
        for domain in uni["domains"]:
            if not re.match(r"^[a-z0-9.-]+\.(ac\.ir|ir)$", domain):
                errors.append(f"Invalid domain format '{domain}' in '{name}'")
                continue
            try:
                dir_path, filename = domain_to_path(domain)
            except ValueError as e:
                errors.append(str(e))
                continue

            file_path = os.path.join(args.domains_dir, dir_path, filename)
            if file_path in files_to_write:
                errors.append(f"Duplicate domain '{domain}' — conflicts with '{files_to_write[file_path][1]}'")
            else:
                files_to_write[file_path] = (name, name)
            all_domains.append(domain)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"Dry run OK: {len(universities)} universities, {len(all_domains)} domains")
        return

    # Write domain tree
    for file_path, (name, _) in files_to_write.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(name + "\n")

    # Write flat domain list
    all_domains.sort()
    with open(args.domains_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(all_domains) + "\n")

    print(f"Generated {len(files_to_write)} domain files and {args.domains_txt}")
    print(f"Total: {len(universities)} universities, {len(all_domains)} domains")


if __name__ == "__main__":
    main()
