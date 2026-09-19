"""Pydantic data models shared across agents."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["present", "partial", "absent"]
Priority = Literal["must_have", "preferred", "unspecified"]
Severity = Literal["dealbreaker", "nice_to_have"]


class SkillEntry(BaseModel):
    name: str
    category: str
    evidence: str = Field(description="Short quote or paraphrase from the resume backing this skill")


class ParsedResume(BaseModel):
    skills: list[SkillEntry]
    experience_summary: str


class JDRequirement(BaseModel):
    id: str
    text: str
    category: str
    stated_priority: Priority = "unspecified"


class ParsedJD(BaseModel):
    role_title: str
    requirements: list[JDRequirement]


class RequirementScore(BaseModel):
    requirement_id: str
    status: Status
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)


class SeverityClassification(BaseModel):
    requirement_id: str
    severity: Severity
    rationale: str


class GapSuggestion(BaseModel):
    requirement_id: str
    project_title: str
    project_description: str
    skills_targeted: list[str]
    resources: list[str] = Field(default_factory=list)


class ScoreBatch(BaseModel):
    """Wrapper so a single LLM call can return scores for every requirement at once."""

    scores: list[RequirementScore]


class PipelineResult(BaseModel):
    parsed_resume: ParsedResume
    parsed_jd: ParsedJD
    scores: list[RequirementScore]
    severities: list[SeverityClassification]
    suggestions: list[GapSuggestion]
