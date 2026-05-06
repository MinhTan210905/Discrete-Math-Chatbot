"""
prepare_pdf_corpus.py - PDF Semantic Chunking
=============================================
Đọc các file PDF trong thư mục data/pdfs/
→ Trích xuất text theo từng trang
→ Semantic Chunking: cắt tại điểm cosine similarity giảm mạnh
→ Xuất ra data/pdf_corpus.json

Usage:
    python data/prepare_pdf_corpus.py

Requirements: pymupdf, sentence-transformers, numpy
"""

import json
import re
import sys
import numpy as np
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    print("Chua cai PyMuPDF. Chay: pip install pymupdf")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Chua cai sentence-transformers. Chay: pip install sentence-transformers")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR    = Path(__file__).resolve().parent
PDF_DIR     = DATA_DIR / "pdfs"
OUTPUT_PATH = DATA_DIR / "pdf_corpus.json"

EMBED_MODEL        = "paraphrase-multilingual-MiniLM-L12-v2"
SIMILARITY_THRESH  = 0.45   # Ngưỡng cosine: drop xuống dưới đây → cắt chunk mới
MIN_CHUNK_CHARS    = 100    # Chunk tối thiểu N ký tự
MAX_CHUNK_CHARS    = 1200   # Chunk tối đa N ký tự (tránh quá dài)
SENTENCE_WINDOW    = 3      # Số câu gom lại để tính embedding đại diện

# ── Text extraction ───────────────────────────────────────────────────────────
def extract_pages(pdf_path: Path) -> list[dict]:
    """Trích xuất text từng trang của PDF."""
    doc   = fitz.open(str(pdf_path))
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": page_num, "text": text})
    doc.close()
    return pages

def split_sentences(text: str) -> list[str]:
    """Tách text thành câu, lọc câu quá ngắn."""
    # Tách theo dấu chấm, chấm hỏi, chấm than, xuống dòng kép
    raw = re.split(r"(?<=[.!?])\s+|(?:\n\s*\n)", text)
    sentences = []
    for s in raw:
        s = s.strip().replace("\n", " ")
        s = re.sub(r"\s{2,}", " ", s)
        if len(s) >= 20:  # Bỏ câu quá ngắn
            sentences.append(s)
    return sentences

# ── Semantic Chunking ─────────────────────────────────────────────────────────
def cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def semantic_chunk(sentences: list[str], model: SentenceTransformer,
                   source_name: str, source_page: int = 0) -> list[dict]:
    """
    Semantic Chunking:
    1. Encode từng câu
    2. So sánh embedding của nhóm câu hiện tại vs nhóm câu tiếp theo
    3. Khi similarity < THRESHOLD → cắt chunk mới
    """
    if not sentences:
        return []

    embeddings = model.encode(sentences, show_progress_bar=False, convert_to_numpy=True)
    chunks     = []
    current    = [sentences[0]]
    current_emb = embeddings[0].copy()

    for i in range(1, len(sentences)):
        # Embedding đại diện = trung bình SENTENCE_WINDOW câu gần nhất trong chunk
        window_embs = embeddings[max(0, i - SENTENCE_WINDOW) : i]
        current_rep = window_embs.mean(axis=0)
        sim = cosine(current_rep, embeddings[i])

        current_text = " ".join(current)

        # Cắt chunk nếu:
        # (a) similarity quá thấp (chủ đề đổi)
        # (b) chunk hiện tại đã quá dài
        if (sim < SIMILARITY_THRESH or len(current_text) >= MAX_CHUNK_CHARS) \
                and len(current_text) >= MIN_CHUNK_CHARS:
            chunks.append(current_text)
            current     = [sentences[i]]
            current_emb = embeddings[i].copy()
        else:
            current.append(sentences[i])

    # Thêm phần còn lại
    if current:
        tail = " ".join(current)
        if len(tail) >= MIN_CHUNK_CHARS:
            chunks.append(tail)
        elif chunks:
            chunks[-1] += " " + tail  # Gộp vào chunk trước nếu quá ngắn

    # Chuyển thành dict chuẩn
    result = []
    for idx, chunk in enumerate(chunks):
        result.append({
            "id":       f"pdf_{source_name}_p{source_page}_c{idx}",
            "topic":    "pdf_document",
            "kind":     "pdf_chunk",
            "title":    f"{source_name} — trang {source_page}, đoạn {idx + 1}",
            "content":  chunk,
            "source":   source_name,
            "page":     source_page,
        })
    return result

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not PDF_DIR.exists():
        PDF_DIR.mkdir(parents=True)
        print(f"Da tao thu muc: {PDF_DIR}")
        print("Hay them file PDF vao thu muc do roi chay lai script nay.")
        return

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"Khong tim thay file PDF nao trong: {PDF_DIR}")
        print("Hay them file PDF roi chay lai.")
        return

    print(f"Tim thay {len(pdf_files)} file PDF.")
    print(f"Dang tai model embedding: {EMBED_MODEL} ...")
    model = SentenceTransformer(EMBED_MODEL)

    all_chunks = []
    for pdf_path in pdf_files:
        source_name = pdf_path.stem  # Ten file khong co duoi
        print(f"\nDang xu ly: {pdf_path.name}")
        pages = extract_pages(pdf_path)
        print(f"  → {len(pages)} trang co noi dung")

        for page_data in pages:
            sentences = split_sentences(page_data["text"])
            if not sentences:
                continue
            chunks = semantic_chunk(sentences, model,
                                    source_name=source_name,
                                    source_page=page_data["page"])
            all_chunks.extend(chunks)

        print(f"  → Da tao {sum(1 for c in all_chunks if c['source'] == source_name)} chunks")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nHoan tat! Tong cong {len(all_chunks)} chunks.")
    print(f"Luu tai: {OUTPUT_PATH}")
    print("\nTiep theo: khoi dong lai backend de brain_rag.py tai du lieu moi.")

if __name__ == "__main__":
    main()
