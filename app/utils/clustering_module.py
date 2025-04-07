import numpy as np
from sklearn.cluster import DBSCAN
from bson import ObjectId
from typing import List, Dict, Any, Tuple
from utils import cosine_distance_matrix


def clustering_module(vectors , eps: float = 0.2, min_samples: int = 3):
        """
        Usage: Cluster knowledge cards for a user
        Args:
            vectors: embedded vectors
            eps: DBSCAN epsilon parameter
            min_samples: DBSCAN min_samples parameter
        Returns:
            Tuple of (number of clusters created, status message)
        """
        print("arriving here")
        # calculate distance matrix
        distance_matrix = cosine_distance_matrix(vectors)

        # DBSCAN clustering
        clustering = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric='precomputed'
        ).fit(distance_matrix)

        labels = clustering.labels_

        return labels