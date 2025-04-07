import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

def cosine_distance_matrix(vectors: np.ndarray) -> np.ndarray:
    """
    Usage: calculate cosine distance matrix from embedded vectors
    Parameters: arrauy of vectors
    Returns: Distance matrix
    """
    cosine_sim = cosine_similarity(vectors)
     # clamp similarities to [-1, 1] to avoid numerical errors
    cosine_sim = np.clip(cosine_sim, -1.0, 1.0)
    
    cosine_dist = 1 - cosine_sim

    return cosine_dist

