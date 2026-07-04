#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.detective_reasoning.runner import RunConfig, run_dataset


DATASETS = [
    {
        "dataset": "musr",
        "split": "murder_mystery",
        "skill": "musr_cot_plus",
        "max_tokens": 1600,
    },
    {
        "dataset": "detectbench",
        "split": "test-hard",
        "skill": "detectbench_detective_prompt",
        "max_tokens": 1600,
    },
    {
        "dataset": "detectiveqa",
        "split": "en_human",
        "skill": "detectiveqa_stepwise_reasoning",
        "max_tokens": 2200,
    },
    {
        "dataset": "turnabout",
        "split": "AA",
        "skill": "turnabout_contradiction_matrix",
        "max_tokens": 2200,
    },
]


MODELS = [
    {
        "label": "deepseek_v4_flash",
        "model": "deepseek-v4-flash",
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "thinking": "disabled",
    },
    {
        "label": "minimax_m3",
        "model": "MiniMax-M3",
        "base_url": "https://api.minimaxi.com/v1",
        "api_key_env": "MINIMAX_API_KEY",
        "thinking": "disabled",
    },
]


def read_index(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def write_index(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def has_completed(rows: list[dict], dataset: str, split: str, model_label: str, condition: str) -> bool:
    for row in rows:
        if (
            row.get("dataset") == dataset
            and row.get("split") == split
            and row.get("model_label") == model_label
            and row.get("condition") == condition
            and row.get("returncode") == 0
        ):
            return True
    return False


def run_one(dataset_cfg: dict, model_cfg: dict, condition: str, limit: int, runs_dir: Path) -> dict:
    skill = dataset_cfg["skill"] if condition == "paper_skill" else ""
    api_key = os.getenv(model_cfg["api_key_env"])
    if not api_key:
        raise RuntimeError(f"{model_cfg['api_key_env']} is required")
    config = RunConfig(
        dataset=dataset_cfg["dataset"],
        split=dataset_cfg["split"],
        method="direct",
        skills=[skill] if skill else [],
        provider="openai",
        model=model_cfg["model"],
        temperature=0.0,
        max_tokens=dataset_cfg["max_tokens"],
        base_url=model_cfg["base_url"],
        thinking=model_cfg.get("thinking"),
        api_key=api_key,
        limit=limit,
        runs_dir=str(runs_dir),
    )
    started = time.time()
    artifacts = run_dataset(config)
    elapsed = time.time() - started
    for idx, pred in enumerate(artifacts.predictions, 1):
        print(
            f"[{idx}/{len(artifacts.predictions)}] {pred.sample_id} "
            f"correct={pred.correct} pred={pred.prediction} gold={pred.gold}",
            flush=True,
        )
    return {
        "dataset": dataset_cfg["dataset"],
        "split": dataset_cfg["split"],
        "skill": skill,
        "model_label": model_cfg["label"],
        "model": model_cfg["model"],
        "condition": condition,
        "run_id": artifacts.run_id,
        "summary": artifacts.summary,
        "elapsed_sec": round(elapsed, 1),
        "returncode": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the 50-sample reproduction batch.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--runs-dir", default="runs/reproduction_50_20260704")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    runs_dir = PROJECT_ROOT / args.runs_dir
    index_path = runs_dir / "experiment_index.json"
    rows = read_index(index_path)

    for dataset_cfg in DATASETS:
        for model_cfg in MODELS:
            for condition in ["baseline_direct", "paper_skill"]:
                if args.resume and has_completed(
                    rows,
                    dataset_cfg["dataset"],
                    dataset_cfg["split"],
                    model_cfg["label"],
                    condition,
                ):
                    print(
                        "SKIP",
                        dataset_cfg["dataset"],
                        dataset_cfg["split"],
                        model_cfg["label"],
                        condition,
                        flush=True,
                    )
                    continue
                print(
                    "\n=== RUN",
                    f"{dataset_cfg['dataset']}:{dataset_cfg['split']}",
                    "|",
                    model_cfg["label"],
                    "|",
                    condition,
                    "===",
                    flush=True,
                )
                try:
                    row = run_one(dataset_cfg, model_cfg, condition, args.limit, runs_dir)
                except Exception as exc:
                    row = {
                        "dataset": dataset_cfg["dataset"],
                        "split": dataset_cfg["split"],
                        "skill": dataset_cfg["skill"] if condition == "paper_skill" else "",
                        "model_label": model_cfg["label"],
                        "model": model_cfg["model"],
                        "condition": condition,
                        "run_id": None,
                        "summary": {
                            "total": 0,
                            "correct": 0,
                            "accuracy": 0,
                            "parse_errors": 0,
                            "total_tokens": 0,
                            "avg_tokens": 0,
                        },
                        "elapsed_sec": 0,
                        "returncode": 1,
                        "error": str(exc),
                    }
                    print("ERROR", json.dumps(row, ensure_ascii=False), flush=True)
                rows.append(row)
                write_index(index_path, rows)
                print(json.dumps(row, ensure_ascii=False), flush=True)

    print("\n=== EXPERIMENT INDEX ===")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
