import json
from pathlib import Path
from typing import List, Dict, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


CATALOG_PATH = Path("data/processed_catalog.json")
INDEX_PATH = Path("data/faiss_index/shl.index")

MODEL_NAME = "all-MiniLM-L6-v2"


import re

class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        self.index = faiss.read_index(str(INDEX_PATH))

        # Fast lookup for exact assessment names
        self.name_lookup = {
            item["name"].lower(): item
            for item in self.catalog
        }

    def encode(self, text: str) -> np.ndarray:
        embedding = self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(np.float32)

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Dict]:
        query_clean = query.lower()

        # 1. Semantic retrieval with FAISS (normalized cosine similarity)
        embedding = self.encode(query)
        distances, indices = self.index.search(
            embedding,
            min(top_k * 3, len(self.catalog)),
        )

        candidates = []
        seen = set()

        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            item = self.catalog[idx].copy()
            # Since vectors are normalized, IP search returns cosine similarity
            item["similarity_score"] = float(score)
            item["hybrid_score"] = float(score)
            candidates.append(item)
            seen.add(item["name"].lower())

        # 2. Exact keyword / substring check on catalog names
        # Extract keywords from the query
        query_tokens = [t.strip() for t in re.split(r"[^\w\+\-]", query_clean) if t.strip()]
        stop_words = {"a", "an", "the", "and", "or", "in", "on", "at", "for", "with", "is", "are", "to", "of", "about", "what", "assessments", "solution", "solutions", "hiring", "screen", "screening"}
        keywords = [t for t in query_tokens if t not in stop_words and len(t) > 1]

        # Add items matching named entities directly to candidates if missed
        for item in self.catalog:
            item_name_lower = item["name"].lower()
            if len(item["name"]) > 4 and item_name_lower in query_clean:
                if item_name_lower not in seen:
                    item_copy = item.copy()
                    item_copy["similarity_score"] = 0.5
                    item_copy["hybrid_score"] = 1.0
                    candidates.append(item_copy)
                    seen.add(item_name_lower)

        # 3. Calculate keyword boost
        for item in candidates:
            boost = 0.0
            item_name_lower = item["name"].lower()
            item_desc_lower = item.get("description", "").lower()
            item_keys_lower = " ".join(item.get("keys", [])).lower()

            for kw in keywords:
                if kw in item_name_lower:
                    boost += 0.25
                if kw in item_keys_lower:
                    boost += 0.1
                if kw in item_desc_lower:
                    boost += 0.05
            
            # Additional boost for matching specific acronyms/aliases
            aliases = ["opq", "svar", "dsi", "gsa", "verify"]
            for alias in aliases:
                if alias in query_clean and alias in item_name_lower:
                    boost += 0.3

            item["hybrid_score"] += boost

        # Sort candidates by hybrid score
        candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return candidates[:top_k]

    def lookup_assessment(
        self,
        assessment_name: str,
    ) -> Optional[Dict]:
        name_clean = assessment_name.lower().strip()

        # 1. Direct exact lookup
        if name_clean in self.name_lookup:
            return self.name_lookup[name_clean]

        # 2. Check aliases
        aliases = {
            "opq": "Occupational Personality Questionnaire OPQ32r",
            "opq32r": "Occupational Personality Questionnaire OPQ32r",
            "dsi": "Dependability and Safety Instrument (DSI)",
            "verify g+": "SHL Verify Interactive G+",
            "g+": "SHL Verify Interactive G+",
            "verify interactive g+": "SHL Verify Interactive G+",
            "gsa": "Global Skills Assessment",
            "global skills assessment": "Global Skills Assessment",
            "svar": "SVAR Spoken English (US) (New)",
            "excel": "Microsoft Excel 365 (New)",
            "word": "Microsoft Word 365 (New)"
        }

        if name_clean in aliases:
            target_name = aliases[name_clean].lower()
            if target_name in self.name_lookup:
                return self.name_lookup[target_name]

        # 3. Substring match fallback (longest match first)
        matches = []
        for cat_name, item in self.name_lookup.items():
            # Check suffix-stripped matches
            clean_cat = cat_name.replace("(new)", "").replace("(general)", "").replace("- essentials (new)", "").strip()
            if name_clean == clean_cat:
                return item
            if name_clean in cat_name or cat_name in name_clean:
                matches.append(item)

        if matches:
            # Prefer exact-length or shortest name matching substring
            matches.sort(key=lambda x: len(x["name"]))
            return matches[0]

        return None


retriever = Retriever()


def retrieve(
    query: str,
    top_k: int = 10,
):
    return retriever.search(
        query=query,
        top_k=top_k,
    )


def lookup_by_name(
    name: str,
):
    return retriever.lookup_assessment(name)