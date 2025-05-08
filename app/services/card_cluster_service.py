import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from bson import ObjectId
from typing import List, Dict, Any, Tuple

from app.dao import knowledge_card_dao
from app.dao import card_cluster_dao
from app.utils import cosine_distance_matrix, generate_topic_name, clustering_module

class ClusteringServices:

    def get_clusters(self,user_id: str):
        print(f"received user_id:{user_id}")
        all_suits = card_cluster_dao.get_clusters_by_user(user_id)
        # here need to read all card details using card ids from the returned list from result
        suit_details=[]
        for suit in all_suits:
            suit_details.append({
                "cluster_id": suit.cluster_id,
                "user_id": suit.user_id,
                "knowledge_card_ids": suit.knowledge_card_ids,
                "topic_name": suit.topic_name
            })
        
        return suit_details

    @staticmethod
    def cluster_knowledge_cards(user_id: str):
        """
        Usage: Cluster knowledge cards for a user
        Args:
            user_id: The user ID to cluster cards for
            eps: DBSCAN epsilon parameter
            min_samples: DBSCAN min_samples parameter
        Returns:
            Tuple of (number of clusters created, status message)
        """
        # get all knowledge cards for the user
        print("processiiiingggggggggggggggggggg")
        cards = knowledge_card_dao.get_cards_by_user(user_id)
        print("cards doneeeeeeeeeee")
        min_samples = 3   #value is already defines in clustering module
        print(len(cards))
        if len(cards) < min_samples:   
            return "not enough cards to perform clustering"
        
        # get embedded vectors from cards
        
        print("getting embedded vectors")
        vectors = np.array([card["embedded_vector"] for card in cards])
        print("vectors")
        if vectors.size < 0:
            return "no vectors found"
        
        print(vectors)
        labels = clustering_module(vectors)
        print("labelsssss doneeee")
        # cleare existing clusters
        card_cluster_dao.clear_user_clusters(user_id)

        # create clusters
        user_id = ObjectId(user_id)
        # process each cluster
        for cluster_id in set(labels):
            # skip if outlier
            if cluster_id == -1:
                continue

            cluster_indices = np.where(labels == cluster_id)[0]

            # get cards in this cluster
            cluster_cards = [cards[i] for i in cluster_indices]
            cluster_card_ids = [card["_id"] for card in cluster_cards]

            # calculate centroid
            cluster_vectors = vectors[cluster_indices]
            centroid = np.mean(cluster_vectors, axis=0)
            print(centroid.shape)
            # # Reduce to 128 dimensions (or fewer as needed)
            # pca = PCA(n_components=384)
            # reduced_centroid = pca.fit_transform([centroid])[0].tolist()
            
            # generate topic name 
            topic_name = generate_topic_name(cluster_cards)
            print(topic_name)
            # create cluster document
            cluster_doc = {
                "user_id":user_id,
                "centroid_vector": centroid.tolist(),
                "knowledge_card_ids":cluster_card_ids,
                "topic_name": topic_name
            }
            clusters_created=0
            # insert cluster
            card_cluster_dao.create_cluster(cluster_doc)
            clusters_created += 1

            # handling noise cards
            noise_indices = np.where(labels == -1)[0]
            if len(noise_indices) >= min_samples:
                noise_cards = [cards[i] for i in noise_indices]
                noise_card_ids = [card["_id"] for card in noise_cards]  
                noise_vectors = vectors[noise_indices]
                noise_centroid = np.mean(noise_vectors, axis=0)

            # misc cluster
            misc_cluster = {
                "user_id":user_id,
                "centroid_vector": noise_centroid.tolist(),
                "knowledge_card_ids":noise_card_ids,
                "topic_name": "Miscellaneous"
            }

            card_cluster_dao.create_cluster(misc_cluster)
            clusters_created += 1

        return "Created {clusters_created} new clusters"