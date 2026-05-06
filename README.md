# Trợ Lý Toán Rời Rạc

Chatbot hỗ trợ học Toán Rời Rạc với hai chế độ:

- **Traditional**: TF-IDF + Sentence Embeddings — không cần API key, chạy hoàn toàn cục bộ.
- **RAG (AI)**: Query Expansion + Vector Search + Cross-Encoder Re-ranking + LLM — cần API key (OpenAI hoặc Groq miễn phí).

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

Bao gồm: `scikit-learn`, `sentence-transformers` (kéo theo `torch`), `openai`, `pymupdf`.

### 2. Cài thư viện Node.js

```bash
cd backend
npm install
```

### 3. Tạo dữ liệu ban đầu (Corpus)

Các file dữ liệu `.json` không được đưa lên Git để giảm dung lượng. Bạn cần chạy các script sau để tự động tạo chúng từ file `output.csv` gốc:

```bash
# Tạo dữ liệu cho mode Traditional
python data/prepare_data_traditional.py

# Tạo dữ liệu cho mode RAG
python data/prepare_data_rag.py
```
*(Nếu bạn có thêm file PDF, xem hướng dẫn phần "Thêm tài liệu PDF vào RAG" bên dưới)*

---

## Cấu hình

File `.env` **không push lên Git**. Tạo từ file mẫu:

```bash
# Windows
copy backend\.env.example backend\.env

# Linux / Mac
cp backend/.env.example backend/.env
```

Mở `backend/.env` và điền:

| Muốn dùng | Cần làm |
|---|---|
| **Traditional** (không cần key) | Không cần làm gì |
| **RAG với Groq (miễn phí)** | Lấy key tại [console.groq.com](https://console.groq.com), điền `OPENAI_API_KEY`, `OPENAI_BASE_URL=https://api.groq.com/openai/v1`, `OPENAI_CHAT_MODEL=llama-3.3-70b-versatile` |
| **RAG với OpenAI** | Lấy key tại [platform.openai.com](https://platform.openai.com/api-keys), điền `OPENAI_API_KEY`, để `OPENAI_BASE_URL` trống |

---

## Chạy

```bash
cd backend
npm start
```

Mở `frontend/index.html` bằng **Live Server** (VS Code).

> **Lần đầu chạy sẽ chậm hơn** vì cần tải model `paraphrase-multilingual-MiniLM-L12-v2` (~120 MB) và tính embedding cho toàn corpus. Các lần sau dùng cache.

---

## Thêm tài liệu PDF vào RAG

```bash
# 1. Đặt PDF vào thư mục
data/pdfs/ten_file.pdf

# 2. Chạy script chunking (semantic chunking)
python data/prepare_pdf_corpus.py

# 3. Restart backend để load dữ liệu mới
```

Script tự động: trích text từng trang → tách câu → tính cosine similarity giữa các câu → cắt chunk tại điểm chủ đề đổi → lưu ra `data/pdf_corpus.json`.

---

## Cấu trúc thư mục

```
├── backend/
│   ├── server.js                    # HTTP server, định tuyến API
│   ├── chat-service.js              # Gọi Python brain, lưu hội thoại
│   ├── conversation-repository.js   # CRUD SQLite
│   ├── config.js                    # Biến cấu hình runtime
│   ├── utils.js                     # Hàm tiện ích
│   ├── .env.example                 # Mẫu cấu hình (copy → .env)
│   └── .env                         # ⚠ Không push Git
│
├── data/
│   ├── brain_traditional.py         # Bộ não Traditional (TF-IDF + Embeddings)
│   ├── brain_rag.py                 # Bộ não RAG (3-phase pipeline)
│   ├── prepare_pdf_corpus.py        # Semantic chunking PDF → pdf_corpus.json
│   ├── prepare_data_traditional.py  # Tạo traditional_corpus.json từ CSV
│   ├── prepare_data_rag.py          # Tạo retrieval_corpus.json
│   ├── traditional_corpus.json      # Dữ liệu Q&A cho Traditional
│   ├── retrieval_corpus.json        # Corpus cho RAG
│   ├── output.csv                   # Dữ liệu gốc
│   ├── requirements.txt             # Thư viện Python
│   │
│   ├── pdfs/                        # ⚠ Đặt PDF vào đây (không push Git)
│   ├── pdf_corpus.json              # ⚠ Auto-generated (không push Git)
│   ├── trad_st_cache.npy            # ⚠ Auto-generated (không push Git)
│   └── rag_embed_cache.npy          # ⚠ Auto-generated (không push Git)
│
└── frontend/
    ├── index.html                   # Giao diện chat
    ├── script.js                    # Gọi API, render UI
    └── style.css                    # Giao diện
```

---

## API Backend

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/health` | Kiểm tra server |
| GET | `/api/conversations` | Danh sách hội thoại |
| GET | `/api/conversations/:id/messages` | Tin nhắn của hội thoại |
| POST | `/api/chat` | Gửi tin nhắn |
| PATCH | `/api/conversations/:id` | Cập nhật hội thoại |
| DELETE | `/api/conversations/:id` | Xóa hội thoại |

**Body POST `/api/chat`:**
```json
{
  "message": "Tập rỗng là gì?",
  "mode": "traditional",
  "conversationId": "optional-uuid"
}
```
