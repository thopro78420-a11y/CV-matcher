import re
import unicodedata
from typing import Iterable

from langdetect import detect


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9+.#/\\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_language(text: str) -> str:
    try:
        lang = detect(text[:5000])
        return "fr" if lang.startswith("fr") else "en"
    except Exception:
        return "unknown"


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def keyword_occurrences(text: str, keywords: Iterable[str]) -> dict[str, int]:
    normalized = normalize_text(text)
    occurrences: dict[str, int] = {}
    for kw in keywords:
        target = normalize_text(kw)
        if not target:
            continue
        occurrences[kw] = len(re.findall(rf"\b{re.escape(target)}\b", normalized))
    return occurrences
