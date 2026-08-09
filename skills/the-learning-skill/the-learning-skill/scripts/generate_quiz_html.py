#!/usr/bin/env python3
"""Generate a self-contained HTML quiz app from a JSON question list.

Reads the template from ../assets/quiz_template.html and injects the question
data, quiz title, and a quiz ID for localStorage.

Usage:
    python generate_quiz_html.py --questions q.json --output quiz.html --title "Topic Quiz"
    python generate_quiz_html.py --questions-stdin --output quiz.html --title "Topic Quiz"

JSON question format (a list of question objects):

    [
      {
        "type": "mcq",
        "question": "What does TCP stand for?",
        "options": ["Transmission Control Protocol", "Terminal Control Protocol", ...],
        "answer": 0,
        "explanation": "Optional context for the answer."
      },
      {
        "type": "true_false",
        "question": "HTTP is stateful by default.",
        "answer": false,
        "explanation": "..."
      },
      {
        "type": "short_answer",
        "question": "Name the database isolation level that prevents phantom reads.",
        "answer": "serializable",
        "accept_aliases": ["serialisable"],
        "explanation": "..."
      }
    ]

The resulting HTML file is fully standalone.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "assets" / "quiz_template.html"


def quiz_id_from(title: str, num_questions: int) -> str:
    raw = f"{title}|{num_questions}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def validate_questions(questions: list) -> list[str]:
    errors = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            errors.append(f"Q{i}: not an object")
            continue
        t = q.get("type")
        if t not in ("mcq", "true_false", "short_answer"):
            errors.append(f"Q{i}: type must be mcq/true_false/short_answer (got {t})")
            continue
        if "question" not in q:
            errors.append(f"Q{i}: missing 'question' field")
        if t == "mcq":
            if not isinstance(q.get("options"), list) or len(q["options"]) < 2:
                errors.append(f"Q{i}: mcq needs at least 2 options")
            ans = q.get("answer")
            if not isinstance(ans, int) or ans < 0 or ans >= len(q.get("options", [])):
                errors.append(f"Q{i}: mcq answer must be an index into options (got {ans})")
        elif t == "true_false":
            if q.get("answer") not in (True, False):
                errors.append(f"Q{i}: true_false answer must be true or false")
        elif t == "short_answer":
            if not isinstance(q.get("answer"), str) or not q["answer"].strip():
                errors.append(f"Q{i}: short_answer answer must be a non-empty string")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--questions", type=Path, help="Path to JSON file with question list")
    p.add_argument("--questions-stdin", action="store_true", help="Read JSON questions from stdin")
    p.add_argument("--output", type=Path, required=True, help="Output HTML path")
    p.add_argument("--title", default="Quiz", help="Title shown in the app")
    p.add_argument("--template", type=Path, default=TEMPLATE, help="Override the HTML template path")
    args = p.parse_args()

    if args.questions_stdin:
        questions = json.loads(sys.stdin.read())
    elif args.questions:
        questions = json.loads(args.questions.read_text(encoding="utf-8"))
    else:
        print("Error: must provide --questions or --questions-stdin", file=sys.stderr)
        return 1

    if not isinstance(questions, list):
        print("Error: questions must be a list", file=sys.stderr)
        return 1

    errs = validate_questions(questions)
    if errs:
        print("Validation errors:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if not args.template.exists():
        print(f"Error: template not found at {args.template}", file=sys.stderr)
        return 1

    template = args.template.read_text(encoding="utf-8")
    quiz_json = json.dumps(questions, ensure_ascii=False)
    qid = quiz_id_from(args.title, len(questions))

    output = (template
        .replace("__TITLE__", args.title)
        .replace("__QUIZ_ID__", qid)
        .replace("__QUIZ_JSON__", quiz_json))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"Wrote {len(questions)} questions to {args.output}")
    print(f"Open with: open {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
