import requests
from retry import retry
from config import Config

class Embedder:
    """Class to handle text embedding using Hugging Face API."""

    def __init__(self):
        """Initialize API URL and authentication token."""

        # exposing here because config is not working (saved in .env as HF_MODEL_ID, HF_TOKEN)
        self.model_id = Config.HF_MODEL_ID
        self.hf_token = Config.HF_TOKEN

        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}

    @retry(tries=3, delay=10)
    def embed_text(self, texts):
        """
        Usage:Sends input text(s) to the Hugging Face API for embedding.
        Parameters:
            texts (str or list of str): The text(s) to be embedded.
        Returns:
            list: The embedding vectors.
        """
        response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts})
        result = response.json()

        if isinstance(result, list):
            return result
        elif "error" in result:
            raise RuntimeError("The model is currently loading, please re-run the query.")