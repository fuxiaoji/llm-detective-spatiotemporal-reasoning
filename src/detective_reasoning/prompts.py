from __future__ import annotations

from .schemas import Sample


def format_options(options) -> str:
    if options is None:
        return ""
    if isinstance(options, dict):
        return "\n".join(f"{k}. {v}" for k, v in options.items())
    return "\n".join(f"{i}. {v}" for i, v in enumerate(options))


def answer_format_hint(sample: Sample) -> str:
    if sample.dataset == "detectiveqa":
        return "Return the final answer as one option letter, such as A, B, C, or D."
    if sample.dataset == "turnabout":
        return "Return the final answer as [evidence_index, testimony_index]."
    return "Return the final answer as one option index, such as 0, 1, 2, or 3."


def base_prompt(sample: Sample, instruction: str) -> str:
    context = sample.context or "(No full context is available for this sample.)"
    evidence = "" if sample.evidence is None else f"\nKnown evidence annotations:\n{sample.evidence}\n"
    return f"""You are solving a detective reasoning benchmark.

{instruction}

Context:
{context}

Question:
{sample.question}

Options:
{format_options(sample.options)}
{evidence}
{answer_format_hint(sample)}
"""


def direct_prompt(sample: Sample) -> str:
    return base_prompt(sample, "Answer directly. Use the evidence in the context, but be concise.")


def cot_prompt(sample: Sample) -> str:
    return base_prompt(
        sample,
        "Reason step by step. Compare the options carefully, then provide the final answer.",
    )


def reflection_prompt(sample: Sample) -> str:
    return base_prompt(
        sample,
        "First solve the problem step by step. Then briefly check whether your answer contradicts any evidence. End with the final answer.",
    )


def evidence_card_prompt(sample: Sample) -> str:
    return base_prompt(
        sample,
        "Build a compact evidence card before answering. For suspect-style questions, compare means, motive, opportunity, evidence for, and evidence against. For other questions, list key clues and how they support each option. End with the final answer.",
    )


def critic_checklist_prompt(sample: Sample, draft: str | None = None) -> str:
    draft_block = f"\nDraft answer to verify:\n{draft}\n" if draft else ""
    return base_prompt(
        sample,
        "Use a critic checklist: check missing key evidence, hallucinated evidence, time/location conflicts, and option consistency. Then provide the corrected final answer.",
    ) + draft_block


def build_prompt(method: str, sample: Sample, draft: str | None = None) -> str:
    if method == "direct":
        return direct_prompt(sample)
    if method == "cot":
        return cot_prompt(sample)
    if method == "reflection":
        return reflection_prompt(sample)
    if method == "evidence_card":
        return evidence_card_prompt(sample)
    if method == "critic_checklist":
        return critic_checklist_prompt(sample, draft=draft)
    raise ValueError(f"Unknown method: {method}")

