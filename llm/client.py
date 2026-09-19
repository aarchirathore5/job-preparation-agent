"""Thin wrapper around litellm giving us one call path for Ollama and OpenAI."""
from __future__ import annotations

import json
import re
from typing import TypeVar

import litellm
from pydantic import BaseModel, ValidationError

from config import LLMSettings

T = TypeVar("T", bound=BaseModel)

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _strip_code_fences(text: str) -> str:
    return _FENCE_RE.sub("", text.strip()).strip()


class LLMClient:
    """Provider-agnostic chat completion client (Ollama local / OpenAI via litellm)."""

    def __init__(self, settings: LLMSettings):
        self.settings = settings

    def _completion_kwargs(self) -> dict:
        kwargs: dict = {
            "model": self.settings.model,
            "temperature": self.settings.temperature,
        }
        if self.settings.api_base:
            kwargs["api_base"] = self.settings.api_base
        if self.settings.api_key:
            kwargs["api_key"] = self.settings.api_key
        return kwargs

    def complete_text(self, system: str, user: str) -> str:
        response = litellm.completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **self._completion_kwargs(),
        )
        return response["choices"][0]["message"]["content"]

    def complete_json(self, system: str, user: str, schema: type[T], retries: int = 2) -> T:
        """Call the model and parse+validate its reply as `schema`, retrying on bad JSON."""
        schema_hint = (
            "\n\nRespond with ONLY a single valid JSON object or array (no prose, no markdown "
            "code fences) that matches this Pydantic schema:\n"
            f"{schema.model_json_schema()}"
        )
        messages = [
            {"role": "system", "content": system + schema_hint},
            {"role": "user", "content": user},
        ]

        last_error: Exception | None = None
        for attempt in range(retries + 1):
            response = litellm.completion(messages=messages, **self._completion_kwargs())
            raw = response["choices"][0]["message"]["content"]
            cleaned = _strip_code_fences(raw)
            try:
                data = json.loads(cleaned)
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "That was not valid JSON matching the schema. Error: "
                            f"{exc}\nReturn ONLY the corrected JSON, nothing else."
                        ),
                    }
                )

        raise ValueError(f"LLM failed to produce valid JSON after {retries + 1} attempts: {last_error}")
