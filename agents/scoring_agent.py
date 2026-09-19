from __future__ import annotations

import json

from agents.base import BaseAgent
from schemas import ParsedJD, ParsedResume, RequirementScore, ScoreBatch

_SYSTEM = (
    "You are a strict technical recruiter evaluating a candidate's resume against every "
    "requirement of a job description. For EACH requirement, decide a status:\n"
    "- 'present': the resume clearly demonstrates this requirement.\n"
    "- 'partial': related or adjacent experience exists but doesn't fully cover it.\n"
    "- 'absent': no meaningful evidence in the resume.\n"
    "Give a one-sentence evidence justification (quote the resume if present/partial, or say "
    "'no evidence found' if absent) and a confidence score between 0 and 1. Return exactly one "
    "score per requirement_id given, matching the requirement_id values exactly."
)


class ScoringAgent(BaseAgent):
    """Tool call / eval step: scores each JD requirement against the resume."""

    def score(self, resume: ParsedResume, jd: ParsedJD) -> list[RequirementScore]:
        if not jd.requirements:
            return []

        user = json.dumps(
            {
                "resume_skills": [s.model_dump() for s in resume.skills],
                "resume_experience_summary": resume.experience_summary,
                "jd_requirements": [r.model_dump() for r in jd.requirements],
            },
            indent=2,
        )
        batch = self.run_json(_SYSTEM, user, ScoreBatch)

        by_id = {s.requirement_id: s for s in batch.scores}
        return [by_id[r.id] for r in jd.requirements if r.id in by_id]
