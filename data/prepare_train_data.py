from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent
QUESTION_PATH = DATA_DIR / "discrete_math_questions.json"
KNOWLEDGE_PATH = DATA_DIR / "discrete_math_knowledge_base.json"
PDF_CORPUS_PATH = DATA_DIR / "pdf_corpus.json"
TRAIN_JSON_PATH = DATA_DIR / "train.json"
TEST_JSON_PATH = DATA_DIR / "test.json"
TRAIN_JSONL_PATH = DATA_DIR / "train.jsonl"
TEST_JSONL_PATH = DATA_DIR / "test.jsonl"
RETRIEVAL_CORPUS_PATH = DATA_DIR / "retrieval_corpus.json"
EVAL_SET_PATH = DATA_DIR / "eval_set.json"
SUMMARY_PATH = DATA_DIR / "dataset_summary.json"

SEED = 42
TEST_RATIO = 0.2
SYSTEM_PROMPT = (
    "Bạn là trợ giảng Toán rời rạc. Trả lời tự nhiên bằng tiếng Việt, giải thích trước khi kết luận, "
    "ưu tiên giúp người học hiểu bản chất. Nếu là bài tập thì phân tích đề, nêu hướng làm, giải từng bước rồi mới chốt đáp án."
)

TYPE_LABELS = {
    "multiple_choice": "Trắc nghiệm",
    "short_answer": "Hỏi đáp ngắn",
    "essay": "Tự luận",
}

FORMULA_REPLACEMENTS = [
    ("", " or "),
    ("∨", " or "),
    ("", " and "),
    ("∧", " and "),
    ("", " not "),
    ("¬", " not "),
    ("→", " -> "),
    ("⇒", " -> "),
    ("↔", " <-> "),
    ("⇔", " <-> "),
    ("∪", " union "),
    ("∩", " intersection "),
    ("⊆", " subseteq "),
    ("⊂", " subset "),
    ("⊇", " superseteq "),
    ("⊃", " superset "),
    ("∈", " in "),
    ("∉", " not in "),
    ("∀", " voi moi "),
    ("∃", " ton tai "),
    ("≤", " <= "),
    ("≥", " >= "),
    ("≠", " != "),
]

ACADEMIC_HINTS = [
    "tập hợp",
    "tập con",
    "logic",
    "mệnh đề",
    "suy diễn",
    "quan hệ",
    "hàm",
    "tổ hợp",
    "chỉnh hợp",
    "đồ thị",
    "cây",
    "truy hồi",
    "boole",
    "định nghĩa",
    "định lý",
    "ví dụ",
    "bài tập",
    "chứng minh",
    "poset",
    "hasse",
]

NOISY_HINTS = [
    "nhà xuất bản",
    "mục lục",
    "tài liệu tham khảo",
    "môn học",
    "đại học sư phạm",
    "khoa công nghệ thông tin",
    "gs.nguyễn",
    "nhà xuất bản lao động",
]


def load_questions() -> list[dict]:
    return json.loads(QUESTION_PATH.read_text(encoding="utf-8"))


def load_knowledge_base() -> list[dict]:
    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))


def load_pdf_corpus() -> list[dict]:
    if not PDF_CORPUS_PATH.exists():
        return []
    return json.loads(PDF_CORPUS_PATH.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows),
        encoding="utf-8",
    )


def sanitize_display_text(text: str) -> str:
    cleaned = str(text or "").replace("\r", "\n")
    for source, target in FORMULA_REPLACEMENTS:
        cleaned = cleaned.replace(source, target)
    cleaned = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    return cleaned.strip()


def estimate_quality_score(text: str) -> float:
    if not text:
        return 0.0

    length = max(1, len(text))
    weird_symbol_count = sum(1 for ch in text if ch in {"", "", "", "�"})
    digit_or_letter = sum(1 for ch in text if ch.isalnum())
    printable_ratio = digit_or_letter / length
    weird_ratio = weird_symbol_count / length
    short_penalty = 0.2 if length < 120 else 0.0
    score = printable_ratio - weird_ratio * 8 - short_penalty
    return max(0.0, min(1.0, round(score, 4)))


