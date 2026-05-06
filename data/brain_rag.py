"""
brain_rag.py - Advanced 3-Phase RAG Pipeline
=============================================
Phase 1 | Pre-retrieval  : Query Expansion (LLM sinh sub-queries)
Phase 2 | Retrieval      : Semantic Vector Search (sentence-transformers)
Phase 3 | Post-retrieval : Cross-Encoder Re-ranking + LLM Generation

Requirements: openai, sentence-transformers (includes torch, numpy)
"""

import sys
import json
import os
import re
import numpy as np
from pathlib import Path

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    HAS_ST = True
except ImportError:
    HAS_ST = False

# ── Config ───────────────────────────────────────────────────────────────────
DATA_DIR         = Path(__file__).resolve().parent
CORPUS_PATH      = DATA_DIR / "retrieval_corpus.json"   # Q&A pairs
PDF_CORPUS_PATH  = DATA_DIR / "pdf_corpus.json"          # PDF chunks (optional)
EMBED_CACHE      = DATA_DIR / "rag_embed_cache.npy"

EMBED_MODEL        = "paraphrase-multilingual-MiniLM-L12-v2"
CROSS_ENC_MODEL    = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"  # multilingual

TOP_K_RETRIEVAL    = 15   # Lấy top 15 từ vector search (gom từ tất cả sub-queries)
TOP_K_RERANK       = 4    # Giữ lại top 4 sau cross-encoder
MAX_CONTEXT_CHARS  = 3000 # Giới hạn context gửi vào LLM

# ── Helpers ───────────────────────────────────────────────────────────────────
def cosine_batch(q, matrix):
    qn = np.linalg.norm(q)
    if qn == 0:
        return np.zeros(len(matrix))
    mn = np.linalg.norm(matrix, axis=1, keepdims=True)
    mn = np.where(mn == 0, 1, mn)
    return (matrix / mn) @ (q / qn)

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

def extract_json(text):
    """Trích xuất JSON từ response LLM (có thể kèm markdown code block)."""
    text = text.strip()
    # Bỏ markdown ```json ... ```
    text = re.sub(r"```(?:json)?", "", text).strip("`").strip()
    try:
        return json.loads(text)
    except Exception:
        return None

# ── Phase 1: Query Expansion ──────────────────────────────────────────────────
def expand_query(client, query, chat_model):
    """
    Dùng LLM sinh 3 sub-queries để mở rộng phạm vi tìm kiếm.
    Fallback về [query] nếu LLM không trả JSON hợp lệ.
    """
    prompt = (
        f'Bạn là chuyên gia Toán Rời Rạc. Câu hỏi gốc: "{query}"\n'
        "Hãy sinh ra đúng 3 sub-query ngắn (từ khóa/câu hỏi phụ) để tìm kiếm "
        "thông tin liên quan trong tài liệu giáo trình.\n"
        'Trả về JSON: {"sub_queries": ["query1", "query2", "query3"]}\n'
        "Chỉ trả về JSON, không giải thích thêm."
    )
    try:
        resp = client.chat.completions.create(
            model=chat_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        data = extract_json(resp.choices[0].message.content)
        if data and isinstance(data.get("sub_queries"), list):
            sub_qs = [q for q in data["sub_queries"] if q and q != query][:3]
            return [query] + sub_qs
    except Exception:
        pass
    return [query]  # Fallback

# ── Phase 2: Vector Search ────────────────────────────────────────────────────
def vector_search(embed_model, corpus, corpus_embeddings, queries, top_k=15):
    """
    Encode từng sub-query → tính cosine similarity với corpus embeddings
    → lấy union top-K, dedup theo idx, sort theo score giảm dần.
    """
    seen  = {}  # idx → best score
    for q in queries:
        q_emb = embed_model.encode([q], convert_to_numpy=True)[0]
        sims  = cosine_batch(q_emb, corpus_embeddings)
        top_idx = np.argsort(sims)[::-1][:top_k]
        for idx in top_idx:
            score = float(sims[idx])
            if score > 0.05:  # Lọc bỏ kết quả quá thấp
                if idx not in seen or score > seen[idx]["score"]:
                    seen[idx] = {"idx": int(idx), "doc": corpus[idx], "score": score}

    results = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# ── Phase 3a: Cross-Encoder Re-ranking ────────────────────────────────────────
def rerank(cross_encoder, query, candidates, top_k=4):
    """
    Cross-encoder chấm điểm lại từng cặp (query, content).
    Chính xác hơn bi-encoder vì xem xét tương tác trực tiếp giữa 2 văn bản.
    """
    if not candidates:
        return []
    pairs  = [(query, c["doc"].get("content", "")[:512]) for c in candidates]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(scores, candidates), key=lambda x: float(x[0]), reverse=True)
    return [c for _, c in ranked[:top_k]]

