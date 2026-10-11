import io
import threading
from typing import Union, List
from PIL import Image
import numpy as np

class CLIPService:
    """
    Singleton CLIP Service using SentenceTransformers for visual & textual 512-dim embeddings.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CLIPService, cls).__new__(cls)
                    cls._instance._model = None
        return cls._instance

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from sentence_transformers import SentenceTransformer
                    # clip-ViT-B-32 maps to openai/clip-vit-base-patch32 with 512 dim embeddings
                    self._model = SentenceTransformer("clip-ViT-B-32")
        return self._model

    def get_text_embedding(self, text: str) -> List[float]:
        """
        Generate 512-dim L2-normalized float vector for text input.
        """
        model = self._get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()

    def get_image_embedding(self, image_input: Union[bytes, str, Image.Image]) -> List[float]:
        """
        Generate 512-dim L2-normalized float vector for image input.
        """
        model = self._get_model()
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, str):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise ValueError("Unsupported image input type")

        embedding = model.encode(image, convert_to_numpy=True)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()

clip_service = CLIPService()
