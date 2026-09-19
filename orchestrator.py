from __future__ import annotations

from agents.gap_closer_agent import GapCloserAgent
from agents.parser_agent import ParserAgent
from agents.scoring_agent import ScoringAgent
from agents.severity_agent import SeverityAgent
from llm.client import LLMClient
from schemas import PipelineResult
from tools.doc_reader import read_text


class Orchestrator:
    """Wires the four agents into the parse -> score -> decide -> close pipeline."""

    def __init__(self, llm: LLMClient):
        self.parser = ParserAgent(llm)
        self.scorer = ScoringAgent(llm)
        self.severity = SeverityAgent(llm)
        self.gap_closer = GapCloserAgent(llm)

    def run(self, resume_path: str, jd_path: str) -> PipelineResult:
        resume_text = read_text(resume_path)
        jd_text = read_text(jd_path)

        parsed_resume = self.parser.parse_resume(resume_text)
        parsed_jd = self.parser.parse_jd(jd_text)

        scores = self.scorer.score(parsed_resume, parsed_jd)
        absent_scores = [s for s in scores if s.status == "absent"]

        classifications = self.severity.classify_absent(absent_scores, parsed_jd)
        dealbreakers = self.severity.escalate_dealbreakers(classifications)

        suggestions = self.gap_closer.suggest(dealbreakers, parsed_jd)

        return PipelineResult(
            parsed_resume=parsed_resume,
            parsed_jd=parsed_jd,
            scores=scores,
            severities=classifications,
            suggestions=suggestions,
        )
