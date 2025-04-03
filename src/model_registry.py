from qdrant_client import QdrantClient

from embedders.interfaces import TextEmbedder
from embedders.one_peace_embedder import OnePeaceMultimodalEmbedder


class ModelRegistry:
    def __init__(self,
                 text_embedder: TextEmbedder,
                 one_peace_embedder: OnePeaceMultimodalEmbedder,
                 qdrant_client: QdrantClient):
        self.text_embedder = text_embedder
        self.one_peace_embedder = one_peace_embedder
        self.qdrant_client = qdrant_client
