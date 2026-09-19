"""Environment-driven LLM provider configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    model: str
    temperature: float
    api_base: str | None = None
    api_key: str | None = None


def load_llm_settings() -> LLMSettings:
    provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
    temperature = float(os.environ.get("LLM_TEMPERATURE", "0.2"))

    if provider == "ollama":
        model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return LLMSettings(
            provider=provider,
            model=f"ollama/{model}",
            temperature=temperature,
            api_base=base_url,
        )

    if provider == "litellm":
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ConfigError("OPENAI_API_KEY must be set when LLM_PROVIDER=litellm")
        return LLMSettings(
            provider=provider,
            model=model,
            temperature=temperature,
            api_key=api_key,
        )

    raise ConfigError(
        f"Unsupported or missing LLM_PROVIDER={provider!r}. Set it to 'ollama' or 'litellm'."
    )
