#!/usr/bin/env python3
"""One-time script to seed universities.json from JetBrains/swot Iranian domain files."""

import json
import subprocess
import sys
import base64


def gh_api(path):
    result = subprocess.run(
        ["gh", "api", f"repos/JetBrains/swot/contents/{path}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error fetching {path}: {result.stderr}", file=sys.stderr)
        return None
    return json.loads(result.stdout)


def fetch_file_content(path):
    data = gh_api(path)
    if data and "content" in data:
        return base64.b64decode(data["content"]).decode("utf-8").strip()
    return None


def main():
    universities = []

    # Fetch ac/* files (subdomain.ac.ir)
    ac_files = gh_api("lib/domains/ir/ac")
    if not ac_files:
        sys.exit(1)

    print(f"Fetching {len(ac_files)} ac/* files from swot...", file=sys.stderr)
    for i, entry in enumerate(ac_files):
        if entry["type"] != "file" or not entry["name"].endswith(".txt"):
            continue
        subdomain = entry["name"].replace(".txt", "")
        domain = f"{subdomain}.ac.ir"
        content = fetch_file_content(entry["path"])
        name = content.split("\n")[0] if content else ""
        universities.append({
            "name": name,
            "name_local": "",
            "country": "IR",
            "domains": [domain],
            "type": "",
            "city": "",
            "website": ""
        })
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(ac_files)} done...", file=sys.stderr)

    # Fetch top-level ir/*.txt files (non-ac domains)
    ir_files = gh_api("lib/domains/ir")
    if ir_files:
        for entry in ir_files:
            if entry["type"] != "file" or not entry["name"].endswith(".txt"):
                continue
            subdomain = entry["name"].replace(".txt", "")
            domain = f"{subdomain}.ir"
            content = fetch_file_content(entry["path"])
            name = content.split("\n")[0] if content else ""
            universities.append({
                "name": name,
                "name_local": "",
            "country": "IR",
                "domains": [domain],
                "type": "",
                "city": "",
                "website": ""
            })

    # Sort by name
    universities.sort(key=lambda u: u["name"].lower())

    output = {
        "$schema": "./schema.json",
        "universities": universities
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\nTotal: {len(universities)} universities", file=sys.stderr)


if __name__ == "__main__":
    main()
