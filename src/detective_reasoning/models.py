from __future__ import annotations

import json
import os
import random
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .schemas import ModelResponse


@dataclass
class ModelConfig:
    provider: str = "mock"
    model: str = "mock"
    temperature: float = 0.0
    max_tokens: int = 800
    base_url: str | None = None
    thinking: str | None = None
    reasoning_effort: str | None = None
    api_key: str | None = None


class ModelClient:
    def generate(self, prompt: str) -> ModelResponse:
        raise NotImplementedError


class MockModelClient(ModelClient):
    def __init__(self, model: str = "mock"):
        self.model = model

    def generate(self, prompt: str) -> ModelResponse:
        # Deterministic enough for tests while still exercising parsing.
        if "A, B, C, or D" in prompt:
            text = "Reasoning omitted for mock mode. Final answer: A"
        elif "[evidence_index, testimony_index]" in prompt:
            text = "Reasoning omitted for mock mode. Final answer: [0, 0]"
        else:
            text = f"Reasoning omitted for mock mode. Final answer: {random.choice([0, 1])}"
        return ModelResponse(text=text, model=self.model, raw={"provider": "mock"})


class OpenAICompatibleClient(ModelClient):
    """Minimal OpenAI-compatible chat completions client using stdlib urllib."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.base_url = (config.base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for provider=openai")

    def generate(self, prompt: str) -> ModelResponse:
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if self.config.thinking:
            payload["thinking"] = {"type": self.config.thinking}
        if self.config.reasoning_effort:
            payload["reasoning_effort"] = self.config.reasoning_effort
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible API error {e.code}: {body}") from e
        message = raw["choices"][0]["message"]
        text = message.get("content") or ""
        usage = raw.get("usage", {})
        return ModelResponse(
            text=text,
            model=self.config.model,
            reasoning_content=message.get("reasoning_content"),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            raw=raw,
        )


def make_model_client(config: ModelConfig) -> ModelClient:
    if config.provider == "mock":
        return MockModelClient(config.model)
    if config.provider == "openai":
        return OpenAICompatibleClient(config)
    raise ValueError(f"Unknown provider: {config.provider}")
