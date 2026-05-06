import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "output.csv"
CORPUS_PATH = DATA_DIR / "traditional_corpus.json"

def process_csv():
    corpus = []
    
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        # Assuming the first line might be header or data.
        # Let's read all lines. If it's a header like ID;Type;Topic;Question;Answer we can skip it.
        reader = csv.reader(f, delimiter=';')
        
        for row in reader:
            if len(row) < 5:
                continue
            
            # Simple header check
            if row[0].lower() == 'id' or row[0].lower() == 'qa_id':
                continue
                
            qa_id = row[0].strip()
            qa_type = row[1].strip()
            topic = row[2].strip()
            question = row[3].strip()
            answer = row[4].strip()
            
            if not question or not answer:
                continue
                
            corpus.append({
                "id": qa_id,
                "type": qa_type,
                "topic": topic,
                "question": question,
                "answer": answer
            })

    with open(CORPUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed {len(corpus)} records into traditional_corpus.json")

if __name__ == "__main__":
    process_csv()
