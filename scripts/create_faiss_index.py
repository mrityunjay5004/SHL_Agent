import numpy as np
import faiss

embeddings = np.load(
    "data/embeddings.npy"
)

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(
    dimension
)

index.add(embeddings)

faiss.write_index(
    index,
    "data/faiss_index/shl.index"
)

print("FAISS index created.")