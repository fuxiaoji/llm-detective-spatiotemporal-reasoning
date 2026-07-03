from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from .models import ModelClient
from .registry import build_registered_prompt
from .schemas import Prediction, Sample


def parse_prediction(text: str, sample: Sample) -> tuple[Any, str | None]:
    lowered = text.strip()
    if sample.dataset == "detectiveqa":
        matches = re.findall(r"\b([ABCD])\b", lowered.upper())
        if matches:
            return matches[-1], None
        return None, "Could not parse option letter"
    if sample.dataset == "turnabout":
        matches = re.findall(r"\[[^\]]+\]", lowered)
        for candidate in reversed(matches):
            try:
                parsed = ast.literal_eval(candidate)
                if (
                    isinstance(parsed, list)
                    and len(parsed) == 2
                    and all(isinstance(x, int) for x in parsed)
                ):
                    return parsed, None
            except Exception as e:
                last_error = str(e)
                continue
        return None, "Could not parse valid evidence-testimony pair"
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_method(
    sample: Sample,
    method: str,
    client: ModelClient,
    model_name: str,
    *,
    provider: str = "unknown",
    skills: list[str] | None = None,
    run_id: str = "",
) -> Prediction:
    active_skills = skills or []
    intermediate: dict[str, Any] = {}
    if method == "critic_checklist":
        draft_prompt = build_registered_prompt("cot", sample, skills=active_skills, intermediate=intermediate)
        draft_resp = client.generate(draft_prompt)
        intermediate["draft"] = draft_resp.text
        intermediate["draft_prompt"] = draft_prompt
        prompt = build_registered_prompt(
            method,
            sample,
            draft=draft_resp.text,
            skills=active_skills,
            intermediate=intermediate,
        )
    else:
        prompt = build_registered_prompt(method, sample, skills=active_skills, intermediate=intermediate)
    resp = client.generate(prompt)
    if resp.reasoning_content:
        intermediate["reasoning_content"] = resp.reasoning_content
    pred, parse_error = parse_prediction(resp.text, sample)
    return Prediction(
        run_id=run_id,
        sample_id=sample.id,
        dataset=sample.dataset,
        split=sample.split,
        method=method,
        skills=active_skills,
        provider=provider,
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
        created_at=utc_now(),
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
