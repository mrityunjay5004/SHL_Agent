import os
import subprocess
import sys

def get_mtime(path):
    if not os.path.exists(path):
        return 0
    return os.path.getmtime(path)

def main():
    shl_catalog = "data/shl_catalog.json"
    processed_catalog = "data/processed_catalog.json"
    embeddings = "data/embeddings.npy"
    metadata = "data/metadata.pkl"
    faiss_index = "data/faiss_index/shl.index"

    t_shl = get_mtime(shl_catalog)
    t_processed = get_mtime(processed_catalog)
    t_embeddings = get_mtime(embeddings)
    t_metadata = get_mtime(metadata)
    t_faiss = get_mtime(faiss_index)

    print(f"shl_catalog modified time: {t_shl}")
    print(f"processed_catalog modified time: {t_processed}")
    print(f"embeddings modified time: {t_embeddings}")
    print(f"metadata modified time: {t_metadata}")
    print(f"faiss_index modified time: {t_faiss}")

    # Step 1: processed_catalog
    if t_processed == 0 or t_processed < t_shl:
        print("Rebuilding processed catalog...")
        subprocess.run([sys.executable, "scripts/create_processed_catalog.py"], check=True)
        t_processed = get_mtime(processed_catalog)
    else:
        print("Processed catalog is up to date.")

    # Step 2: embeddings
    if t_embeddings == 0 or t_embeddings < t_processed:
        print("Rebuilding embeddings...")
        subprocess.run([sys.executable, "scripts/create_embeddings.py"], check=True)
        t_embeddings = get_mtime(embeddings)
    else:
        print("Embeddings are up to date.")

    # Step 3: metadata
    if t_metadata == 0 or t_metadata < t_processed:
        print("Rebuilding metadata...")
        subprocess.run([sys.executable, "scripts/create_metadata.py"], check=True)
        t_metadata = get_mtime(metadata)
    else:
        print("Metadata is up to date.")

    # Step 4: FAISS index
    if t_faiss == 0 or t_faiss < t_embeddings:
        print("Rebuilding FAISS index...")
        subprocess.run([sys.executable, "scripts/create_faiss_index.py"], check=True)
        t_faiss = get_mtime(faiss_index)
    else:
        print("FAISS index is up to date.")

    print("Pipeline check complete.")

if __name__ == '__main__':
    main()
