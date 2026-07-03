from __future__ import annotations

import argparse
import json

from .registry import (
    list_dataset_specs,
    list_evaluator_specs,
    list_method_specs,
    list_skill_specs,
    load_registered_dataset,
)
from .runner import RunConfig, run_dataset


def cmd_list_datasets(_: argparse.Namespace) -> None:
    for spec in list_dataset_specs():
        print(json.dumps(spec, ensure_ascii=False))


def cmd_list_methods(_: argparse.Namespace) -> None:
    for spec in list_method_specs():
        print(json.dumps(spec, ensure_ascii=False))


def cmd_list_skills(_: argparse.Namespace) -> None:
    for spec in list_skill_specs():
        print(json.dumps(spec, ensure_ascii=False))


def cmd_list_evaluators(_: argparse.Namespace) -> None:
    for spec in list_evaluator_specs():
        print(json.dumps(spec, ensure_ascii=False))


def cmd_peek(args: argparse.Namespace) -> None:
    samples = load_registered_dataset(args.dataset, args.split, limit=args.limit)
    for sample in samples:
        print(json.dumps(sample.to_dict(), ensure_ascii=False, indent=2)[: args.max_chars])


def _parse_skills(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def cmd_eval(args: argparse.Namespace) -> None:
    config = RunConfig(
        dataset=args.dataset,
        split=args.split,
        method=args.method,
        skills=_parse_skills(args.skills),
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        base_url=args.base_url,
        thinking=args.thinking,
        reasoning_effort=args.reasoning_effort,
        limit=args.limit,
        runs_dir=args.runs_dir,
    )
    artifacts = run_dataset(config)
    for idx, pred in enumerate(artifacts.predictions, 1):
        print(
            f"[{idx}/{len(artifacts.predictions)}] {pred.sample_id} "
            f"correct={pred.correct} pred={pred.prediction} gold={pred.gold}"
        )
    print(json.dumps({"run_id": artifacts.run_id, "summary": artifacts.summary}, ensure_ascii=False))
    print(f"wrote {artifacts.manifest_path}")
    print(f"wrote {artifacts.predictions_path}")
    print(f"wrote {artifacts.summary_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detective reasoning reproduction toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-datasets")
    p.set_defaults(func=cmd_list_datasets)

    p = sub.add_parser("list-methods")
    p.set_defaults(func=cmd_list_methods)

    p = sub.add_parser("list-skills")
    p.set_defaults(func=cmd_list_skills)

    p = sub.add_parser("list-evaluators")
    p.set_defaults(func=cmd_list_evaluators)

    p = sub.add_parser("peek")
    p.add_argument("--dataset", required=True)
    p.add_argument("--split", default=None)
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--max-chars", type=int, default=4000)
    p.set_defaults(func=cmd_peek)

    p = sub.add_parser("eval")
    p.add_argument("--dataset", required=True)
    p.add_argument("--split", default=None)
    p.add_argument("--method", default="direct", choices=[s["name"] for s in list_method_specs()])
    p.add_argument("--skills", default="", help="Comma-separated registered skills, e.g. external_evidence_bank,dummy_skill")
    p.add_argument("--provider", default="mock", choices=["mock", "openai"])
    p.add_argument("--model", default="mock")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=800)
    p.add_argument("--base-url", default=None)
    p.add_argument("--thinking", default=None, choices=[None, "enabled", "disabled"])
    p.add_argument("--reasoning-effort", default=None, choices=[None, "low", "medium", "high"])
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--runs-dir", default=None)
    p.set_defaults(func=cmd_eval)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
