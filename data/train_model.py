from __future__ import annotations

import hashlib
import json
import math
import os
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request


DATA_DIR = Path(__file__).resolve().parent
CORPUS_PATH = DATA_DIR / "retrieval_corpus.json"
MODEL_PATH = DATA_DIR / "discrete_math_model.json"

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
SEMANTIC_DIMENSIONS = 256
EMBEDDING_BATCH_SIZE = 32
EMBEDDING_TIMEOUT = 90

STOPWORDS = {
    "a",
    "ai",
    "anh",
    "ba",
    "bai",
    "ban",
    "bao",
    "bay",
    "bi",
    "biet",
    "boi",
    "cac",
    "can",
    "cang",
    "cau",
    "cauhoi",
    "chi",
    "cho",
    "co",
    "con",
    "cua",
    "cung",
    "da",
    "dang",
    "de",
    "den",
    "di",
    "do",
    "doi",
    "duoc",
    "giai",
    "gi",
    "giai_thich",
    "gom",
    "hay",
    "hoi",
    "hoc",
    "kha",
    "khi",
    "khong",
    "la",
    "lai",
    "lam",
    "len",
    "loai",
    "luon",
    "ma",
    "mau",
    "menhde",
    "minh",
    "mot",
    "neu",
    "nhat",
    "nhieu",
    "nhung",
    "nho",
    "noi",
    "noi_dung",
    "o",
    "phan",
    "phai",
    "phep",
    "ra",
    "rang",
    "roi",
    "sao",
    "sau",
    "se",
    "so",
    "suy",
    "ta",
    "tai",
    "the",
    "theo",
    "thi",
    "thu",
    "thuoc",
    "toi",
    "tra",
    "trinh",
    "tro",
    "trong",
    "tu",
    "tu_luan",
    "va",
    "vao",
    "ve",
    "vi",
    "vi_du",
    "voi",
    "xac",
    "xacdinh",
}


def load_corpus() -> list[dict]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    lowered = text.lower().replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", lowered)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", without_marks)
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = normalized.split()
    return [token for token in tokens if token and token not in STOPWORDS]


def build_document_text(document: dict) -> str:
    return document.get("retrieval_text") or "\n".join(
        part
        for part in [
            document.get("topic", ""),
            document.get("kind", ""),
            document.get("title", ""),
            document.get("normalized_content") or document.get("content", ""),
            " ".join(document.get("keywords") or []),
        ]
        if part
    )


def compute_idf(documents: list[list[str]], vocabulary: dict[str, int]) -> list[float]:
    document_count = len(documents)
    doc_frequency = [0] * len(vocabulary)
    for tokens in documents:
        for token in set(tokens):
            doc_frequency[vocabulary[token]] += 1
    return [math.log((1 + document_count) / (1 + df)) + 1 for df in doc_frequency]


def vectorize_tokens(tokens: list[str], vocabulary: dict[str, int], idf: list[float]) -> list[list[float]]:
    counts = Counter(token for token in tokens if token in vocabulary)
    if not counts:
        return []

    weights = []
    norm = 0.0
    for token, count in counts.items():
        idx = vocabulary[token]
        tf = 1 + math.log(count)
        weight = tf * idf[idx]
        weights.append([idx, weight])
        norm += weight * weight

    norm = math.sqrt(norm) or 1.0
    return [[idx, round(weight / norm, 8)] for idx, weight in sorted(weights)]


def semantic_ngrams(text: str, size: int = 3) -> list[str]:
    normalized = f" {normalize_text(text)} "
    if len(normalized) < size:
        return [normalized.strip()] if normalized.strip() else []
    return [normalized[idx : idx + size] for idx in range(len(normalized) - size + 1)]


def stable_hash(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")


def build_semantic_vector(text: str, dimensions: int = SEMANTIC_DIMENSIONS) -> list[float]:
    grams = semantic_ngrams(text)
    if not grams:
        return []

    counts = Counter(grams)
    vector = [0.0] * dimensions
    for gram, count in counts.items():
        index = stable_hash(gram) % dimensions
        sign = 1.0 if stable_hash(f"sign::{gram}") % 2 == 0 else -1.0
        vector[index] += sign * count

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 8) for value in vector]


