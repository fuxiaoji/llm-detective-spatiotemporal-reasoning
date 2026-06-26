from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Sample:
    id: str
    dataset: str
    split: str
    context: str | None
    question: str
    options: list[str] | dict[str, str] | None
    answer: int | str | list[Any]
    evidence: Any = None
    reasoning: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ModelResponse:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Prediction:
    sample_id: str
    dataset: str
    split: str
    method: str
    model: str
    prompt: str
    raw_output: str
    prediction: Any
    gold: Any
    correct: bool
    parse_error: str | None = None
    intermediate: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

