import json
import pickle

with open(
    "data/processed_catalog.json",
    "r",
    encoding="utf-8"
) as f:

    catalog = json.load(f)

metadata = []

for idx, item in enumerate(catalog):

    metadata.append({
        "index": idx,
        "name": item["name"],
        "link": item["link"]
    })

with open(
    "data/metadata.pkl",
    "wb"
) as f:

    pickle.dump(metadata, f)

print("Metadata created.")