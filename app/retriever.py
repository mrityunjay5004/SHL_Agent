import json
import faiss
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

index = faiss.read_index(
    "data/faiss_index/shl.index"
)


def retrieve(query, top_k=10):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for idx in indices[0]:

        results.append(catalog[idx])

    return results