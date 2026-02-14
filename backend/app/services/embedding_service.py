import hashlib
import math


class EmbeddingService:
    def embed(self, text: str, size: int = 64) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [((digest[i % len(digest)] / 255.0) * 2 - 1) for i in range(size)]
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))
