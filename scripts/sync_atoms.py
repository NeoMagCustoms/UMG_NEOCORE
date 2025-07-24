import csv, os, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAT = ROOT / 'catalog' / 'blocks_master.csv'
DST = ROOT / 'blocks'

# Create stub JSON for each atomic block
with open(CAT) as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        parts = name.split('.')
        if len(parts) < 3:
            continue
        domain, subdomain, action = parts[0], parts[1], '.'.join(parts[2:])
        json_path = DST / domain / subdomain / f'{action}.json'
        if not json_path.exists():
            json_path.parent.mkdir(parents=True, exist_ok=True)
            stub = {
                \"label\": action.replace('.', '-'),
                \"domain\": domain,
                \"subdomain\": subdomain,
                \"tags\": [],
                \"props\": {}
            }
            json_path.write_text(json.dumps(stub, indent=2))

# Apply bundle tags based on macro_to_blocks.csv
macro_csv = ROOT / 'catalog' / 'macro_to_blocks.csv'
with open(macro_csv) as m:
    reader = csv.DictReader(m)
    for r in reader:
        feature = r['macro_feature']
        atoms = [a.strip() for a in r['atomic_blocks'].split('|') if a.strip()]
        slug = feature.lower().replace(' ', '-').replace('/', '').replace('(', '').replace(')', '').replace('&','and')
        for a in atoms:
            parts = a.split('.')
            if len(parts) < 3:
                continue
            domain, subdomain, action = parts[0], parts[1], '.'.join(parts[2:])
            json_path = DST / domain / subdomain / f'{action}.json'
            if json_path.exists():
                data = json.loads(json_path.read_text())
                tags = set(data.get('tags', []))
                tags.add(f\"bundle:{slug}\")
                data['tags'] = sorted(tags)
                json_path.write_text(json.dumps(data, indent=2))
