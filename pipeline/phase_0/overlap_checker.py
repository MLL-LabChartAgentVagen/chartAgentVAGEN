"""
Semantic overlap checking using embeddings.

This module provides the check_overlap function as specified in phase_0.md.
"""

from typing import List, Tuple
import numpy as np

def get_embeddings(items: List[str], model: str = "text-embedding-3-small") -> np.ndarray:
    """Fetch embeddings for a list of strings using OpenAI."""
    from openai import OpenAI
    client = OpenAI()
    response = client.embeddings.create(input=items, model=model)
    embeddings = [data.embedding for data in response.data]
    return np.array(embeddings)

def cosine_similarity(embeddings: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarity matrix."""
    # We can use sklearn or just compute it manually
    try:
        from sklearn.metrics.pairwise import cosine_similarity as sklearn_cos_sim
        return sklearn_cos_sim(embeddings)
    except ImportError:
        # Fallback to manual computation if sklearn is missing
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / np.where(norms > 0, norms, 1.0)
        return np.dot(normalized, normalized.T)

def check_overlap(items: List[str],
                   model: str = "text-embedding-3-small",
                   threshold: float = 0.80) -> List[Tuple[str, str, float]]:
    """Return pairs whose cosine similarity >= threshold.

    Works for both topics and sub-topics — just pass the name list.
    """
    if len(items) < 2:
        return []

    embeddings = get_embeddings(items, model=model)   # items -> vectors
    sim_matrix = cosine_similarity(embeddings)
    overlaps = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if float(sim_matrix[i][j]) >= threshold:
                overlaps.append((items[i], items[j], float(sim_matrix[i][j])))
    return overlaps  # empty list = no overlap, good to go
