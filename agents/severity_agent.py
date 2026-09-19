from __future__ import annotations

import json

from agents.base import BaseAgent
from schemas import ParsedJD, RequirementScore, SeverityClassification

_SYSTEM = (
    "You are a hiring manager deciding how much a single missing requirement actually matters "
    "for this role. Classify it as 'dealbreaker' (the candidate would likely be screened out "
    "without it) or 'nice_to_have' (it would strengthen the application but isn't a blocker). "
    "Use the requirement's stated_priority as a signal, but judge holistically: a requirement "
    "phrased as 'required' can still be a nice_to_have in practice (e.g. an easily learned tool), "
    "and something phrased as 'preferred' can still be a dealbreaker for a senior/specialized "
    "role. Give a one-sentence rationale."
)


class SeverityAgent(BaseAgent):
    """Decision loop: for each absent requirement, classify severity; only dealbreakers escalate."""

    def classify_absent(
        self, absent_scores: list[RequirementScore], jd: ParsedJD
    ) -> list[SeverityClassification]:
        req_by_id = {r.id: r for r in jd.requirements}
        classifications: list[SeverityClassification] = []

        for score in absent_scores:
            requirement = req_by_id.get(score.requirement_id)
            if requirement is None:
                continue

            user = json.dumps(
                {
                    "role_title": jd.role_title,
                    "requirement": requirement.model_dump(),
                },
                indent=2,
            )
            classification = self.run_json(_SYSTEM, user, SeverityClassification)
            classifications.append(classification)

        return classifications

    @staticmethod
    def escalate_dealbreakers(
        classifications: list[SeverityClassification],
    ) -> list[SeverityClassification]:
        """Only dealbreaker items are escalated to the gap-closer agent."""
        return [c for c in classifications if c.severity == "dealbreaker"]
