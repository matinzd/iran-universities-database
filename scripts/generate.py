#!/usr/bin/env python3
"""Generate swot-compatible domains/ tree and domains.txt from universities/*.json."""

import argparse
import glob
import json
import os
import re
import sys


def domain_to_path(domain):
    """Convert any university domain to (dir_path, filename) relative to domains/.

    Mirrors swot's directory structure: TLD parts reversed become nested dirs,
    the leftmost label becomes the filename.

    Examples:
        ut.ac.ir      -> ('ir/ac', 'ut.txt')
        iau.ir        -> ('ir',    'iau.txt')
        mit.edu       -> ('edu',   'mit.txt')
        ox.ac.uk      -> ('uk/ac', 'ox.txt')
    """
    parts = domain.split(".")
    if len(parts) < 2:
        raise ValueError(f"Domain must have at least two labels: {domain}")
    subdomain = parts[0]
    dir_parts = list(reversed(parts[1:]))
    return os.path.join(*dir_parts), f"{subdomain}.txt"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write files")
    parser.add_argument("--universities-dir", default="universities", help="Directory containing per-country JSON files")
    parser.add_argument("--domains-dir", default="domains", help="Output directory for domain tree")
    parser.add_argument("--domains-txt", default="domains.txt", help="Output flat domain list")
    args = parser.parse_args()

    country_files = sorted(glob.glob(os.path.join(args.universities_dir, "*.json")))
    if not country_files:
        print(f"ERROR: No JSON files found in {args.universities_dir}/", file=sys.stderr)
        sys.exit(1)

    all_universities = []
    all_domains = []
    errors = []
    files_to_write = {}

    for country_file in country_files:
        with open(country_file, encoding="utf-8") as f:
            country_data = json.load(f)

        for uni in country_data["universities"]:
            name = uni["name"]
            for domain in uni["domains"]:
                if not re.match(r"^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$", domain):
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

            all_universities.append(uni)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"Dry run OK: {len(all_universities)} universities, {len(all_domains)} domains")
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
    print(f"Total: {len(all_universities)} universities, {len(all_domains)} domains")


if __name__ == "__main__":
    main()