def looks_academic(text: str, topic: str = "") -> bool:
    lowered = sanitize_display_text(f"{topic}\n{text}").lower()
    if any(hint in lowered for hint in NOISY_HINTS):
        return False

    hint_hits = sum(1 for hint in ACADEMIC_HINTS if hint in lowered)
    if hint_hits >= 2:
        return True

    token_count = len(lowered.split())
    return token_count >= 45 and hint_hits >= 1


def format_options(options: list[str]) -> str:
    labels = ["A", "B", "C", "D", "E", "F"]
    return "\n".join(
        f"{labels[idx] if idx < len(labels) else f'#{idx + 1}'}. {option}"
        for idx, option in enumerate(options)
    )


def build_assistant_response(question: dict) -> str:
    intro = f"Mình sẽ đi từ ý chính của phần {question['topic'].lower()} trước nhé."
    explanation = sanitize_display_text(question.get("explanation", "").strip())

    if question["type"] == "multiple_choice":
        options_text = format_options(question.get("options") or [])
        return "\n\n".join(
            [
                intro,
                f"Đây là câu {TYPE_LABELS[question['type']].lower()}:\n{question['question']}\n{options_text}",
                f"Đáp án đúng là: {sanitize_display_text(question['answer'])}.",
                f"Vì sao: {explanation}" if explanation else "Vì đáp án này khớp với định nghĩa và quy tắc của chủ đề.",
            ]
        )

    return "\n\n".join(
        [
            intro,
            f"Câu hỏi: {sanitize_display_text(question['question'])}",
            f"Trả lời ngắn gọn: {sanitize_display_text(question['answer'])}",
            f"Giải thích: {explanation}" if explanation else "Giải thích: Ta dựa vào định nghĩa cốt lõi của khái niệm này.",
        ]
    )


def build_training_variants(question: dict) -> list[str]:
    base_variants = [question["question"]]
    base_variants.extend(question.get("sample_user_questions") or [])

    variants = []
    seen = set()
    for value in base_variants:
        normalized = " ".join(str(value).strip().split())
        if normalized and normalized not in seen:
            seen.add(normalized)
            variants.append(normalized)
    return variants


def expand_examples(questions: list[dict]) -> list[dict]:
    records = []
    for question in questions:
        assistant_response = build_assistant_response(question)
        for variant in build_training_variants(question):
            records.append(
                {
                    "question_id": question["id"],
                    "question_type": question["type"],
                    "topic": question["topic"],
                    "difficulty": question["difficulty"],
                    "mode": "exercise" if question["type"] == "multiple_choice" else "theory",
                    "prompt": variant,
                    "target": assistant_response,
                    "keywords": question.get("keywords") or [],
                }
            )
    return records


def split_questions(questions: list[dict]) -> tuple[list[dict], list[dict]]:
    shuffled = list(questions)
    random.Random(SEED).shuffle(shuffled)
    test_size = max(1, int(len(shuffled) * TEST_RATIO))
    test_questions = shuffled[:test_size]
    train_questions = shuffled[test_size:]
    return train_questions, test_questions


def build_jsonl_rows(records: list[dict]) -> list[dict]:
    rows = []
    for record in records:
        rows.append(
            {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": record["prompt"]},
                    {"role": "assistant", "content": record["target"]},
                ],
                "metadata": {
                    "question_id": record["question_id"],
                    "topic": record["topic"],
                    "question_type": record["question_type"],
                    "difficulty": record["difficulty"],
                    "mode": record["mode"],
                },
            }
        )
    return rows


