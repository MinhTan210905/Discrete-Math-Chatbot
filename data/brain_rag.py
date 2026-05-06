import sys
import json
import os
import numpy as np
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print(json.dumps({
        "reply": "Lỗi: Chưa cài đặt thư viện openai. Hãy chạy lệnh 'pip install openai' để sử dụng RAG.",
        "mode": "rag",
        "confidence": 0,
        "sources": [],
        "provider": "error"
    }))
    sys.exit(1)

DATA_DIR = Path(__file__).resolve().parent
CORPUS_PATH = DATA_DIR / "retrieval_corpus.json"

def get_embedding(client, text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "reply": "Lỗi: Không nhận được câu hỏi.",
            "mode": "rag",
            "confidence": 0,
            "sources": []
        }))
        sys.exit(1)

    query = sys.argv[1].strip()
    history_json = sys.argv[2] if len(sys.argv) > 2 else "[]"
    
    try:
        history = json.loads(history_json)
    except:
        history = []

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(json.dumps({
            "reply": "Lỗi: Chưa cấu hình OPENAI_API_KEY trong môi trường.",
            "mode": "rag",
            "confidence": 0,
            "sources": [],
            "provider": "error"
        }))
        sys.exit(1)

    base_url = os.environ.get("OPENAI_BASE_URL")  # None = dùng OpenAI mặc định
    client = OpenAI(api_key=api_key, base_url=base_url)

    if not CORPUS_PATH.exists():
        print(json.dumps({
            "reply": "Lỗi: Không tìm thấy dữ liệu RAG (retrieval_corpus.json).",
            "mode": "rag",
            "confidence": 0,
            "sources": []
        }))
        sys.exit(1)

    with open(CORPUS_PATH, 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    # Simplified embedding process (ideally embeddings should be pre-computed and stored)
    # But since we deleted train_model.py, we will just simulate a quick keyword search or 
    # compute embeddings on the fly for small datasets. For performance in real life, 
    # we should pre-embed. Given the user's constraints, we will do a fast text search 
    # to find relevant context if pre-computed vectors don't exist, but since it's RAG, 
    # let's just do a simple term overlap for retrieval to save API costs on every run, 
    # or just send the most relevant items.
    
    # Simple lexical retrieval to find top 3 chunks (since we deleted the complex RAG index)
    query_terms = set(query.lower().split())
    
    scored_corpus = []
    for item in corpus:
        text = item.get("content", "").lower()
        score = sum(1 for term in query_terms if term in text)
        scored_corpus.append((score, item))
        
    scored_corpus.sort(key=lambda x: x[0], reverse=True)
    top_docs = [item for score, item in scored_corpus[:3] if score > 0]
    
    context_text = "\n\n---\n\n".join([doc["content"] for doc in top_docs])
    
    sources = [{"title": doc.get("title", ""), "topic": doc.get("topic", "")} for doc in top_docs]

    messages = [
        {"role": "system", "content": "Bạn là trợ giảng Toán Rời Rạc. Dựa vào tài liệu dưới đây, hãy trả lời câu hỏi của sinh viên. Nếu tài liệu không chứa câu trả lời, hãy nói không biết.\n\nTÀI LIỆU:\n" + context_text}
    ]
    
    for msg in history[-4:]: # Giữ 4 tin nhắn gần nhất
        messages.append({"role": msg["role"], "content": msg["text"]})
        
    messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.3
        )
        reply = response.choices[0].message.content
        print(json.dumps({
            "reply": reply,
            "mode": "rag",
            "confidence": 0.9 if top_docs else 0.5,
            "sources": sources,
            "provider": "python-openai-rag"
        }))
        
    except Exception as e:
        print(json.dumps({
            "reply": f"Lỗi gọi OpenAI: {str(e)}",
            "mode": "rag",
            "confidence": 0,
            "sources": [],
            "provider": "error"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
