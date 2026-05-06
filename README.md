# Trợ Lý Toán Rời Rạc

Chatbot hỗ trợ học Toán Rời Rạc, cho phép chuyển đổi giữa hai chế độ trả lời:

- **Traditional (TF-IDF + Sentence Embeddings + BiGRU)**: Không cần API key, chạy hoàn toàn cục bộ.
- **RAG (AI)**: Dùng OpenAI hoặc Groq để sinh câu trả lời từ ngữ liệu truy xuất được.

## Kiến trúc hệ thống

```text
Frontend (index.html)
    │
    │  HTTP POST /api/chat  { message, mode, conversationId }
    ▼
Backend (Node.js - server.js)
    │
    │  spawn child process
    ├──► brain_traditional.py   (mode = "traditional")
    └──► brain_rag.py           (mode = "rag")
    │
    │  JSON stdout
    ▼
SQLite (chatbot.sqlite) — lưu lịch sử hội thoại
```

### Bộ não Traditional — 3-layer Hybrid Retrieval

| Layer | Kỹ thuật | Trọng số | Mô tả |
| :---: | :--- | :---: | :--- |
| **1** | TF-IDF char n-gram (2–4) | 25% | Khớp từ/ký tự, tốt cho tiếng Việt |
| **2** | Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) | 55% | Embedding ngữ nghĩa đa ngôn ngữ |
| **3** | Character-level BiGRU (2-layer, PyTorch) | 20% | Mã hóa tuần tự ký tự |

**Điểm cuối** = Tổng có trọng số $\rightarrow$ lấy câu hỏi có điểm cao nhất $\rightarrow$ trả về câu trả lời tương ứng. Embeddings được cache vào `trad_st_cache.npy` và `trad_gru_cache.npy` để tăng tốc các lần sau.

### Bộ não RAG

Dùng API tương thích OpenAI (OpenAI hoặc Groq) để sinh câu trả lời từ ngữ liệu truy xuất từ `retrieval_corpus.json`.

---

## Yêu cầu

- **Node.js 20+**
- **Python 3.10+**

Kiểm tra nhanh:
```bash
node -v
python --version
```

---

## Cài đặt

### 1. Cài thư viện Python
```bash
pip install -r data/requirements.txt
```
> [!NOTE]
> Thư viện Python bao gồm: `scikit-learn`, `sentence-transformers` (kéo theo `torch`), `openai`, `numpy`.

### 2. Cài thư viện Node.js
```bash
cd backend
npm install
```

---

## Cấu hình

File `.env` không được push lên Git. Sau khi clone, tạo file `.env` từ mẫu:

* **Windows:**
  ```cmd
  copy backend\.env.example backend\.env
  ```
* **Linux / Mac:**
  ```bash
  cp backend/.env.example backend/.env
  ```

Mở `backend/.env` và cấu hình theo nhu cầu của bạn:

* **Chỉ dùng mode Traditional:** Không cần làm gì thêm.
* **Dùng mode RAG với Groq (miễn phí):**
  * Lấy API key tại [console.groq.com](https://console.groq.com)
  * Điền `OPENAI_API_KEY=gsk_...`
  * Điền `OPENAI_BASE_URL=https://api.groq.com/openai/v1`
  * Đổi `OPENAI_CHAT_MODEL=llama-3.3-70b-versatile`
* **Dùng mode RAG với OpenAI:**
  * Lấy API key tại [platform.openai.com](https://platform.openai.com)
  * Điền `OPENAI_API_KEY=sk-...`
  * Giữ `OPENAI_BASE_URL=` trống
  * Giữ `OPENAI_CHAT_MODEL=gpt-4o-mini`

---

## Chạy ứng dụng

```bash
cd backend
npm start
```
Mở `frontend/index.html` bằng Live Server (VS Code) hoặc trực tiếp trên trình duyệt.

> [!IMPORTANT]
> **Lưu ý lần đầu:** Khi gửi tin nhắn đầu tiên ở chế độ **Traditional**, script `brain_traditional.py` sẽ tải model `paraphrase-multilingual-MiniLM-L12-v2` (~120 MB) và tính embedding cho toàn bộ corpus. Quá trình khởi tạo này mất khoảng **30–60 giây**. Từ các lần gửi tin tiếp theo sẽ cực kỳ nhanh do dữ liệu đã được cache.

---

## Cấu trúc thư mục

```text
├── backend/
│   ├── server.js                  # HTTP server, định tuyến API
│   ├── chat-service.js            # Gọi Python brain, lưu hội thoại
│   ├── conversation-repository.js # CRUD SQLite
│   ├── config.js                  # Biến cấu hình runtime
│   ├── utils.js                   # Hàm tiện ích (cosine, normalize…)
│   └── .env                       # Biến môi trường (không push Git)
│
├── data/
│   ├── brain_traditional.py       # Bộ não Traditional (TF-IDF + Embedding + BiGRU)
│   ├── brain_rag.py               # Bộ não RAG (OpenAI/Groq)
│   ├── traditional_corpus.json    # Dữ liệu Q&A cho Traditional
│   ├── retrieval_corpus.json      # Ngữ liệu cho RAG
│   ├── prepare_data_traditional.py  # Tạo traditional_corpus.json từ CSV
│   ├── prepare_data_rag.py        # Tạo retrieval_corpus.json
│   ├── output.csv                 # Dữ liệu gốc
│   └── requirements.txt           # Thư viện Python cần cài
│
└── frontend/
    ├── index.html                 # Giao diện chat
    ├── script.js                  # Gọi API, render UI
    └── style.css                  # Giao diện
```

---

## API Backend

| Method | Endpoint | Mô tả |
| :---: | :--- | :--- |
| **GET** | `/api/health` | Kiểm tra trạng thái server |
| **GET** | `/api/conversations` | Lấy danh sách cuộc hội thoại |
| **GET** | `/api/conversations/:id/messages` | Lấy chi tiết tin nhắn của cuộc hội thoại |
| **POST** | `/api/chat` | Gửi tin nhắn mới |
| **PATCH** | `/api/conversations/:id` | Cập nhật hội thoại (đổi tên, ghim...) |
| **DELETE** | `/api/conversations/:id` | Xóa cuộc hội thoại |

**Cấu trúc Body của POST `/api/chat`:**
```json
{
  "message": "Tập rỗng là gì?",
  "mode": "traditional",
  "conversationId": "optional-uuid"
}
```

---

## Gợi ý phát triển tiếp

1. **Fine-tune BiGRU** bằng contrastive loss trên bộ (câu hỏi, câu trả lời) để tăng chất lượng Layer 3.
2. **Thêm PDF giáo trình** vào RAG corpus bằng cách parse PDF rồi đưa thêm vào `retrieval_corpus.json`.
3. **Thêm re-ranking** sau bước retrieval để cải thiện độ chính xác và chất lượng phản hồi của RAG.
