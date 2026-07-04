#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


DATASET_LABELS = {
    "musr": "MuSR",
    "detectbench": "DetectBench",
    "detectiveqa": "DetectiveQA",
    "turnabout": "TurnaboutLLM",
}


MODEL_LABELS = {
    "deepseek_v4_flash": "DeepSeek V4 Flash",
    "minimax_m3": "MiniMax-M3",
}


def load_rows(index_path: Path) -> list[dict]:
    return json.loads(index_path.read_text(encoding="utf-8"))


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def condition_label(row: dict) -> str:
    return "Skill" if row["condition"] == "paper_skill" else "Baseline"


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "dataset",
                "split",
                "model_label",
                "model",
                "condition",
                "skill",
                "total",
                "correct",
                "accuracy",
                "parse_errors",
                "total_tokens",
                "avg_tokens",
                "elapsed_sec",
                "run_id",
                "returncode",
            ],
        )
        writer.writeheader()
        for row in rows:
            summary = row["summary"]
            writer.writerow(
                {
                    "dataset": row["dataset"],
                    "split": row["split"],
                    "model_label": row["model_label"],
                    "model": row["model"],
                    "condition": row["condition"],
                    "skill": row.get("skill") or "",
                    "total": summary["total"],
                    "correct": summary["correct"],
                    "accuracy": summary["accuracy"],
                    "parse_errors": summary["parse_errors"],
                    "total_tokens": summary["total_tokens"],
                    "avg_tokens": summary["avg_tokens"],
                    "elapsed_sec": row.get("elapsed_sec", 0),
                    "run_id": row.get("run_id") or "",
                    "returncode": row.get("returncode"),
                }
            )


