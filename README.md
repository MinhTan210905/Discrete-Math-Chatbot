# Trợ Lý Toán Rời Rạc

Ứng dụng này đã được nâng từ bot TF-IDF trả lời theo mẫu sang kiến trúc kiểu `RAG + conversation memory + tutor-style response`.

Bot mới có 4 lớp chính:

1. `Knowledge pipeline`: sinh ngân hàng câu hỏi, knowledge base có cấu trúc, retrieval corpus, eval set.
2. `Hybrid retrieval`: kết hợp lexical TF-IDF, semantic vector cục bộ, và OpenAI embedding cache nếu có `OPENAI_API_KEY`.
3. `Chat orchestration`: phân loại câu hỏi thành `greeting`, `small_talk`, `theory`, `exercise`, `follow_up`, truy xuất tri thức khi thật sự cần, rồi sinh câu trả lời tự nhiên kiểu gia sư.
4. `Conversation memory`: lưu toàn bộ lịch sử chat trong SQLite ở server-side, không còn để frontend ghi đè cả mảng lịch sử như trước.

## Yêu cầu

- Node.js 20+
- Python 3.10+

Kiểm tra nhanh:

```bash
node -v
python --version
```

## Quickstart

Repo này không cần commit các file dữ liệu sinh ra (corpus/model/train/test). Sau khi clone, chạy:

```bash
cd backend
npm install
npm run rebuild:data
npm start
```

Rồi mở `frontend/index.html` (Live Server) để chat.

## Cấu trúc thư mục

### `data/`

- `build_question_bank.py`: tạo `discrete_math_questions.json` và `discrete_math_knowledge_base.json`.
- `topic_blueprints.py`: tri thức nền theo từng chủ đề như `concept_note`, `formula_rule`, `worked_example`, `common_mistake`, `exercise_variants`.
- `prepare_train_data.py`: sinh `train.json`, `test.json`, `train.jsonl`, `test.jsonl`, `retrieval_corpus.json`, `eval_set.json`, `dataset_summary.json`.
- `train_model.py`: build retrieval index vào `discrete_math_model.json`.
- `discrete_math_questions.json`: 100 câu seed về Toán rời rạc.
- `discrete_math_knowledge_base.json`: kho tri thức có cấu trúc dùng cho RAG.
- `retrieval_corpus.json`: corpus đã chuẩn hóa để retriever index.
- `train.json`: dữ liệu train ở dạng record nội bộ dễ đọc.
- `train.jsonl`: dữ liệu hội thoại kiểu fine-tune/chat format để dùng tiếp về sau.
- `test.json`: tập holdout để kiểm tra record-level.
- `test.jsonl`: phiên bản JSONL của tập test.
- `eval_set.json`: bộ case offline cho `theory`, `exercise`, `follow_up`.
- `dataset_summary.json`: thống kê số lượng câu hỏi, knowledge docs, retrieval docs, eval cases.
- `discrete_math_model.json`: retrieval index đã build, gồm lexical vector, semantic vector và embedding cache nếu có.
- `file_map.md`: bản đồ ngắn giải thích file nào là file gốc, file nào được sinh ra, file nào runtime đang dùng.
- `history-temp.json`: file lịch sử cũ; backend mới sẽ migrate sang SQLite ở lần chạy đầu nếu DB còn trống.

### `backend/`

- `server.js`: HTTP API chính.
- `chat-service.js`: orchestration cho một lượt chat.
- `conversation-repository.js`: SQLite repository cho conversations/messages.
- `retrieval-engine.js`: phân loại mode và truy xuất tài liệu liên quan.
- `openai-service.js`: gọi OpenAI Responses API và Embeddings API, có fallback local khi chưa cấu hình key.
- `config.js`: cấu hình runtime.
- `utils.js`: normalize text, cosine similarity, semantic vector helper.
- `qa-engine.js`: compatibility wrapper cho model status.
- `.env.example`: mẫu biến môi trường.
- `tests/`: unit + integration tests.

### `frontend/`

- `index.html`: layout giao diện chat.
- `script.js`: chỉ render UI và gọi API; server mới là source of truth của conversation.
- `style.css`: giao diện chat và sidebar.

## Dòng chảy dữ liệu

```bash
python data/build_question_bank.py
python data/prepare_train_data.py
python data/train_model.py
```

## Nhúng PDF vào RAG

Nếu bạn có PDF giáo trình/bài giảng, hãy chạy:

```bash
python data/ingest_pdfs.py "D:\Duong Dan\file1.pdf" "D:\Duong Dan\file2.pdf"
python data/prepare_train_data.py
python data/train_model.py
```

Các đoạn PDF sẽ được lưu vào `data/pdf_corpus.json`, sau đó được làm sạch, lọc bớt chunk nhiễu, đưa vào `retrieval_corpus.json` và index mới.

Hoặc từ thư mục `backend/`:

```bash
npm run rebuild:data
```

## Cấu hình OpenAI

Copy `backend/.env.example` thành file `.env` riêng của bạn hoặc set biến môi trường trực tiếp trong terminal.

Các biến quan trọng:

- `OPENAI_API_KEY`: bắt buộc nếu muốn bot trả lời bằng model OpenAI.
- `OPENAI_CHAT_MODEL`: mặc định `gpt-5.4`.
- `OPENAI_EMBEDDING_MODEL`: mặc định `text-embedding-3-small`.
- `OPENAI_REASONING_EFFORT`: mặc định `medium`.
- `CHAT_DB_PATH`: đường dẫn SQLite file, mặc định `data/chatbot.sqlite`.

Nếu chưa có `OPENAI_API_KEY`, app vẫn chạy được với fallback generator cục bộ dựa trên tri thức đã truy xuất, nhưng câu trả lời sẽ kém tự nhiên hơn.

## Chạy backend

Từ thư mục `backend/`:

```bash
npm install
npm start
```

API chính:

- `GET /api/health`
- `GET /api/model-status`
- `GET /api/conversations`
- `GET /api/conversations/:id/messages`
- `POST /api/chat`
- `PATCH /api/conversations/:id`
- `DELETE /api/conversations/:id`

## Chạy frontend

Mở `frontend/index.html` bằng Live Server hoặc trình duyệt rồi đảm bảo backend đang chạy ở `http://localhost:3001`.

## Chạy test

Từ thư mục `backend/`:

```bash
npm test
```

Bộ test hiện có:

- repository SQLite
- classifier + retrieval
- integration test cho chat nhiều lượt và lưu lịch sử

## Bot hiện trả lời như thế nào?

- Nếu là chào hỏi hoặc xã giao: trả lời như chatbot bình thường, không lôi PDF hay nguồn ra.
- Nếu là câu lý thuyết: trả lời tự nhiên, giải thích ý nghĩa trước rồi mới chốt định nghĩa/quy tắc.
- Nếu là bài tập: đi theo `hiểu đề -> ý tưởng làm -> từng bước giải -> kết luận`.
- Nếu là câu nối tiếp: dùng lịch sử conversation gần nhất để trả lời tiếp mạch trước đó.
- PDF chỉ được ưu tiên khi câu hỏi thật sự mang tính học thuật hoặc nhắc rõ giáo trình/tài liệu.

## Gợi ý phát triển tiếp

- Bổ sung thêm `worked examples` khó hơn trong `topic_blueprints.py`.
- Sinh embedding cache bằng cách set `OPENAI_API_KEY` rồi chạy lại `python data/train_model.py`.
- Thêm server-side eval script đọc `eval_set.json` để chấm regression tự động.