def fetch_openai_embeddings(texts: list[str], model: str) -> list[list[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []

    url = "https://api.openai.com/v1/embeddings"
    embeddings = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        payload = json.dumps(
            {
                "model": model,
                "input": batch,
                "encoding_format": "float",
            }
        ).encode("utf-8")
        req = request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=EMBEDDING_TIMEOUT) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Embedding request failed: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Embedding request failed: {exc.reason}") from exc

        data = sorted(parsed["data"], key=lambda item: item["index"])
        embeddings.extend(item["embedding"] for item in data)
        print(f"Embedded {min(len(texts), start + len(batch))}/{len(texts)} documents...")

    return embeddings


def main() -> None:
    corpus = load_corpus()
    document_texts = [build_document_text(document) for document in corpus]
    documents = [tokenize(text) for text in document_texts]
    vocabulary = {
        token: idx
        for idx, token in enumerate(sorted({token for doc in documents for token in doc}))
    }
    idf = compute_idf(documents, vocabulary)

    semantic_vectors = [build_semantic_vector(text) for text in document_texts]

    embedding_vectors: list[list[float]] = []
    embedding_enabled = False
    embedding_error = None
    if os.getenv("OPENAI_API_KEY"):
        try:
            embedding_vectors = fetch_openai_embeddings(document_texts, EMBEDDING_MODEL)
            embedding_enabled = len(embedding_vectors) == len(corpus)
        except Exception as exc:  # pragma: no cover - diagnostic path
            embedding_error = str(exc)
            embedding_vectors = []
            print(f"Warning: {embedding_error}")

    entries = []
    for index, (document, lexical_tokens, semantic_vector) in enumerate(
        zip(corpus, documents, semantic_vectors)
    ):
        entry = {
            "id": document["id"],
            "topic": document["topic"],
            "kind": document["kind"],
            "title": document.get("title") or document["id"],
            "content": document.get("content") or "",
            "normalized_content": document.get("normalized_content") or document.get("content") or "",
            "keywords": document.get("keywords") or [],
            "difficulty": document.get("difficulty") or "mixed",
            "source_group": document.get("source_group") or "core",
            "quality_score": document.get("quality_score") or 1.0,
            "source_question_ids": document.get("source_question_ids") or [],
            "linked_questions": document.get("linked_questions") or [],
            "source_file": document.get("source_file") or None,
            "source_page": document.get("source_page") or None,
            "vector": vectorize_tokens(lexical_tokens, vocabulary, idf),
            "semantic_vector": semantic_vector,
            "embedding": embedding_vectors[index] if embedding_enabled else None,
        }
        entries.append(entry)

    payload = {
        "model_type": "hybrid_retrieval_index",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "document_count": len(corpus),
        "vocabulary_size": len(vocabulary),
        "semantic_dimensions": SEMANTIC_DIMENSIONS,
        "embedding": {
            "enabled": embedding_enabled,
            "model": EMBEDDING_MODEL if embedding_enabled else None,
            "dimensions": len(embedding_vectors[0]) if embedding_enabled and embedding_vectors else 0,
            "error": embedding_error,
        },
        "weights": {
            "lexical": 0.45,
            "semantic": 0.25,
            "embedding": 0.30,
        },
        "thresholds": {
            "high": 0.52,
            "medium": 0.34,
            "fallback": 0.18,
        },
        "stopwords": sorted(STOPWORDS),
        "vocabulary": vocabulary,
        "idf": [round(value, 8) for value in idf],
        "entries": entries,
    }

    MODEL_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "Built retrieval index: "
        f"{len(corpus)} docs, {len(vocabulary)} vocabulary terms, "
        f"embedding_enabled={embedding_enabled}."
    )


if __name__ == "__main__":
    main()
