"""
brain_traditional.py - Hybrid 2-layer Retrieval System
=======================================================
Layer 1: TF-IDF char n-gram (2-4)  — lexical matching        (weight: 35%)
Layer 2: Sentence Transformers      — multilingual semantic    (weight: 65%)

Requirements: scikit-learn, sentence-transformers
"""

import sys
import json
import numpy as np
from pathlib import Path

# ── Layer 1: TF-IDF ─────────────────────────────────────────────────────────
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# ── Layer 2: Sentence Transformers ───────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

# ── Config ───────────────────────────────────────────────────────────────────
DATA_DIR    = Path(__file__).resolve().parent
CORPUS_PATH = DATA_DIR / "traditional_corpus.json"
ST_CACHE    = DATA_DIR / "trad_st_cache.npy"

ST_MODEL    = "paraphrase-multilingual-MiniLM-L12-v2"
W_TFIDF     = 0.35
W_EMBED     = 0.65
THRESHOLD   = 0.12

# ── Helper functions ──────────────────────────────────────────────────────────
def cosine_batch(q, matrix):
    """Cosine similarity giữa vector q và từng hàng của matrix."""
    qn = np.linalg.norm(q)
    if qn == 0:
        return np.zeros(len(matrix))
    mn = np.linalg.norm(matrix, axis=1, keepdims=True)
    mn = np.where(mn == 0, 1, mn)
    return (matrix / mn) @ (q / qn)

def load_cache(path, key):
    """Đọc embedding cache từ file .npy nếu key khớp."""
    if path.exists():
        try:
            d = np.load(str(path), allow_pickle=True).item()
            if d.get("key") == key:
                return d["data"]
        except Exception:
            pass
    return None

def save_cache(path, key, data):
    """Lưu embedding cache ra file .npy."""
    try:
        np.save(str(path), {"key": key, "data": data})
    except Exception:
        pass

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(json.dumps({"reply": "Loi: Khong nhan duoc cau hoi.", "mode": "traditional", "confidence": 0, "sources": []}))
        sys.exit(1)

    query = sys.argv[1].strip()

    if not CORPUS_PATH.exists():
        print(json.dumps({"reply": "Loi: Khong tim thay traditional_corpus.json.", "mode": "traditional", "confidence": 0, "sources": []}))
        sys.exit(1)

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    if not corpus:
        print(json.dumps({"reply": "Du lieu trong.", "mode": "traditional", "confidence": 0, "sources": []}))
        sys.exit(0)

    documents = [item["question"] for item in corpus]
    n         = len(documents)
    cache_key = str(n)
    scores    = np.zeros(n)
    layers    = []

    try:
        # ── Layer 1: TF-IDF char n-gram ───────────────────────────────────
        if HAS_SKLEARN:
            vect = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1)
            mat  = vect.fit_transform(documents + [query])
            tfidf_scores = sklearn_cosine(mat[-1], mat[:-1]).flatten()
            scores += W_TFIDF * tfidf_scores
            layers.append("tfidf-char-ngram")

        # ── Layer 2: Sentence Transformer embeddings ──────────────────────
        if HAS_ST:
            st_model  = SentenceTransformer(ST_MODEL)
            corpus_st = load_cache(ST_CACHE, cache_key)
            if corpus_st is None:
                corpus_st = st_model.encode(documents, show_progress_bar=False, convert_to_numpy=True)
                save_cache(ST_CACHE, cache_key, corpus_st)
            query_st  = st_model.encode([query], convert_to_numpy=True)[0]
            st_scores = cosine_batch(query_st, corpus_st)
            scores   += W_EMBED * st_scores
            layers.append(f"sentence-transformers({ST_MODEL})")

        if not layers:
            print(json.dumps({"reply": "Loi: Chua cai scikit-learn hoac sentence-transformers.", "mode": "traditional", "confidence": 0, "sources": []}))
            sys.exit(1)

        # Chuẩn hóa theo trọng số thực tế (phòng trường hợp 1 layer bị thiếu)
        w_sum = (W_TFIDF if HAS_SKLEARN else 0) + (W_EMBED if HAS_ST else 0)
        if w_sum > 0:
            scores /= w_sum

        best_idx   = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        top3       = np.argsort(scores)[::-1][:3]

        if best_score > THRESHOLD:
            result = {
                "reply":      corpus[best_idx]["answer"],
                "mode":       "traditional",
                "confidence": round(best_score, 4),
                "sources": [
                    {
                        "title": corpus[i]["question"],
                        "topic": corpus[i].get("topic", ""),
                        "score": round(float(scores[i]), 4),
                    }
                    for i in top3 if float(scores[i]) > THRESHOLD * 0.5
                ],
                "provider": " + ".join(layers),
            }
        else:
            result = {
                "reply":      "Xin loi, toi khong tim thay cau tra loi phu hop trong du lieu.",
                "mode":       "traditional",
                "confidence": round(best_score, 4),
                "sources":    [],
                "provider":   " + ".join(layers),
            }

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"reply": f"Loi xu ly: {str(e)}", "mode": "traditional", "confidence": 0, "sources": []}))
        sys.exit(1)

if __name__ == "__main__":
    main()
