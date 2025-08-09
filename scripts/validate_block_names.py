#!/usr/bin/env python
import csv, sys, re, collections, pathlib

CSV = pathlib.Path("docs/block_names.csv")
NAME_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+){2,3}$")  # domain.sub.action[.variant]

REQUIRED = {
    "math": 350, "ndarray": 200, "dataframe": 150, "image": 120, "audio": 90,
    "text": 110, "io": 80, "crypto": 60, "system": 90, "util": 250,
}

def main():
    if not CSV.exists():
        print(f"ERROR: {CSV} not found")
        sys.exit(1)

    # Count rows & domains
    rows = list(csv.DictReader(CSV.open()))
    if len(rows) != 1500:
        print(f"ERROR: Expected 1500 rows, got {len(rows)}")
        sys.exit(1)

    # Validate each name format
    bad_names = [r["name"] for r in rows if not NAME_RE.match(r["name"])]
    if bad_names:
        print(f"ERROR: Invalid names: {bad_names[:5]}...")
        sys.exit(1)

    # Count domain distribution
    domains = collections.Counter(r["domain"] for r in rows)
    print(f"SUCCESS: 1500 blocks validated")
    print("Distribution:", dict(domains.most_common(10)))

    # Check required minimums
    for domain, min_count in REQUIRED.items():
        if domains.get(domain, 0) < min_count:
            print(f"WARNING: {domain}: {domains.get(domain, 0)} < {min_count} required")

if __name__ == "__main__":
    main()