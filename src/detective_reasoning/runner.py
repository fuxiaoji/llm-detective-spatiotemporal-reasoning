from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluation import run_method, write_jsonl, write_summary_csv
from .models import ModelConfig, make_model_client
from .registry import load_registered_dataset
from .schemas import Prediction, Sample


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_DIR = PROJECT_ROOT / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_run_id(prefix: str = "run") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{stamp}_{uuid.uuid4().hex[:8]}"


@dataclass
class RunConfig:
    dataset: str
    split: str | None
    method: str
    skills: list[str]
    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 800
    base_url: str | None = None
    thinking: str | None = None
    reasoning_effort: str | None = None
    api_key: str | None = None
    limit: int | None = None
    evaluator: str = "exact_match"
    run_id: str | None = None
    runs_dir: str | None = None


@dataclass
class RunArtifacts:
    run_id: str
    run_dir: str
    manifest_path: str
    predictions_path: str
    summary_path: str
    predictions: list[Prediction]
    summary: dict[str, Any]


def summarize_predictions(predictions: list[Prediction]) -> dict[str, Any]:
    total = len(predictions)
    correct = sum(1 for p in predictions if p.correct)
    parse_errors = sum(1 for p in predictions if p.parse_error)
    token_total = sum((p.usage.get("total_tokens") or 0) for p in predictions)
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0,
        "parse_errors": parse_errors,
        "total_tokens": token_total,
        "avg_tokens": token_total / total if total else 0,
    }


def _write_manifest(path: Path, config: RunConfig, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    saved_config = asdict(config)
    if saved_config.get("api_key"):
        saved_config["api_key"] = "<provided in GUI; not saved>"
    manifest = {
        "run_id": config.run_id,
        "created_at": utc_now(),
        "config": saved_config,
        "summary": summary,
        "note": (
            "Saved reasoning contains only model-visible outputs, prompts, and "
            "tool traces. Hidden model reasoning is not captured."
        ),
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def run_samples(samples: list[Sample], config: RunConfig) -> RunArtifacts:
    run_id = config.run_id or make_run_id()
    config.run_id = run_id
    runs_dir = Path(config.runs_dir) if config.runs_dir else DEFAULT_RUNS_DIR
    run_dir = runs_dir / run_id

    model_config = ModelConfig(
        provider=config.provider,
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        base_url=config.base_url,
        thinking=config.thinking,
        reasoning_effort=config.reasoning_effort,
        api_key=config.api_key,
    )
    client = make_model_client(model_config)

    predictions: list[Prediction] = []
    for sample in samples:
        try:
            pred = run_method(
                sample,
                config.method,
                client,
                config.model,
                provider=config.provider,
                skills=config.skills,
                run_id=run_id,
            )
        except Exception as e:
            pred = Prediction(
                run_id=run_id,
                sample_id=sample.id,
                dataset=sample.dataset,
                split=sample.split,
                method=config.method,
                skills=config.skills,
                provider=config.provider,
                model=config.model,
                prompt="",
                raw_output="",
                prediction=None,
                gold=sample.answer,
                correct=False,
                parse_error=f"runtime_error: {e}",
                created_at=utc_now(),
            )
        predictions.append(pred)

    summary = summarize_predictions(predictions)
    predictions_path = run_dir / "predictions.jsonl"
    summary_path = run_dir / "summary.csv"
    manifest_path = run_dir / "manifest.json"
    write_jsonl(predictions_path, [p.to_dict() for p in predictions])
    write_summary_csv(summary_path, predictions)
    _write_manifest(manifest_path, config, summary)

    return RunArtifacts(
        run_id=run_id,
        run_dir=str(run_dir),
        manifest_path=str(manifest_path),
        predictions_path=str(predictions_path),
        summary_path=str(summary_path),
        predictions=predictions,
        summary=summary,
    )


def run_dataset(config: RunConfig) -> RunArtifacts:
    samples = load_registered_dataset(config.dataset, config.split, config.limit)
    return run_samples(samples, config)