def write_svg(rows: list[dict], path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    grouped: dict[tuple[str, str], dict[str, float]] = {}
    for row in rows:
        key = (row["dataset"], row["model_label"])
        grouped.setdefault(key, {})[row["condition"]] = row["summary"]["accuracy"]

    items = sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1]))
    width = 1180
    left = 260
    top = 80
    row_h = 44
    chart_w = 760
    height = top + len(items) * row_h + 80
    colors = {"baseline_direct": "#8fb3ff", "paper_skill": "#ff9f6e"}

    def x(acc: float) -> float:
        return left + chart_w * acc

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="36" font-size="24" font-family="Arial" font-weight="700">{title}</text>',
        f'<line x1="{left}" y1="{top - 25}" x2="{left + chart_w}" y2="{top - 25}" stroke="#333"/>',
    ]
    for tick in range(0, 101, 10):
        tx = left + chart_w * tick / 100
        lines.append(f'<line x1="{tx}" y1="{top - 31}" x2="{tx}" y2="{height - 50}" stroke="#eeeeee"/>')
        lines.append(f'<text x="{tx - 10}" y="{top - 38}" font-size="12" font-family="Arial" fill="#666">{tick}%</text>')

    for i, ((dataset, model), vals) in enumerate(items):
        y = top + i * row_h
        label = f"{DATASET_LABELS.get(dataset, dataset)} / {MODEL_LABELS.get(model, model)}"
        baseline = vals.get("baseline_direct", 0)
        skill = vals.get("paper_skill", 0)
        lines.append(f'<text x="20" y="{y + 18}" font-size="14" font-family="Arial" fill="#222">{label}</text>')
        lines.append(f'<rect x="{left}" y="{y}" width="{max(1, x(baseline) - left)}" height="16" fill="{colors["baseline_direct"]}"/>')
        lines.append(f'<rect x="{left}" y="{y + 20}" width="{max(1, x(skill) - left)}" height="16" fill="{colors["paper_skill"]}"/>')
        lines.append(f'<text x="{x(baseline) + 6}" y="{y + 13}" font-size="12" font-family="Arial">{pct(baseline)}</text>')
        lines.append(f'<text x="{x(skill) + 6}" y="{y + 33}" font-size="12" font-family="Arial">{pct(skill)}</text>')

    legend_y = height - 25
    lines.extend(
        [
            f'<rect x="{left}" y="{legend_y - 12}" width="16" height="12" fill="{colors["baseline_direct"]}"/>',
            f'<text x="{left + 22}" y="{legend_y}" font-size="13" font-family="Arial">Baseline</text>',
            f'<rect x="{left + 110}" y="{legend_y - 12}" width="16" height="12" fill="{colors["paper_skill"]}"/>',
            f'<text x="{left + 132}" y="{legend_y}" font-size="13" font-family="Arial">Paper-inspired skill</text>',
            "</svg>",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def result_table(rows: list[dict], lang: str) -> str:
    if lang == "zh":
        header = "| 数据集 | 模型 | 方法 | Skill | 正确数 | 准确率 | Parse errors | Run ID |\n|---|---|---|---|---:|---:|---:|---|"
    else:
        header = "| Dataset | Model | Condition | Skill | Correct | Accuracy | Parse errors | Run ID |\n|---|---|---|---|---:|---:|---:|---|"
    lines = [header]
    for row in rows:
        summary = row["summary"]
        lines.append(
            "| "
            + " | ".join(
                [
                    DATASET_LABELS.get(row["dataset"], row["dataset"]),
                    MODEL_LABELS.get(row["model_label"], row["model_label"]),
                    condition_label(row),
                    f"`{row.get('skill')}`" if row.get("skill") else "-",
                    f"{summary['correct']}/{summary['total']}",
                    pct(summary["accuracy"]),
                    str(summary["parse_errors"]),
                    f"`{row.get('run_id')}`",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def delta_table(rows: list[dict], lang: str) -> str:
    grouped: dict[tuple[str, str], dict[str, dict]] = {}
    for row in rows:
        grouped.setdefault((row["dataset"], row["model_label"]), {})[row["condition"]] = row
    if lang == "zh":
        header = "| 数据集 | 模型 | Baseline | Skill | 差值 |\n|---|---|---:|---:|---:|"
    else:
        header = "| Dataset | Model | Baseline | Skill | Delta |\n|---|---|---:|---:|---:|"
    lines = [header]
    for (dataset, model), vals in sorted(grouped.items()):
        base = vals.get("baseline_direct", {}).get("summary", {}).get("accuracy", 0)
        skill = vals.get("paper_skill", {}).get("summary", {}).get("accuracy", 0)
        delta = skill - base
        lines.append(
            f"| {DATASET_LABELS.get(dataset, dataset)} | {MODEL_LABELS.get(model, model)} | "
            f"{pct(base)} | {pct(skill)} | {delta * 100:+.1f} pp |"
        )
    return "\n".join(lines)


def write_report(rows: list[dict], path: Path, lang: str, runs_dir: str, figure_path: str) -> None:
    all_ok = all(row.get("returncode") == 0 for row in rows)
    if lang == "zh":
        text = f"""# 50 条样本扩大复现报告

生成时间：2026-07-04  
实验目录：`{runs_dir}`  
可视化：`{figure_path}`  

## 1. 实验范围

本轮把上一版 10 条 smoke test 扩大到每组 50 条。实验矩阵为 4 个数据集 × 2 个模型 × 2 种方法，共 16 组、800 次模型调用。

- 数据集：MuSR murder mystery、DetectBench test-hard、DetectiveQA en_human、TurnaboutLLM AA。
- 模型：DeepSeek V4 Flash、MiniMax-M3。
- 方法：Baseline 直接回答；Skill 使用对应任务的 paper-inspired prompt。
- DetectiveQA：前 50 条所需小说正文已下载，本轮 50/50 样本均加载小说上下文。每题根据 `answer_position` 取答案前段落，并保留尾部最多 24,000 字符。
- 运行状态：{"全部 16 组完成" if all_ok else "存在失败组，请查看结果表中的 returncode"}。

## 2. 总结果

{result_table(rows, "zh")}

## 3. Skill 提升/下降

{delta_table(rows, "zh")}

## 4. 初步观察

MuSR 仍然是最适合第一阶段主实验的数据集之一，因为它稳定、成本适中，且能直接观察结构化 CoT 是否提升多步侦探推理。

DetectBench 的结果需要看模型差异：如果 skill 对某个模型提升、对另一个模型下降，就说明“外部结构化提示”不是无条件有效，后续应拆成 evidence card、timeline、contradiction check、verifier 做 ablation。

DetectiveQA 本轮已经是带小说正文的长文本测试。由于固定 24,000 字符尾部截断仍然比较粗糙，下一步更有研究价值的是加入 retrieval/context selection，比较“固定截断”和“问题相关证据检索”的差异。

TurnaboutLLM 如果仍然低分，优先不要把它当主 benchmark，而应把它改造成候选 pair 选择任务：先枚举 evidence-testimony pair，再让模型在候选项中选择，减少编号和顺序错误。

## 5. 下一步

1. 在 MuSR 和 DetectBench 上做 skill ablation。
2. 给 DetectiveQA 加检索式外部证据库。
3. 将 GUI 增加图表入口，显示不同模型/方法的准确率和 token 成本。
4. TurnaboutLLM 单独做 candidate-pair 版本 evaluator。
"""
    else:
        text = f"""# 50-Sample Expanded Reproduction Report

Generated on 2026-07-04  
Experiment directory: `{runs_dir}`  
Visualization: `{figure_path}`  

## 1. Scope

This run expands the previous 10-sample smoke test to 50 samples per condition. The matrix contains 4 datasets × 2 models × 2 methods, for 16 runs and 800 model calls.

- Datasets: MuSR murder mystery, DetectBench test-hard, DetectiveQA en_human, and TurnaboutLLM AA.
- Models: DeepSeek V4 Flash and MiniMax-M3.
- Conditions: direct baseline and a paper-inspired task skill.
- DetectiveQA: all novels required by the first 50 samples were downloaded locally. All 50/50 samples loaded novel context. The loader includes paragraphs up to `answer_position` and keeps the final 24,000 characters.
- Run status: {"all 16 runs completed" if all_ok else "some runs failed; inspect returncode/error fields"}.

## 2. Results

{result_table(rows, "en")}

## 3. Skill Delta

{delta_table(rows, "en")}

## 4. Initial Observations

MuSR remains a good first-stage benchmark because it is stable, affordable, and directly tests whether structured CoT improves multi-step mystery reasoning.

DetectBench should be interpreted per model. If the skill helps one model but hurts another, external structured prompting is not universally beneficial. The next step should split the large prompt into evidence card, timeline, contradiction check, and verifier ablations.

DetectiveQA is now a true novel-context test. However, fixed 24,000-character tail truncation is still a rough context strategy. The stronger research direction is to compare fixed truncation with retrieval-based external evidence selection.

TurnaboutLLM should not be used as a main benchmark until it has a candidate-pair interface. The task asks for exact evidence-testimony pairs, so enumerating candidate pairs should reduce numbering and order errors.

## 5. Next Steps

1. Run skill ablations on MuSR and DetectBench.
2. Add retrieval-based external evidence for DetectiveQA.
3. Add GUI charts for accuracy and token cost across models/methods.
4. Build a candidate-pair evaluator for TurnaboutLLM.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CSV, SVG, and Markdown reports.")
    parser.add_argument("--runs-dir", default="runs/reproduction_50_20260704")
    parser.add_argument("--out-dir", default="outputs/reproduction_50_20260704")
    args = parser.parse_args()

    runs_dir = PROJECT_ROOT / args.runs_dir
    out_dir = PROJECT_ROOT / args.out_dir
    rows = load_rows(runs_dir / "experiment_index.json")
    rows = [row for row in rows if row.get("returncode") == 0]

    csv_path = out_dir / "summary.csv"
    svg_path = out_dir / "accuracy_by_dataset_model.svg"
    write_csv(rows, csv_path)
    write_svg(rows, svg_path, "50-Sample Reproduction Accuracy")

    write_report(
        rows,
        PROJECT_ROOT / "notes/reproduction_50_report_zh.md",
        "zh",
        args.runs_dir,
        str(svg_path.relative_to(PROJECT_ROOT)),
    )
    write_report(
        rows,
        PROJECT_ROOT / "notes/reproduction_50_report.md",
        "en",
        args.runs_dir,
        str(svg_path.relative_to(PROJECT_ROOT)),
    )
    print(f"wrote {csv_path}")
    print(f"wrote {svg_path}")
    print("wrote notes/reproduction_50_report_zh.md")
    print("wrote notes/reproduction_50_report.md")


if __name__ == "__main__":
    main()
