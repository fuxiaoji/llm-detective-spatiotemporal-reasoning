from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schemas import Sample


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _read_detectiveqa_novel_context(
    lang: str,
    novel_id: int | str | None,
    answer_position: int | str | None,
    max_chars: int = 24000,
) -> tuple[str | None, dict]:
    if novel_id is None:
        return None, {"context_status": "missing_novel_id"}
    root = DATA_ROOT / "DetectiveQA" / "hf_dataset" / f"novel_data_{lang}"
    matches = sorted(root.glob(f"{novel_id}-*.txt"))
    if not matches:
        return None, {"context_status": "novel_text_not_found", "novel_text_dir": str(root)}
    path = matches[0]
    paragraphs: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                paragraphs.append(line)
    end_position = None
    try:
        end_position = int(answer_position) if answer_position is not None else None
    except (TypeError, ValueError):
        end_position = None
    if end_position is not None and end_position > 0:
        selected = paragraphs[: min(end_position, len(paragraphs))]
    else:
        selected = paragraphs
    context = "\n".join(selected)
    truncated = False
    if len(context) > max_chars:
        context = context[-max_chars:]
        truncated = True
    return context, {
        "context_status": "loaded",
        "novel_text_path": str(path),
        "answer_position": answer_position,
        "paragraphs_used": len(selected),
        "context_chars": len(context),
        "truncated_from_tail": truncated,
    }


def load_musr(domain: str = "murder_mystery", limit: int | None = None) -> list[Sample]:
    path = DATA_ROOT / "MuSR" / "datasets" / f"{domain}.json"
    rows = _read_json(path)
    samples: list[Sample] = []
    for i, item in enumerate(rows):
        questions = item.get("questions") or []
        if not questions:
            continue
        q = questions[0]
        samples.append(
            Sample(
                id=f"musr_{domain}_{i}",
                dataset="musr",
                split=domain,
                context=item.get("context"),
                question=q.get("question", ""),
                options=q.get("choices"),
                answer=q.get("answer"),
                evidence=None,
                reasoning={
                    "intermediate_trees": q.get("intermediate_trees"),
                    "intermediate_data": q.get("intermediate_data"),
                },
                metadata={"domain": domain, "source_path": str(path), "index": i},
            )
        )
        if limit is not None and len(samples) >= limit:
            break
    return samples


def load_detectbench(split: str = "test-hard", limit: int | None = None) -> list[Sample]:
    path = DATA_ROOT / "DetectBench" / "DetectBench_eng_v1.3" / f"{split}.jsonl"
    samples: list[Sample] = []
    for i, item in enumerate(_read_jsonl(path)):
        clue = item.get("clue_graph") or item.get("reasoning_process")
        evidence = None
        reasoning = None
        if isinstance(clue, dict):
            evidence = clue.get("evidence")
            reasoning = clue.get("multi_hop_reasoning") or clue
        else:
            reasoning = clue
        samples.append(
            Sample(
                id=f"detectbench_{split}_{item.get('id', i)}",
                dataset="detectbench",
                split=split,
                context=item.get("context"),
                question=item.get("question", ""),
                options=item.get("options"),
                answer=item.get("answer"),
                evidence=evidence,
                reasoning=reasoning,
                metadata={"source_path": str(path), "index": i, "raw_id": item.get("id")},
            )
        )
        if limit is not None and len(samples) >= limit:
            break
    return samples


def load_detectiveqa_annotations(
    lang: str = "en", anno: str = "human", limit: int | None = None
) -> list[Sample]:
    anno_dir = "human_anno" if anno == "human" else "AIsup_anno"
    root = DATA_ROOT / "DetectiveQA" / "hf_dataset" / f"anno_data_{lang}" / anno_dir
    samples: list[Sample] = []
    for path in sorted(root.glob("*.json")):
        rows = _read_json(path)
        for novel in rows:
            for qi, q in enumerate(novel.get("questions", [])):
                context, context_meta = _read_detectiveqa_novel_context(
                    lang=lang,
                    novel_id=novel.get("novel_id"),
                    answer_position=q.get("answer_position"),
                )
                samples.append(
                    Sample(
                        id=f"detectiveqa_{lang}_{anno}_{novel.get('novel_id')}_{qi}",
                        dataset="detectiveqa",
                        split=f"{lang}_{anno}",
                        context=context,
                        question=q.get("question", ""),
                        options=q.get("options"),
                        answer=q.get("answer"),
                        evidence={
                            "reasoning": q.get("reasoning"),
                            "clue_position": q.get("clue_position"),
                            "answer_position": q.get("answer_position"),
                        },
                        reasoning=q.get("reasoning"),
                        metadata={
                            "source_path": str(path),
                            "novel_id": novel.get("novel_id"),
                            "num_paragraphs": novel.get("num_paragraphs"),
                            "annotation": anno,
                            "language": lang,
                            **context_meta,
                        },
                    )
                )
                if limit is not None and len(samples) >= limit:
                    return samples
    return samples


def load_turnabout(source: str = "AA", limit: int | None = None) -> list[Sample]:
    file_name = "AA_integrated_dataset.json" if source.upper() == "AA" else "DR_integrate_dataset.json"
    path = DATA_ROOT / "TurnaboutLLM" / "data" / file_name
    rows = _read_json(path)
    samples: list[Sample] = []
    for i, item in enumerate(rows):
        inp = item.get("input", {})
        samples.append(
            Sample(
                id=f"turnabout_{source.lower()}_{item.get('source', i)}",
                dataset="turnabout",
                split=source.upper(),
                context=inp.get("summarized_context") or inp.get("full_input"),
                question="Find the contradictory evidence-testimony pair.",
                options=None,
                answer=item.get("output"),
                evidence=inp.get("evidence"),
                reasoning=None,
                metadata={
                    "source_path": str(path),
                    "source": item.get("source"),
                    "testimonies": inp.get("testimonies"),
                    "prefix": inp.get("prefix"),
                    "suffix": inp.get("suffix"),
                },
            )
        )
        if limit is not None and len(samples) >= limit:
            break
    return samples


def load_dataset(name: str, split: str | None = None, limit: int | None = None) -> list[Sample]:
    if name == "musr":
        return load_musr(split or "murder_mystery", limit)
    if name == "detectbench":
        return load_detectbench(split or "test-hard", limit)
    if name == "detectiveqa":
        lang = "zh" if split and split.startswith("zh") else "en"
        anno = "ai" if split and "ai" in split.lower() else "human"
        return load_detectiveqa_annotations(lang=lang, anno=anno, limit=limit)
    if name == "turnabout":
        return load_turnabout(split or "AA", limit)
    raise ValueError(f"Unknown dataset: {name}")


def list_dataset_specs() -> list[dict[str, str]]:
    return [
        {"name": "musr", "split": "murder_mystery", "description": "MuSR murder mystery"},
        {"name": "musr", "split": "object_placements", "description": "MuSR object placements"},
        {"name": "detectbench", "split": "test-hard", "description": "DetectBench hard split"},
        {"name": "detectbench", "split": "test", "description": "DetectBench normal test"},
        {"name": "detectbench", "split": "test-distract", "description": "DetectBench distract split"},
        {"name": "detectiveqa", "split": "en_human", "description": "DetectiveQA English human annotations"},
        {"name": "turnabout", "split": "AA", "description": "TurnaboutLLM Ace Attorney"},
        {"name": "turnabout", "split": "DR", "description": "TurnaboutLLM Danganronpa"},
    ]
