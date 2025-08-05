import csv
import pathlib
import textwrap
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--max", type=int, default=None, help="limit number of kernels")
args = parser.parse_args()

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "kernels"
CSV = ROOT.parent / "docs" / "block_names.csv"

def generate_kernels():
    count = 0
    generated = 0
    with open(CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if args.max and generated >= args.max:
                break
                
            parts = row["name"].split(".")
            if len(parts) < 3:
                print(f"Skipping invalid name: {row['name']}")
                continue
                
            domain = parts[0]
            sub = parts[1]
            action = parts[2]
            
            # Create directory structure
            out_dir = SRC / domain / sub
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            out_file = out_dir / f"{action}.mojo"
            
            # Skip if already exists
            if out_file.exists():
                continue
            
            # Generate struct name by capitalizing and removing underscores
            struct_name = ''.join(word.capitalize() for word in action.split('_'))
            
            # Generate Mojo stub
            stub = textwrap.dedent(f'''
            @compiler.register("{row['name']}")
            struct {struct_name}:
                @staticmethod
                fn execute() -> Void:
                    # TODO: implement
                    return
            ''').strip()
            
            # Write file
            out_file.write_text(stub + "\n")
            count += 1
            generated += 1
            
    print(f"Generated {count} new kernel files (total processed: {generated})")

if __name__ == "__main__":
    generate_kernels()