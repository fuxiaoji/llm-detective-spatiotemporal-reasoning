from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path
from typing import Any

from .models import ModelClient
from .prompts import build_prompt
from .schemas import Prediction, Sample


def parse_prediction(text: str, sample: Sample) -> tuple[Any, str | None]:
    lowered = text.strip()
    if sample.dataset == "detectiveqa":
        matches = re.findall(r"\b([ABCD])\b", lowered.upper())
        if matches:
            return matches[-1], None
        return None, "Could not parse option letter"
    if sample.dataset == "turnabout":
        match = re.search(r"\[[^\]]+\]", lowered)
        if match:
            try:
                return ast.literal_eval(match.group(0)), None
            except Exception as e:
                return None, f"Could not parse pair: {e}"
        return None, "Could not parse evidence-testimony pair"
    matches = re.findall(r"(?<![\w.-])(\d+)(?![\w.-])", lowered)
    if matches:
        return int(matches[-1]), None
    return None, "Could not parse option index"


def is_correct(prediction: Any, gold: Any, sample: Sample) -> bool:
    if prediction is None:
        return False
    if sample.dataset == "turnabout":
        return prediction in gold if isinstance(gold, list) else prediction == gold
    return prediction == gold


def run_method(sample: Sample, method: str, client: ModelClient, model_name: str) -> Prediction:
    intermediate: dict[str, Any] = {}
    if method == "critic_checklist":
        draft_prompt = build_prompt("cot", sample)
        draft_resp = client.generate(draft_prompt)
        intermediate["draft"] = draft_resp.text
        prompt = build_prompt(method, sample, draft=draft_resp.text)
    else:
        prompt = build_prompt(method, sample)
    resp = client.generate(prompt)
    pred, parse_error = parse_prediction(resp.text, sample)
    return Prediction(
        sample_id=sample.id,
        dataset=sample.dataset,
        split=sample.split,
        method=method,
        model=model_name,
        prompt=prompt,
        raw_output=resp.text,
        prediction=pred,
        gold=sample.answer,
        correct=is_correct(pred, sample.answer, sample),
        parse_error=parse_error,
        intermediate=intermediate,
        usage={
            "prompt_tokens": resp.prompt_tokens,
            "completion_tokens": resp.completion_tokens,
            "total_tokens": resp.total_tokens,
        },
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_summary_csv(path: Path, predictions: list[Prediction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(predictions)
    correct = sum(1 for p in predictions if p.correct)
    parse_errors = sum(1 for p in predictions if p.parse_error)
    token_total = sum((p.usage.get("total_tokens") or 0) for p in predictions)
    row = {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0,
        "parse_errors": parse_errors,
        "total_tokens": token_total,
        "avg_tokens": token_total / total if total else 0,
    }
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

