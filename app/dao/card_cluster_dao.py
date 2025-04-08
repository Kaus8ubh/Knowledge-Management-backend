from bson import ObjectId
from database import db_instance
from models import CardCluster
from typing import List, Dict, Any, Optional


class ClusterDao:
    def __init__(self):
        """        
        Initialize the ClusterDao with a reference to the clusters collection.
        """
        self.clusters_collection = db_instance.get_collection("clusters_collection")

    def clear_user_clusters(self, user_id: str):
        """
        Usage: delete previous clusters of a user
        parameter: user_id to delete clusters for
        returns: success/failure message
        """
        try:
            user_id = ObjectId(user_id)
            result = self.clusters_collection.delete_many({"user_id": user_id})
            print("clusters cleared")
            return result.deleted_count
        except Exception as exception:
            print(f"error clearing clusters: {exception}")
            return 0
            
    def create_cluster(self, cluster_data: Dict[str, Any]):
        """
        Usage: creates new cluster
        parameter: cluster_data to insert
        return: id of inserted cluster or none on failure
        """
        try:
            result = self.clusters_collection.insert_one(cluster_data)
            return str(result.inserted_id) if result.inserted_id else None
        except Exception as exception:
            print(f"error creating cluster: {exception}")
            return None
            
    def get_clusters_by_user(self, user_id: str) ->List[Dict]:
        """
        Usage: Get all clusters for a user
        Parameter: user_id: The user ID to get clusters for
        Returns: List of clusters
        """
        try:
            user_obj_id = ObjectId(user_id)
            clusters = self.clusters_collection.find({"user_id": user_obj_id})
            return [
                CardCluster(
                    cluster_id=str(cluster["_id"]),
                    user_id=str(cluster["user_id"]),
                    centroid_vector=cluster.get("centroid_vector", []),
                    knowledge_card_ids=[
                        str(card_id) for card_id in cluster.get("knowledge_card_ids", [])
                    ],
                    topic_name=cluster.get("topic_name","Misc")
                )
                for cluster in clusters
            ]
        except Exception as exception:
            print(f"error getting clusters: {exception}")
            return []