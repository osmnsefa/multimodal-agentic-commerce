import io
import hashlib
import logging
import math
import random
import threading
from typing import Union, List, Optional, Any

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger(__name__)

class CLIPService:
    """
    Singleton CLIP Service generating 512-dimensional L2-normalized float embeddings
    for multimodal textual and visual search queries.
    """
    _instance: Optional["CLIPService"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "CLIPService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CLIPService, cls).__new__(cls)
                    cls._instance._model = None
                    cls._instance._fallback_mode = False
        return cls._instance

    def _get_model(self):
        if self._model is None and not self._fallback_mode:
            with self._lock:
                if self._model is None and not self._fallback_mode:
                    model_holder = []
                    def loader():
                        try:
                            from sentence_transformers import SentenceTransformer
                            try:
                                m = SentenceTransformer("clip-ViT-B-32", local_files_only=True)
                                model_holder.append(m)
                                return
                            except Exception:
                                pass
                            m = SentenceTransformer("clip-ViT-B-32")
                            model_holder.append(m)
                        except Exception as e:
                            logger.warning(f"SentenceTransformer load failed: {e}")

                    t = threading.Thread(target=loader, daemon=True)
                    t.start()
                    t.join(timeout=3.0)
                    if model_holder:
                        self._model = model_holder[0]
                    else:
                        logger.info("SentenceTransformer model offline or timed out. Using deterministic 512-dim unit vector fallback.")
                        self._fallback_mode = True
        return self._model

    def _generate_fallback_embedding(self, seed: Union[str, bytes]) -> List[float]:
        """
        Generates a deterministic 512-dim L2-normalized float vector
        when neural model weights are unreachable or in test environments.
        """
        raw_bytes = seed.encode("utf-8") if isinstance(seed, str) else seed
        digest = hashlib.sha256(raw_bytes).digest()
        seed_int = int.from_bytes(digest[:4], "big")

        if np is not None:
            rng = np.random.RandomState(seed_int)
            vec = rng.randn(512).astype(np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec.tolist()
        else:
            r = random.Random(seed_int)
            raw = [r.gauss(0, 1) for _ in range(512)]
            norm = math.sqrt(sum(x * x for x in raw))
            if norm > 0:
                return [round(x / norm, 6) for x in raw]
            return [0.0] * 512

    def get_text_embedding(self, text: str) -> List[float]:
        """
        Generate 512-dim L2-normalized float vector for text input.
        """
        model = self._get_model()
        if model is not None:
            try:
                embedding = model.encode(text, convert_to_numpy=True)
                if np is not None:
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
                    return embedding.tolist()
                else:
                    emb_list = list(embedding)
                    norm = math.sqrt(sum(x * x for x in emb_list))
                    return [x / norm for x in emb_list] if norm > 0 else emb_list
            except Exception as e:
                logger.error(f"Error encoding text with model: {e}")

        return self._generate_fallback_embedding(f"text:{text}")

    def get_image_embedding(self, image_input: Any) -> List[float]:
        """
        Generate 512-dim L2-normalized float vector for image input.
        """
        raw_bytes = b"dummy_image"
        try:
            if isinstance(image_input, bytes):
                raw_bytes = image_input
                image = Image.open(io.BytesIO(image_input)).convert("RGB") if Image is not None else None
            elif isinstance(image_input, str):
                raw_bytes = image_input.encode("utf-8")
                image = Image.open(image_input).convert("RGB") if Image is not None else None
            elif Image is not None and isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                raw_bytes = buf.getvalue()
            else:
                image = None

            model = self._get_model()
            if model is not None and image is not None:
                embedding = model.encode(image, convert_to_numpy=True)
                if np is not None:
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
                    return embedding.tolist()
                else:
                    emb_list = list(embedding)
                    norm = math.sqrt(sum(x * x for x in emb_list))
                    return [x / norm for x in emb_list] if norm > 0 else emb_list
        except Exception as e:
            logger.error(f"Error in image embedding: {e}")

        return self._generate_fallback_embedding(raw_bytes)

clip_service = CLIPService()
