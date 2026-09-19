from __future__ import annotations

from agents.base import BaseAgent
from schemas import ParsedJD, ParsedResume

_RESUME_SYSTEM = (
    "You are a resume parser. Extract every distinct skill (technical, tool, domain, or soft "
    "skill) evidenced in the resume, and a short experience summary. Categorize each skill "
    "(e.g. 'language', 'framework', 'cloud', 'domain', 'soft-skill'). Ground every skill in a "
    "short quote or paraphrase from the resume."
)

_JD_SYSTEM = (
    "You are a job description parser. Extract the role title and a flat list of distinct "
    "requirements. For each requirement, assign a stable short id (e.g. 'req-1'), the "
    "requirement text, a category (e.g. 'language', 'framework', 'experience', 'domain', "
    "'soft-skill'), and a stated_priority of 'must_have', 'preferred', or 'unspecified' based on "
    "how the JD itself phrases it (e.g. 'required'/'must' vs 'nice to have'/'bonus')."
)


class ParserAgent(BaseAgent):
    """Tool call: parses resume + JD free text into structured skill/requirement lists."""

    def parse_resume(self, resume_text: str) -> ParsedResume:
        return self.run_json(_RESUME_SYSTEM, resume_text, ParsedResume)

    def parse_jd(self, jd_text: str) -> ParsedJD:
        return self.run_json(_JD_SYSTEM, jd_text, ParsedJD)
