# Trợ Lý Toán Rời Rạc

Chatbot hỗ trợ học Toán Rời Rạc với **giao diện Toán học tuyệt đẹp (KaTeX + Markdown)** và hai chế độ AI:

- **Traditional**: TF-IDF + Sentence Embeddings — không cần API key, chạy hoàn toàn cục bộ.
- **RAG (AI)**: Query Expansion + Vector Search + LLM — cần API key (OpenAI hoặc Groq miễn phí). Hỗ trợ đọc file PDF giáo trình.

---

## Kiến trúc hệ thống

```
Frontend (index.html)
    │  HTTP POST /api/chat  { message, mode, conversationId }
    ▼
Backend (Node.js — server.js)
    │  spawn child process
    ├──► brain_traditional.py   (mode = "traditional")
    └──► brain_rag.py           (mode = "rag")
    │  JSON stdout
    ▼
SQLite (data/chatbot.sqlite) — lưu lịch sử hội thoại
```

### Bộ não Traditional

| Layer | Kỹ thuật | Trọng số |
|---|---|---|
| 1 | TF-IDF char n-gram (2–4) | 35% |
| 2 | Sentence Transformers `paraphrase-multilingual-MiniLM-L12-v2` | 65% |

### Bộ não RAG — 3 Phase

```
Phase 1 (Pre-retrieval)  : Query Expansion — LLM sinh 3 sub-queries
Phase 2 (Retrieval)      : Vector Search — sentence-transformers lấy top-15, dedup
Phase 3 (Post-retrieval) : Cross-Encoder Re-ranking → top-4 → LLM sinh câu trả lời
```

Nguồn dữ liệu RAG = `retrieval_corpus.json` (Q&A pairs) **+** `pdf_corpus.json` (PDF chunks, nếu có).

---

## Yêu cầu
- **Node.js** 20+
- **Python** 3.10+

---

## Cài đặt

### 1. Cài thư viện Python
```bash
pip install -r data/requirements.txt
```
> [!NOTE]
> Thư viện Python bao gồm: `scikit-learn`, `sentence-transformers`, `openai`, `pymupdf`.

### 2. Cài thư viện Node.js
```bash
cd backend
npm install
```

### 3. Tạo dữ liệu ban đầu (Corpus)
```bash
# Tạo dữ liệu cho mode Traditional
python data/prepare_data_traditional.py

# Tạo dữ liệu cho mode RAG
python data/prepare_data_rag.py
```

---

## Cấu hình

Tạo file `.env`:
```bash
# Windows
copy backend\.env.example backend\.env
```

Mở `backend/.env` và cấu hình các thông số API Key của Groq/OpenAI.

---

## Chạy

```bash
cd backend
npm start
```
Mở `frontend/index.html` trực tiếp trên trình duyệt.

---

## Thêm tài liệu PDF vào RAG

```bash
# 1. Đặt PDF vào thư mục
data/pdfs/ten_file.pdf

# 2. Chạy script chunking (semantic chunking)
python data/prepare_pdf_corpus.py

# 3. Restart backend để load dữ liệu mới
```
