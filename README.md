# Discrete Math Chatbot

Giao diện chatbot Toán Rời Rạc (frontend thuần HTML/CSS/JS) + backend mini Node.js để lưu lịch sử chat vào file JSON.

## 1) Yêu cầu môi trường

- Node.js 18+ (khuyên dùng bản LTS)
- npm (đi kèm Node.js)
- Trình duyệt Chrome/Edge/Firefox

Kiểm tra nhanh:

```bash
node -v
npm -v
```

## 2) Cấu trúc chính

- `frontend/`: giao diện chat
- `backend/server.js`: API lưu lịch sử
- `data/history-temp.json`: file lưu lịch sử tạm

## 3) Chạy backend (bắt buộc)

Từ thư mục gốc project, mở terminal và chạy:

```bash
cd backend
npm start
```

Sau khi chạy thành công:

- API: `http://localhost:3001/api/history`
- Health check: `http://localhost:3001/api/health`
- File lưu dữ liệu: `data/history-temp.json`

## 4) Mở frontend

Có 2 cách:

### Cách A (khuyên dùng): Live Server trong VS Code

1. Mở file `frontend/index.html`
2. Bấm `Go Live` (extension Live Server)
3. Truy cập URL local do Live Server cấp

### Cách B: Mở trực tiếp file HTML

Mở `frontend/index.html` bằng trình duyệt.

## 5) Cách kiểm tra lưu lịch sử

1. Gửi vài tin nhắn trong giao diện
2. Mở file `data/history-temp.json`
3. Xác nhận đã có mảng hội thoại mới (title, pinned, archived, messages...)

## 6) Tính năng lịch sử hiện có

- Mở lại chat cũ bằng cách bấm vào mục lịch sử
- Menu `⋯` cho từng chat: Chia sẻ, Bắt đầu chat nhóm, Đổi tên, Ghim, Lưu trữ, Xóa
- Tab lọc: `Gần đây` / `Lưu trữ`

## 7) Lỗi hay gặp

### Không lưu được lịch sử

- Kiểm tra backend đã chạy chưa (`npm start` trong `backend`)
- Kiểm tra cổng `3001` có bị app khác chiếm không

### Giao diện mở được nhưng không có dữ liệu cũ

- Kiểm tra file `data/history-temp.json` có bị xóa hoặc format sai JSON không

## 8) Gợi ý cho team

- `history-temp.json` là dữ liệu tạm, có thể reset bất cứ lúc nào
- Không commit dữ liệu riêng tư vào Git khi dùng chung repo