import numpy as np
from sentence_transformers import SentenceTransformer

from .interfaces import TextEmbedder


class SBERTEmbedder(TextEmbedder):
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(text)
