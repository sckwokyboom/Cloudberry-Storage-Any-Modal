from abc import ABC, abstractmethod

import numpy as np
from PIL import Image


class TextEmbedder(ABC):
    @abstractmethod
    def encode_text(self, text: str) -> np.ndarray:
        pass


class ImageEmbedder(ABC):
    @abstractmethod
    def encode_image(self, image: Image.Image) -> np.ndarray:
        pass


class AudioEmbedder(ABC):
    @abstractmethod
    def encode_audio(self, waveform: np.ndarray, sr: int) -> np.ndarray:
        pass
