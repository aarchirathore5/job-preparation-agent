from __future__ import annotations

import json

from agents.base import BaseAgent
from schemas import GapSuggestion, ParsedJD, SeverityClassification
from tools import web_search

_SYSTEM = (
    "You help a job candidate close a skill gap before applying. Given a missing requirement "
    "(a dealbreaker) and optional web search results, propose ONE minimal, concrete, buildable "
    "project that would let the candidate credibly claim this skill in an interview or on their "
    "resume. Keep it scoped to something doable in a few days to a couple weeks, not a full "
    "course. List the specific skills_targeted and, if any search results were useful, include "
    "their urls in resources (otherwise leave resources empty)."
)


class GapCloserAgent(BaseAgent):
    """Tool call: for each dealbreaker, searches for/suggests a minimal project to close the gap."""

    def suggest(
        self, dealbreakers: list[SeverityClassification], jd: ParsedJD
    ) -> list[GapSuggestion]:
        req_by_id = {r.id: r for r in jd.requirements}
        suggestions: list[GapSuggestion] = []

        for item in dealbreakers:
            requirement = req_by_id.get(item.requirement_id)
            if requirement is None:
                continue

            search_results = web_search.search(
                f"beginner project to learn {requirement.text} for {jd.role_title}"
            )

            user = json.dumps(
                {
                    "role_title": jd.role_title,
                    "requirement": requirement.model_dump(),
                    "severity_rationale": item.rationale,
                    "web_search_results": search_results,
                },
                indent=2,
            )
            suggestion = self.run_json(_SYSTEM, user, GapSuggestion)
            suggestions.append(suggestion)

        return suggestions
