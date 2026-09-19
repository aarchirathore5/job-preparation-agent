from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from llm.client import LLMClient

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run_json(self, system: str, user: str, schema: type[T]) -> T:
        return self.llm.complete_json(system, user, schema)
