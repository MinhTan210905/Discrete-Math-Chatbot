"""
brain_traditional.py - Hybrid Multi-layer Retrieval System
============================================================
Layer 1: TF-IDF char n-gram       (lexical matching)
Layer 2: Sentence Transformers    (multilingual semantic embeddings)
Layer 3: Character-level BiGRU    (sequential character encoding - PyTorch)

Requirements: scikit-learn, sentence-transformers, torch (included with sentence-transformers)
"""

import sys
import json
import os
import numpy as np
from pathlib import Path

# ── Layer 1: TF-IDF ─────────────────────────────────────────────────────────
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# ── Layer 2 + 3: Sentence Transformers + PyTorch BiGRU ──────────────────────
try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# ── Config ───────────────────────────────────────────────────────────────────
DATA_DIR    = Path(__file__).resolve().parent
CORPUS_PATH = DATA_DIR / "traditional_corpus.json"
ST_CACHE    = DATA_DIR / "trad_st_cache.npy"
GRU_CACHE   = DATA_DIR / "trad_gru_cache.npy"

ST_MODEL    = "paraphrase-multilingual-MiniLM-L12-v2"
W_TFIDF     = 0.25
W_EMBED     = 0.55
W_GRU       = 0.20
THRESHOLD   = 0.12
MAX_CHAR    = 128

# ── BiGRU Model ──────────────────────────────────────────────────────────────
class CharBiGRU(nn.Module):
    """2-layer Character-level BiGRU sentence encoder."""
    def __init__(self, vocab_size, embed_dim=32, hidden_dim=64):
        super().__init__()
        self.emb  = nn.Embedding(vocab_size + 1, embed_dim, padding_idx=0)
        self.gru  = nn.GRU(embed_dim, hidden_dim, num_layers=2,
                           batch_first=True, bidirectional=True, dropout=0.0)
        self.out_dim = hidden_dim * 2

    def forward(self, ids):
        x = self.emb(ids)                          # (B, T, E)
        o, _ = self.gru(x)                         # (B, T, H*2)
        mask  = (ids != 0).float().unsqueeze(-1)   # (B, T, 1)
        pooled = (o * mask).sum(1) / mask.sum(1).clamp(min=1)
        return pooled                               # (B, H*2)

# ── Helper functions ──────────────────────────────────────────────────────────
def cosine_batch(q, matrix):
    qn = np.linalg.norm(q)
    if qn == 0:
        return np.zeros(len(matrix))
    mn = np.linalg.norm(matrix, axis=1, keepdims=True)
    mn = np.where(mn == 0, 1, mn)
    return (matrix / mn) @ (q / qn)

def build_vocab(texts):
    chars = set()
    for t in texts:
        chars.update(t.lower())
    return {c: i + 1 for i, c in enumerate(sorted(chars))}

def to_ids(text, vocab, max_len=MAX_CHAR):
    ids = [vocab.get(c, 0) for c in text.lower()[:max_len]]
    return ids + [0] * (max_len - len(ids))

def gru_encode(model, vocab, texts, batch=32):
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch):
            ids = torch.tensor([to_ids(t, vocab) for t in texts[i:i+batch]], dtype=torch.long)
            out.append(model(ids).numpy())
    return np.vstack(out)

def load_cache(path, key):
    if path.exists():
        try:
            d = np.load(str(path), allow_pickle=True).item()
            if d.get("key") == key:
                return d["data"]
        except Exception:
            pass
    return None

def save_cache(path, key, data):
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

    documents  = [item["question"] for item in corpus]
    n          = len(documents)
    cache_key  = str(n)
    scores     = np.zeros(n)
    layers     = []

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
            st_model = SentenceTransformer(ST_MODEL)
            corpus_st = load_cache(ST_CACHE, cache_key)
            if corpus_st is None:
                corpus_st = st_model.encode(documents, show_progress_bar=False, convert_to_numpy=True)
                save_cache(ST_CACHE, cache_key, corpus_st)
            query_st = st_model.encode([query], convert_to_numpy=True)[0]
            st_scores = cosine_batch(query_st, corpus_st)
            scores += W_EMBED * st_scores
            layers.append(f"sentence-transformers({ST_MODEL})")

        # ── Layer 3: Character-level BiGRU ────────────────────────────────
        if HAS_TORCH:
            torch.manual_seed(42)
            vocab    = build_vocab(documents + [query])
            gru      = CharBiGRU(vocab_size=len(vocab))
            corpus_gru = load_cache(GRU_CACHE, cache_key)
            if corpus_gru is None:
                corpus_gru = gru_encode(gru, vocab, documents)
                save_cache(GRU_CACHE, cache_key, corpus_gru)
            query_gru  = gru_encode(gru, vocab, [query])[0]
            gru_scores = cosine_batch(query_gru, corpus_gru)
            scores += W_GRU * gru_scores
            layers.append("char-bigru(2-layer)")

        if not layers:
            print(json.dumps({"reply": "Loi: Chua cai scikit-learn hoac sentence-transformers.", "mode": "traditional", "confidence": 0, "sources": []}))
            sys.exit(1)

        # Normalize weights
        w_sum = (W_TFIDF if HAS_SKLEARN else 0) + (W_EMBED if HAS_ST else 0) + (W_GRU if HAS_TORCH else 0)
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
                    {"title": corpus[i]["question"], "topic": corpus[i].get("topic", ""), "score": round(float(scores[i]), 4)}
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
