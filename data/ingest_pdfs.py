from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = DATA_DIR / "pdf_corpus.json"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 180

FORMULA_REPLACEMENTS = [
    ("", " or "),
    ("∨", " or "),
    ("", " and "),
    ("∧", " and "),
    ("", " not "),
    ("¬", " not "),
    ("→", " -> "),
    ("⇒", " -> "),
    ("↔", " <-> "),
    ("⇔", " <-> "),
    ("∪", " union "),
    ("∩", " intersection "),
    ("⊆", " subseteq "),
    ("⊂", " subset "),
    ("⊇", " superseteq "),
    ("⊃", " superset "),
    ("∈", " in "),
    ("∉", " not in "),
    ("∀", " voi moi "),
    ("∃", " ton tai "),
    ("≤", " <= "),
    ("≥", " >= "),
    ("≠", " != "),
]

ACADEMIC_HINTS = [
    "tập hợp",
    "tập con",
    "logic",
    "mệnh đề",
    "suy diễn",
    "quan hệ",
    "hàm",
    "tổ hợp",
    "chỉnh hợp",
    "đồ thị",
    "cây",
    "truy hồi",
    "boole",
    "định nghĩa",
    "định lý",
    "ví dụ",
    "bài tập",
    "chứng minh",
    "poset",
    "hasse",
]

DROP_HINTS = [
    "mục lục",
    "nhà xuất bản",
    "đại học sư phạm",
    "khoa công nghệ thông tin",
    "tài liệu tham khảo",
]


def slugify(value: str) -> str:
    cleaned = value.lower()
    cleaned = cleaned.replace("đ", "d")
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    return cleaned.strip("_") or "doc"


def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\r", "\n")
    for source, target in FORMULA_REPLACEMENTS:
        cleaned = cleaned.replace(source, target)
    cleaned = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[\t ]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    return cleaned.strip()


def estimate_quality_score(text: str) -> float:
    if not text:
        return 0.0
    length = max(1, len(text))
    weird_symbol_count = sum(1 for ch in text if ch in {"", "", "", "�"})
    alnum_count = sum(1 for ch in text if ch.isalnum())
    score = (alnum_count / length) - (weird_symbol_count / length) * 8
    if len(text) < 120:
        score -= 0.2
    return max(0.0, min(1.0, round(score, 4)))


def is_academic_text(text: str) -> bool:
    lowered = normalize_text(text).lower()
    if any(hint in lowered for hint in DROP_HINTS):
        return False
    hint_hits = sum(1 for hint in ACADEMIC_HINTS if hint in lowered)
    if hint_hits >= 2:
        return True
    return len(lowered.split()) >= 45 and hint_hits >= 1


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}".strip()
            continue

        if current:
            chunks.append(current)
        current = para

    if current:
        chunks.append(current)

    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= size:
            final_chunks.append(chunk)
            continue

        words = chunk.split()
        start = 0
        while start < len(words):
            piece = " ".join(words[start : start + size // 6])
            if piece:
                final_chunks.append(piece)
            start += max(1, (size - overlap) // 6)

    return final_chunks


def extract_pdf(path: Path) -> list[dict]:
    reader = PdfReader(str(path))
    file_stem = path.stem
    file_slug = slugify(file_stem)
    documents = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = normalize_text(page.extract_text() or "")
        if not text or not is_academic_text(text):
            continue

        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk_index, chunk in enumerate(chunks, start=1):
            normalized_content = normalize_text(chunk)
            quality_score = estimate_quality_score(normalized_content)
            if not normalized_content or quality_score < 0.35 or not is_academic_text(normalized_content):
                continue

            documents.append(
                {
                    "id": f"pdf::{file_slug}::p{page_index:03d}::c{chunk_index:02d}",
                    "topic": file_stem,
                    "kind": "pdf_chunk",
                    "title": f"{file_stem} trang {page_index}",
                    "content": normalized_content,
                    "normalized_content": normalized_content,
                    "keywords": [],
                    "difficulty": "mixed",
                    "source_group": "pdf",
                    "quality_score": quality_score,
                    "source_file": str(path),
                    "source_page": page_index,
                    "chunk_index": chunk_index,
                }
            )

    return documents


def main(argv: list[str]) -> None:
    if len(argv) == 0:
        raise SystemExit("Usage: python data/ingest_pdfs.py <file1.pdf> <file2.pdf> ...")

    pdf_paths = [Path(arg).expanduser().resolve() for arg in argv]
    all_docs = []
    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        all_docs.extend(extract_pdf(pdf_path))

    OUTPUT_PATH.write_text(json.dumps(all_docs, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = Counter(doc["topic"] for doc in all_docs)
    print(f"Wrote {len(all_docs)} chunks to {OUTPUT_PATH}")
    for topic, count in counts.items():
        print(f"- {topic}: {count} chunks")


if __name__ == "__main__":
    main(sys.argv[1:])
