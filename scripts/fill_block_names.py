#!/usr/bin/env python
"""
Fill docs/block_names.csv to hit the target counts per domain.
- Reads the existing CSV
- Adds placeholder actions (op001, op002, …) per missing slot
- Writes back a complete ~1500‑row file, sorted lexicographically.
"""
import csv, pathlib, collections, itertools

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV  = ROOT / "docs" / "block_names.csv"

TARGET = {
    "math": 350,
    "ndarray": 200,
    "dataframe": 150,
    "image": 120,
    "audio": 90,
    "text": 110,
    "io": 80,
    "crypto": 60,
    "system": 90,
    "util": 250,
}

rows = list(csv.DictReader(CSV.open()))
by_domain = collections.defaultdict(list)
for r in rows:
    by_domain[r["domain"]].append(r)

def add_row(domain, sub, action, variant=""):
    name = ".".join([domain, sub, action] + ([variant] if variant else []))
    rows.append(
        dict(name=name, domain=domain, subdomain=sub, action=action, variant=variant)
    )

# simple placeholder generator
alph = "abcdefghijklmnopqrstuvwxyz"
for domain, target in TARGET.items():
    cur = len(by_domain[domain])
    if cur >= target:
        continue
    missing = target - cur
    sub = "placeholder"
    for i in range(1, missing + 1):
        action = f"op{i:03d}"
        add_row(domain, sub, action)

# de‑dupe + sort
unique = {(r["name"]): r for r in rows}
final_rows = sorted(unique.values(), key=lambda r: r["name"])

with CSV.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name", "domain", "subdomain", "action", "variant"])
    w.writeheader()
    w.writerows(final_rows)

print(f"CSV now has {len(final_rows)} rows (including header).")