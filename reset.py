import os
import shutil
from pathlib import Path

# Thư mục gốc của project
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"

# Danh sách các file cần xóa (các file được sinh ra tự động, cache, database)
FILES_TO_REMOVE = [
    DATA_DIR / "chatbot.sqlite",
    DATA_DIR / "chatbot.sqlite-shm",
    DATA_DIR / "chatbot.sqlite-wal",
    DATA_DIR / "history-temp.json",
    DATA_DIR / "traditional_corpus.json",
    DATA_DIR / "retrieval_corpus.json",
    DATA_DIR / "pdf_corpus.json",
    DATA_DIR / "trad_st_cache.npy",
    DATA_DIR / "rag_embed_cache.npy",
]

# Danh sách các thư mục cần xóa (cache)
DIRS_TO_REMOVE = [
    DATA_DIR / "__pycache__",
]

def reset_project():
    print("=== BẮT ĐẦU RESET PROJECT ===")
    
    # Xóa files
    for file_path in FILES_TO_REMOVE:
        if file_path.exists():
            try:
                os.remove(file_path)
                print(f"[XÓA] Đã xóa file: {file_path.name}")
            except Exception as e:
                print(f"[LỖI] Không thể xóa file {file_path.name}: {e}")
                
    # Xóa thư mục
    for dir_path in DIRS_TO_REMOVE:
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                print(f"[XÓA] Đã xóa thư mục: {dir_path.name}")
            except Exception as e:
                print(f"[LỖI] Không thể xóa thư mục {dir_path.name}: {e}")

    # Tìm và xóa tất cả các thư mục __pycache__ và file .pyc
    for root, dirs, files in os.walk(ROOT_DIR):
        if "node_modules" in root or ".git" in root or ".vs" in root:
            continue
            
        for d in dirs:
            if d == "__pycache__":
                pycache_path = os.path.join(root, d)
                try:
                    shutil.rmtree(pycache_path)
                    print(f"[XÓA] Đã xóa thư mục cache: {pycache_path}")
                except Exception as e:
                    pass
                    
        for f in files:
            if f.endswith(".pyc"):
                pyc_path = os.path.join(root, f)
                try:
                    os.remove(pyc_path)
                except:
                    pass

    print("=== RESET HOÀN TẤT ===")
    print("\nĐể chạy lại hệ thống từ đầu, bạn cần chạy các script tạo data:")
    print("  python data/prepare_data_traditional.py")
    print("  python data/prepare_data_rag.py")
    print("  python data/prepare_pdf_corpus.py  (nếu có file PDF trong data/pdfs/)")
    print("\nSau đó khởi động lại server:")
    print("  cd backend && npm run dev")

if __name__ == "__main__":
    reset_project()
