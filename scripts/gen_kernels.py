#!/usr/bin/env python
"""Generate Mojo kernel stubs from block CSV (idempotent)."""
import csv, pathlib, textwrap, argparse

CSV = pathlib.Path("docs/block_names.csv")
KERNELS = pathlib.Path("neocore/src/kernels")

TEMPLATE = '''
from memory import memset_zero, memcpy
from python import Python
from utils.variant import Variant

@compiler.register("{full_name}")
struct {class_name}:
    var config: Dict[String, Variant]
    var state: Dict[String, Variant]
    
    fn __init__(inout self):
        self.config = Dict[String, Variant]()
        self.state = Dict[String, Variant]()
    
    @staticmethod
    fn execute(inout self, input: Variant) -> Variant:
        # TODO: Implement {action} for {domain}.{subdomain}
        return Variant(True)
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=None, help="limit number of kernels")
    args = parser.parse_args()

    rows = list(csv.DictReader(CSV.open()))
    if args.max:
        rows = rows[:args.max]

    # Ensure output dir
    KERNELS.mkdir(parents=True, exist_ok=True)

    generated = 0
    for row in rows:
        parts = row["name"].split(".")
        domain, subdomain = parts[0], parts[1]
        action = parts[2] if len(parts) > 2 else "default"
        variant = parts[3] if len(parts) > 3 else None

        # Create path
        if variant:
            path = KERNELS / domain / subdomain / f"{action}_{variant}.mojo"
        else:
            path = KERNELS / domain / subdomain / f"{action}.mojo"

        # Skip if exists (idempotent)
        if path.exists():
            continue

        # Generate stub
        path.parent.mkdir(parents=True, exist_ok=True)
        class_name = "".join(p.title() for p in parts)
        code = TEMPLATE.format(
            full_name=row["name"],
            class_name=class_name,
            domain=domain,
            subdomain=subdomain,
            action=action
        ).strip()
        
        path.write_text(code)
        generated += 1

    print(f"Generated {generated} new kernels (total: {len(rows)})")

if __name__ == "__main__":
    main()