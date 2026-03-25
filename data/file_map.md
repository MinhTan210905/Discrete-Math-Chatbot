# Bản đồ file trong data/

## File gốc để mình chỉnh tay
- `build_question_bank.py`: tạo ngân hàng câu hỏi gốc và knowledge base.
- `topic_blueprints.py`: các ghi chú theo chủ đề như định nghĩa, quy tắc, ví dụ, lỗi hay nhầm.
- `prepare_train_data.py`: gom dữ liệu, làm sạch PDF, sinh `train/test`, `retrieval_corpus`, `eval_set`.
- `train_model.py`: build chỉ mục retrieval từ `retrieval_corpus.json`.
- `ingest_pdfs.py`: đọc PDF, cắt chunk, lọc chunk nhiễu và xuất ra `pdf_corpus.json`.

## File dữ liệu nguồn
- `discrete_math_questions.json`: ngân hàng câu hỏi seed.
- `discrete_math_knowledge_base.json`: kho tri thức lõi cho RAG.
- `pdf_corpus.json`: các đoạn text đã trích ra từ PDF.

## File sinh ra để runtime dùng
- `retrieval_corpus.json`: corpus đã chuẩn hóa để retriever đọc.
- `discrete_math_model.json`: index hybrid đã build, backend đọc file này khi tìm tài liệu.
- `dataset_summary.json`: bảng thống kê dataset.
- `eval_set.json`: bộ ca kiểm tra offline cho greeting, small talk, theory, exercise, follow_up.

## File train/test để tham khảo hoặc fine-tune sau này
- `train.json`, `test.json`: bản dễ đọc.
- `train.jsonl`, `test.jsonl`: định dạng chat JSONL.

## Khi muốn thêm PDF mới
1. Chạy `python data/ingest_pdfs.py "duong_dan_file.pdf"`
2. Chạy `python data/prepare_train_data.py`
3. Chạy `python data/train_model.py`

## Khi bot trả lời dùng file nào
- Lúc chat: backend đọc `discrete_math_model.json`
- Model index đó được build từ `retrieval_corpus.json`
- `retrieval_corpus.json` được sinh từ knowledge base lõi + `pdf_corpus.json`
