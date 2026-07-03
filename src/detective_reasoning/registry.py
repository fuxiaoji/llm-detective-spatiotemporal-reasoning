from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import prompts
from .datasets import (
    load_dataset,
    load_detectbench,
    load_detectiveqa_annotations,
    load_musr,
    load_turnabout,
)
from .schemas import Sample


DatasetLoader = Callable[[str | None, int | None], list[Sample]]
PromptBuilder = Callable[[Sample], str]
SkillApplier = Callable[[Sample, str, dict], str]


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    split: str
    description: str
    loader: DatasetLoader


@dataclass(frozen=True)
class MethodSpec:
    name: str
    description: str
    builder: PromptBuilder


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    apply: SkillApplier


@dataclass(frozen=True)
class EvaluatorSpec:
    name: str
    description: str


def _musr_loader(split: str | None, limit: int | None) -> list[Sample]:
    return load_musr(split or "murder_mystery", limit)


def _detectbench_loader(split: str | None, limit: int | None) -> list[Sample]:
    return load_detectbench(split or "test-hard", limit)


def _detectiveqa_loader(split: str | None, limit: int | None) -> list[Sample]:
    lang = "zh" if split and split.startswith("zh") else "en"
    anno = "ai" if split and "ai" in split.lower() else "human"
    return load_detectiveqa_annotations(lang=lang, anno=anno, limit=limit)


def _turnabout_loader(split: str | None, limit: int | None) -> list[Sample]:
    return load_turnabout(split or "AA", limit)


DATASETS: dict[str, DatasetSpec] = {
    "musr:murder_mystery": DatasetSpec(
        name="musr",
        split="murder_mystery",
        description="MuSR murder mystery",
        loader=_musr_loader,
    ),
    "musr:object_placements": DatasetSpec(
        name="musr",
        split="object_placements",
        description="MuSR object placements",
        loader=_musr_loader,
    ),
    "musr:team_allocation": DatasetSpec(
        name="musr",
        split="team_allocation",
        description="MuSR team allocation",
        loader=_musr_loader,
    ),
    "detectbench:test-hard": DatasetSpec(
        name="detectbench",
        split="test-hard",
        description="DetectBench hard split",
        loader=_detectbench_loader,
    ),
    "detectbench:test": DatasetSpec(
        name="detectbench",
        split="test",
        description="DetectBench normal test",
        loader=_detectbench_loader,
    ),
    "detectbench:test-distract": DatasetSpec(
        name="detectbench",
        split="test-distract",
        description="DetectBench distract split",
        loader=_detectbench_loader,
    ),
    "detectiveqa:en_human": DatasetSpec(
        name="detectiveqa",
        split="en_human",
        description="DetectiveQA English human annotations",
        loader=_detectiveqa_loader,
    ),
    "detectiveqa:en_ai": DatasetSpec(
        name="detectiveqa",
        split="en_ai",
        description="DetectiveQA English AI-assisted annotations",
        loader=_detectiveqa_loader,
    ),
    "detectiveqa:zh_human": DatasetSpec(
        name="detectiveqa",
        split="zh_human",
        description="DetectiveQA Chinese human annotations",
        loader=_detectiveqa_loader,
    ),
    "detectiveqa:zh_ai": DatasetSpec(
        name="detectiveqa",
        split="zh_ai",
        description="DetectiveQA Chinese AI-assisted annotations",
        loader=_detectiveqa_loader,
    ),
    "turnabout:AA": DatasetSpec(
        name="turnabout",
        split="AA",
        description="TurnaboutLLM Ace Attorney",
        loader=_turnabout_loader,
    ),
    "turnabout:DR": DatasetSpec(
        name="turnabout",
        split="DR",
        description="TurnaboutLLM Danganronpa",
        loader=_turnabout_loader,
    ),
}


METHODS: dict[str, MethodSpec] = {
    "direct": MethodSpec("direct", "Answer directly with a concise rationale.", prompts.direct_prompt),
    "cot": MethodSpec("cot", "Reason step by step before answering.", prompts.cot_prompt),
    "reflection": MethodSpec("reflection", "Answer, then check for contradictions.", prompts.reflection_prompt),
    "evidence_card": MethodSpec(
        "evidence_card",
        "Build a compact evidence card before answering.",
        prompts.evidence_card_prompt,
    ),
    "critic_checklist": MethodSpec(
        "critic_checklist",
        "Draft with CoT, then verify with a critic checklist.",
        prompts.critic_checklist_prompt,
    ),
}


