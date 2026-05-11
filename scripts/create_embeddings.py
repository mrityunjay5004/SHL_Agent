import json
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

with open(
    "data/processed_catalog.json",
    "r",
    encoding="utf-8"
) as f:

    catalog = json.load(f)

texts = [
    item["combined_text"]
    for item in catalog
]

embeddings = model.encode(
    texts,
    convert_to_numpy=True
)

np.save(
    "data/embeddings.npy",
    embeddings
)

print("Embeddings created.")