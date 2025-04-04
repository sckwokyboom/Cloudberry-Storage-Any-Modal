from qdrant_client import QdrantClient

from embedders.interfaces import TextEmbedder
from embedders.one_peace_client import OnePeaceClient


class ModelRegistry:
    def __init__(self,
                 text_embedder: TextEmbedder,
                 one_peace_client: OnePeaceClient,
                 qdrant_client: QdrantClient):
        self.text_embedder = text_embedder
        self.one_peace_client = one_peace_client
        self.qdrant_client = qdrant_client
