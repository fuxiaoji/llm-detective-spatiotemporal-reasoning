from __future__ import annotations

import argparse
import json
from pathlib import Path

from .datasets import load_dataset, list_dataset_specs
from .evaluation import run_method, write_jsonl, write_summary_csv
from .models import ModelConfig, make_model_client


def cmd_list_datasets(_: argparse.Namespace) -> None:
    for spec in list_dataset_specs():
        print(json.dumps(spec, ensure_ascii=False))


def cmd_peek(args: argparse.Namespace) -> None:
    samples = load_dataset(args.dataset, args.split, limit=args.limit)
    for sample in samples:
        print(json.dumps(sample.to_dict(), ensure_ascii=False, indent=2)[: args.max_chars])


def cmd_eval(args: argparse.Namespace) -> None:
    samples = load_dataset(args.dataset, args.split, limit=args.limit)
    config = ModelConfig(
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        base_url=args.base_url,
    )
    client = make_model_client(config)
    predictions = []
    for idx, sample in enumerate(samples, 1):
        try:
            pred = run_method(sample, args.method, client, args.model)
        except Exception as e:
            # Preserve batch progress even if a provider call fails.
            from .schemas import Prediction

            pred = Prediction(
                sample_id=sample.id,
                dataset=sample.dataset,
                split=sample.split,
                method=args.method,
                model=args.model,
                prompt="",
                raw_output="",
                prediction=None,
                gold=sample.answer,
                correct=False,
                parse_error=f"runtime_error: {e}",
            )
        predictions.append(pred)
        print(f"[{idx}/{len(samples)}] {sample.id} correct={pred.correct} pred={pred.prediction} gold={pred.gold}")
    out_dir = Path(args.output_dir)
    stem = f"{args.dataset}_{args.split}_{args.method}_{args.model}".replace("/", "_")
    write_jsonl(out_dir / f"{stem}.jsonl", [p.to_dict() for p in predictions])
    write_summary_csv(out_dir / f"{stem}_summary.csv", predictions)
    print(f"wrote {out_dir / f'{stem}.jsonl'}")
    print(f"wrote {out_dir / f'{stem}_summary.csv'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detective reasoning reproduction toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-datasets")
    p.set_defaults(func=cmd_list_datasets)

    p = sub.add_parser("peek")
    p.add_argument("--dataset", required=True)
    p.add_argument("--split", default=None)
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--max-chars", type=int, default=4000)
    p.set_defaults(func=cmd_peek)

    p = sub.add_parser("eval")
    p.add_argument("--dataset", required=True)
    p.add_argument("--split", default=None)
    p.add_argument("--method", default="direct", choices=["direct", "cot", "reflection", "evidence_card", "critic_checklist"])
    p.add_argument("--provider", default="mock", choices=["mock", "openai"])
    p.add_argument("--model", default="mock")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=800)
    p.add_argument("--base-url", default=None)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--output-dir", default="outputs")
    p.set_defaults(func=cmd_eval)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