# ── Phase 3b: LLM Generation ──────────────────────────────────────────────────
def generate_answer(client, chat_model, query, top_docs, history):
    """
    Ghép top_docs làm context → tạo prompt → LLM sinh câu trả lời.
    """
    # Xây context từ top docs
    context_parts = []
    total_chars   = 0
    for i, d in enumerate(top_docs):
        chunk = d["doc"].get("content", "")
        if total_chars + len(chunk) > MAX_CONTEXT_CHARS:
            chunk = chunk[: MAX_CONTEXT_CHARS - total_chars]
        context_parts.append(f"[Tài liệu {i+1}]\n{chunk}")
        total_chars += len(chunk)
        if total_chars >= MAX_CONTEXT_CHARS:
            break

    context = "\n\n---\n\n".join(context_parts)

    system_msg = (
        "Bạn là trợ giảng môn Toán Rời Rạc. "
        "Dựa VÀO các tài liệu tham khảo bên dưới, hãy trả lời câu hỏi của sinh viên "
        "một cách rõ ràng, chính xác, có cấu trúc. "
        "Nếu tài liệu không đủ thông tin, hãy nói rõ là không tìm thấy.\n\n"
        f"TÀI LIỆU THAM KHẢO:\n{context}"
    )

    messages = [{"role": "system", "content": system_msg}]
    # Thêm lịch sử hội thoại (tối đa 4 lượt gần nhất)
    for msg in history[-8:]:
        role = msg.get("role", "user")
        text = msg.get("text", "")
        if role in ("user", "assistant") and text:
            messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": query})

    resp = client.chat.completions.create(
        model=chat_model,
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(json.dumps({"reply": "Loi: Khong nhan duoc cau hoi.", "mode": "rag",
                          "confidence": 0, "sources": [], "provider": "error"}))
        sys.exit(1)

    query        = sys.argv[1].strip()
    history_raw  = sys.argv[2] if len(sys.argv) > 2 else "[]"
    try:
        history = json.loads(history_raw)
    except Exception:
        history = []

    # Kiểm tra API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(json.dumps({"reply": "Loi: Chua cau hinh OPENAI_API_KEY trong moi truong.",
                          "mode": "rag", "confidence": 0, "sources": [], "provider": "error"}))
        sys.exit(1)

    base_url   = os.environ.get("OPENAI_BASE_URL") or None
    chat_model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    client     = OpenAI(api_key=api_key, base_url=base_url)

    if not CORPUS_PATH.exists():
        print(json.dumps({"reply": "Loi: Khong tim thay retrieval_corpus.json.",
                          "mode": "rag", "confidence": 0, "sources": [], "provider": "error"}))
        sys.exit(1)

    if not CORPUS_PATH.exists():
        print(json.dumps({"reply": "Loi: Khong tim thay retrieval_corpus.json.",
                          "mode": "rag", "confidence": 0, "sources": [], "provider": "error"}))
        sys.exit(1)

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    # Load PDF corpus nếu có (merge vào corpus chính)
    if PDF_CORPUS_PATH.exists():
        with open(PDF_CORPUS_PATH, "r", encoding="utf-8") as f:
            pdf_chunks = json.load(f)
        corpus = corpus + pdf_chunks

    cache_key = str(len(corpus))

    try:
        if not HAS_ST:
            raise ImportError("Chua cai sentence-transformers. Chay: pip install sentence-transformers")

        # Load embedding model + corpus embeddings (có cache)
        embed_model   = SentenceTransformer(EMBED_MODEL)
        corpus_embeds = load_cache(EMBED_CACHE, cache_key)
        if corpus_embeds is None:
            texts         = [doc.get("content", "") for doc in corpus]
            corpus_embeds = embed_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            save_cache(EMBED_CACHE, cache_key, corpus_embeds)

        # ── Phase 1: Query Expansion ──────────────────────────────────────
        queries = expand_query(client, query, chat_model)

        # ── Phase 2: Vector Search (top 15 dedup) ─────────────────────────
        candidates = vector_search(embed_model, corpus, corpus_embeds, queries, top_k=TOP_K_RETRIEVAL)

        # ── Phase 3a: Cross-Encoder Re-ranking ────────────────────────────
        cross_encoder = CrossEncoder(CROSS_ENC_MODEL)
        top_docs      = rerank(cross_encoder, query, candidates, top_k=TOP_K_RERANK)
        if not top_docs:
            top_docs = candidates[:TOP_K_RERANK]

        # ── Phase 3b: LLM Generation ──────────────────────────────────────
        reply   = generate_answer(client, chat_model, query, top_docs, history)
        sources = [
            {"title": d["doc"].get("title", ""), "topic": d["doc"].get("topic", "")}
            for d in top_docs
        ]
        top_score = round(float(top_docs[0]["score"]) if top_docs else 0.5, 4)

        print(json.dumps({
            "reply":      reply,
            "mode":       "rag",
            "confidence": top_score,
            "sources":    sources,
            "provider":   f"query-expansion + vector-search({EMBED_MODEL}) + cross-encoder({CROSS_ENC_MODEL}) + {chat_model}",
        }))

    except Exception as e:
        print(json.dumps({
            "reply":      f"Loi RAG: {str(e)}",
            "mode":       "rag",
            "confidence": 0,
            "sources":    [],
            "provider":   "error",
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