def normalize_external_docs(external_docs: list[dict]) -> list[dict]:
    normalized = []
    for doc in external_docs:
        if not isinstance(doc, dict):
            continue

        raw_content = str(doc.get("normalized_content") or doc.get("content") or "").strip()
        normalized_content = sanitize_display_text(raw_content)
        if not normalized_content:
            continue

        topic = str(doc.get("topic") or "Tài liệu PDF").strip()
        title = sanitize_display_text(str(doc.get("title") or topic).strip())
        kind = str(doc.get("kind") or "pdf_chunk").strip()
        source_group = str(doc.get("source_group") or ("pdf" if kind == "pdf_chunk" else "core")).strip()
        keywords = doc.get("keywords") or []
        quality_score = float(doc.get("quality_score") or estimate_quality_score(normalized_content))

        if source_group == "pdf":
            if not looks_academic(normalized_content, topic=topic):
                continue
            if quality_score < 0.35:
                continue

        normalized.append(
            {
                "id": doc.get("id") or f"pdf::{len(normalized)}",
                "topic": topic,
                "kind": kind,
                "title": title,
                "content": normalized_content,
                "normalized_content": normalized_content,
                "keywords": keywords if isinstance(keywords, list) else [],
                "difficulty": doc.get("difficulty") or "mixed",
                "source_group": source_group,
                "quality_score": quality_score,
                "source_question_ids": doc.get("source_question_ids") or [],
                "linked_questions": doc.get("linked_questions") or [],
                "source_file": doc.get("source_file") or None,
                "source_page": doc.get("source_page") or None,
                "retrieval_text": "\n".join(
                    part
                    for part in [
                        topic,
                        topic,
                        kind,
                        title,
                        normalized_content,
                        "\n".join(keywords if isinstance(keywords, list) else []),
                    ]
                    if part
                ),
            }
        )
    return normalized


def build_retrieval_corpus(
    questions: list[dict],
    knowledge_items: list[dict],
    external_docs: list[dict],
) -> list[dict]:
    question_lookup = {question["id"]: question for question in questions}
    corpus = []

    for item in knowledge_items:
        source_question_ids = item.get("source_question_ids") or []
        linked_questions = [question_lookup[qid]["question"] for qid in source_question_ids if qid in question_lookup]
        normalized_content = sanitize_display_text(item["content"])
        corpus.append(
            {
                "id": item["id"],
                "topic": item["topic"],
                "kind": item["kind"],
                "title": sanitize_display_text(item.get("title") or item["id"]),
                "content": normalized_content,
                "normalized_content": normalized_content,
                "keywords": item.get("keywords") or [],
                "difficulty": item.get("difficulty") or "mixed",
                "source_group": "core",
                "quality_score": 1.0,
                "source_question_ids": source_question_ids,
                "linked_questions": linked_questions,
                "retrieval_text": "\n".join(
                    part
                    for part in [
                        item["topic"],
                        item["topic"],
                        item.get("kind") or "",
                        item.get("title") or "",
                        normalized_content,
                        "\n".join(item.get("keywords") or []),
                        "\n".join(linked_questions),
                    ]
                    if part
                ),
            }
        )

    corpus.extend(normalize_external_docs(external_docs))
    return corpus


def build_eval_set(questions: list[dict]) -> dict:
    theory_cases = []
    exercise_cases = []
    follow_up_cases = []
    greeting_cases = []
    small_talk_cases = []

    theory_pool = [question for question in questions if question["type"] != "multiple_choice"][:4]
    exercise_pool = [question for question in questions if question["type"] == "multiple_choice"][:4]

    for question in theory_pool:
        theory_cases.append(
            {
                "id": f"theory::{question['id']}",
                "prompt": (question.get("sample_user_questions") or [question["question"]])[0],
                "expected_topic": question["topic"],
                "expected_mode": "theory",
                "must_include_any": [question["answer"], question.get("explanation", "")],
            }
        )

    for question in exercise_pool:
        exercise_cases.append(
            {
                "id": f"exercise::{question['id']}",
                "prompt": question["question"],
                "expected_topic": question["topic"],
                "expected_mode": "exercise",
                "must_include_any": [question["answer"], question.get("explanation", "")],
            }
        )
        follow_up_cases.append(
            {
                "id": f"follow_up::{question['id']}",
                "conversation": [
                    {"role": "user", "text": question["question"]},
                    {"role": "assistant", "text": build_assistant_response(question)},
                ],
                "prompt": "Giải kỹ hơn từng bước giúp mình được không?",
                "expected_topic": question["topic"],
                "expected_mode": "follow_up",
                "must_include_any": [question["answer"], "bước", "ý tưởng"],
            }
        )

    greeting_cases.append(
        {
            "id": "greeting::hello",
            "prompt": "chào bạn nha",
            "expected_mode": "greeting",
            "must_not_use_sources": True,
        }
    )
    small_talk_cases.append(
        {
            "id": "small_talk::capabilities",
            "prompt": "bạn giúp được gì vậy",
            "expected_mode": "small_talk",
            "must_not_use_sources": True,
        }
    )

    return {
        "greeting": greeting_cases,
        "small_talk": small_talk_cases,
        "theory": theory_cases,
        "exercise": exercise_cases,
        "follow_up": follow_up_cases,
    }


