import csv
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "output.csv"
RETRIEVAL_CORPUS_PATH = DATA_DIR / "retrieval_corpus.json"

FORMULA_REPLACEMENTS = [
    ("", " or "), ("∨", " or "), ("", " and "), ("∧", " and "),
    ("", " not "), ("¬", " not "), ("→", " -> "), ("⇒", " -> "),
    ("↔", " <-> "), ("⇔", " <-> "), ("∪", " union "), ("∩", " intersection "),
    ("⊆", " subseteq "), ("⊂", " subset "), ("⊇", " superseteq "),
    ("⊃", " superset "), ("∈", " in "), ("∉", " not in "),
    ("∀", " voi moi "), ("∃", " ton tai "), ("≤", " <= "),
    ("≥", " >= "), ("≠", " != "),
]

def sanitize_display_text(text: str) -> str:
    cleaned = str(text or "").replace("\r", "\n")
    for source, target in FORMULA_REPLACEMENTS:
        cleaned = cleaned.replace(source, target)
    cleaned = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    return cleaned.strip()

def process_csv():
    corpus = []
    
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        
        for row in reader:
            if len(row) < 5:
                continue
            
            if row[0].lower() == 'id' or row[0].lower() == 'qa_id':
                continue
                
            qa_id = row[0].strip()
            qa_type = row[1].strip()
            topic = row[2].strip()
            question = row[3].strip()
            answer = row[4].strip()
            
            if not question or not answer:
                continue
                
            normalized_content = sanitize_display_text(question + "\n" + answer)
            
            retrieval_text = "\n".join(part for part in [
                topic,
                topic,
                "qa_pair",
                question,
                normalized_content
            ] if part)

            corpus.append({
                "id": qa_id,
                "topic": topic,
                "kind": "qa_pair",
                "title": question,
                "content": question + "\n" + answer,
                "normalized_content": normalized_content,
                "keywords": [],
                "difficulty": "mixed",
                "source_group": "core",
                "quality_score": 1.0,
                "source_question_ids": [qa_id],
                "linked_questions": [question],
                "retrieval_text": retrieval_text
            })

    with open(RETRIEVAL_CORPUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully built retrieval corpus from {len(corpus)} records.")

if __name__ == "__main__":
    process_csv()