def _dummy_skill(sample: Sample, prompt: str, intermediate: dict) -> str:
    intermediate.setdefault("skills", []).append(
        {
            "name": "dummy_skill",
            "effect": "Recorded a no-op skill call for registry and GUI testing.",
            "sample_id": sample.id,
        }
    )
    return prompt + "\n\n[Registered skill: dummy_skill ran as a no-op test component.]\n"


def _external_evidence_bank(sample: Sample, prompt: str, intermediate: dict) -> str:
    evidence = {
        "known_evidence": sample.evidence,
        "known_reasoning": sample.reasoning,
        "metadata": {
            "dataset": sample.dataset,
            "split": sample.split,
            "sample_id": sample.id,
        },
    }
    intermediate.setdefault("skills", []).append(
        {
            "name": "external_evidence_bank",
            "effect": "Attached available structured annotations as an external evidence bank.",
            "has_evidence": sample.evidence is not None,
            "has_reasoning": sample.reasoning is not None,
        }
    )
    return (
        prompt
        + "\n\nExternal structured evidence bank:\n"
        + str(evidence)
        + "\nUse this bank only when it is supported by the problem statement.\n"
    )


def _structured_memory_stub(sample: Sample, prompt: str, intermediate: dict) -> str:
    intermediate.setdefault("skills", []).append(
        {
            "name": "structured_memory_stub",
            "effect": "Requested a temporary timeline/location/entity memory before answering.",
        }
    )
    return (
        prompt
        + "\n\nBefore the final answer, create a compact temporary memory with: "
        + "timeline, locations, entities, evidence for each option, and contradictions. "
        + "Then answer in the required final format.\n"
    )


SKILLS: dict[str, SkillSpec] = {
    "dummy_skill": SkillSpec(
        "dummy_skill",
        "No-op test skill used to verify plugin-style registration.",
        _dummy_skill,
    ),
    "external_evidence_bank": SkillSpec(
        "external_evidence_bank",
        "Attach available structured evidence/reasoning annotations to the prompt.",
        _external_evidence_bank,
    ),
    "structured_memory_stub": SkillSpec(
        "structured_memory_stub",
        "Ask the model to build a temporary structured memory before answering.",
        _structured_memory_stub,
    ),
}


EVALUATORS: dict[str, EvaluatorSpec] = {
    "exact_match": EvaluatorSpec(
        "exact_match",
        "Dataset-aware exact match over option index, option letter, or evidence-testimony pair.",
    )
}


def dataset_key(name: str, split: str | None) -> str:
    return f"{name}:{split or ''}"


def list_dataset_specs() -> list[dict[str, str]]:
    return [
        {"name": spec.name, "split": spec.split, "description": spec.description}
        for spec in DATASETS.values()
    ]


def list_method_specs() -> list[dict[str, str]]:
    return [{"name": spec.name, "description": spec.description} for spec in METHODS.values()]


def list_skill_specs() -> list[dict[str, str]]:
    return [{"name": spec.name, "description": spec.description} for spec in SKILLS.values()]


def list_evaluator_specs() -> list[dict[str, str]]:
    return [{"name": spec.name, "description": spec.description} for spec in EVALUATORS.values()]


def load_registered_dataset(name: str, split: str | None = None, limit: int | None = None) -> list[Sample]:
    key = dataset_key(name, split)
    spec = DATASETS.get(key)
    if spec is not None:
        return spec.loader(spec.split, limit)
    return load_dataset(name, split, limit)


def build_registered_prompt(
    method: str,
    sample: Sample,
    draft: str | None = None,
    skills: list[str] | None = None,
    intermediate: dict | None = None,
) -> str:
    if method == "critic_checklist":
        prompt = prompts.critic_checklist_prompt(sample, draft=draft)
    else:
        spec = METHODS.get(method)
        if spec is None:
            raise ValueError(f"Unknown method: {method}")
        prompt = spec.builder(sample)

    trace = intermediate if intermediate is not None else {}
    for skill_name in skills or []:
        skill = SKILLS.get(skill_name)
        if skill is None:
            raise ValueError(f"Unknown skill: {skill_name}")
        prompt = skill.apply(sample, prompt, trace)
    return prompt