def build_summary(
    all_questions: list[dict],
    train_questions: list[dict],
    test_questions: list[dict],
    train_records: list[dict],
    test_records: list[dict],
    knowledge_items: list[dict],
    retrieval_corpus: list[dict],
    eval_set: dict,
    pdf_corpus: list[dict],
) -> dict:
    topic_counter = Counter(question["topic"] for question in all_questions)
    type_counter = Counter(question["type"] for question in all_questions)
    difficulty_counter = Counter(question["difficulty"] for question in all_questions)
    knowledge_kind_counter = Counter(item["kind"] for item in knowledge_items)
    source_group_counter = Counter(item.get("source_group") or "unknown" for item in retrieval_corpus)

    return {
        "question_count": len(all_questions),
        "knowledge_item_count": len(knowledge_items),
        "retrieval_document_count": len(retrieval_corpus),
        "pdf_document_count": len(pdf_corpus),
        "train_question_count": len(train_questions),
        "test_question_count": len(test_questions),
        "train_record_count": len(train_records),
        "test_record_count": len(test_records),
        "eval_counts": {group: len(rows) for group, rows in eval_set.items()},
        "random_seed": SEED,
        "test_ratio": TEST_RATIO,
        "topics": dict(topic_counter),
        "types": dict(type_counter),
        "difficulties": dict(difficulty_counter),
        "knowledge_kinds": dict(knowledge_kind_counter),
        "source_groups": dict(source_group_counter),
        "files": {
            "train_json": TRAIN_JSON_PATH.name,
            "test_json": TEST_JSON_PATH.name,
            "train_jsonl": TRAIN_JSONL_PATH.name,
            "test_jsonl": TEST_JSONL_PATH.name,
            "retrieval_corpus": RETRIEVAL_CORPUS_PATH.name,
            "eval_set": EVAL_SET_PATH.name,
        },
    }


def main() -> None:
    questions = load_questions()
    knowledge_items = load_knowledge_base()
    pdf_corpus = load_pdf_corpus()
    train_questions, test_questions = split_questions(questions)
    train_records = expand_examples(train_questions)
    test_records = expand_examples(test_questions)
    retrieval_corpus = build_retrieval_corpus(questions, knowledge_items, pdf_corpus)
    eval_set = build_eval_set(questions)

    write_json(TRAIN_JSON_PATH, train_records)
    write_json(TEST_JSON_PATH, test_records)
    write_jsonl(TRAIN_JSONL_PATH, build_jsonl_rows(train_records))
    write_jsonl(TEST_JSONL_PATH, build_jsonl_rows(test_records))
    write_json(RETRIEVAL_CORPUS_PATH, retrieval_corpus)
    write_json(EVAL_SET_PATH, eval_set)
    write_json(
        SUMMARY_PATH,
        build_summary(
            all_questions=questions,
            train_questions=train_questions,
            test_questions=test_questions,
            train_records=train_records,
            test_records=test_records,
            knowledge_items=knowledge_items,
            retrieval_corpus=retrieval_corpus,
            eval_set=eval_set,
            pdf_corpus=pdf_corpus,
        ),
    )

    print(
        "Prepared structured data: "
        f"{len(train_records)} train records, {len(test_records)} test records, "
        f"{len(retrieval_corpus)} retrieval docs."
    )


if __name__ == "__main__":
    main()
