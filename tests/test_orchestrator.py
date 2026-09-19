from orchestrator import Orchestrator
from schemas import (
    GapSuggestion,
    JDRequirement,
    ParsedJD,
    ParsedResume,
    RequirementScore,
    ScoreBatch,
    SeverityClassification,
    SkillEntry,
)


class FakeLLMClient:
    """Stubs LLMClient.complete_json, returning canned responses keyed by schema name.

    Each key maps to either a single instance (returned every time) or a list
    (returned in order, one per call, for schemas invoked multiple times).
    """

    def __init__(self, responses: dict):
        self._responses = {
            name: value if isinstance(value, list) else [value]
            for name, value in responses.items()
        }
        self._index = {name: 0 for name in self._responses}

    def complete_json(self, system, user, schema):
        name = schema.__name__
        items = self._responses[name]
        idx = self._index[name]
        item = items[idx % len(items)]
        self._index[name] += 1
        return item


def _build_fake_llm() -> FakeLLMClient:
    parsed_resume = ParsedResume(
        skills=[SkillEntry(name="Python", category="language", evidence="Used Python daily")],
        experience_summary="4 years backend engineering",
    )
    parsed_jd = ParsedJD(
        role_title="Backend Engineer",
        requirements=[
            JDRequirement(id="req-1", text="Python", category="language", stated_priority="must_have"),
            JDRequirement(id="req-2", text="Kubernetes", category="tool", stated_priority="must_have"),
            JDRequirement(id="req-3", text="Communication", category="soft-skill", stated_priority="preferred"),
        ],
    )
    score_batch = ScoreBatch(
        scores=[
            RequirementScore(requirement_id="req-1", status="present", evidence="Uses Python", confidence=0.9),
            RequirementScore(requirement_id="req-2", status="absent", evidence="no evidence found", confidence=0.9),
            RequirementScore(requirement_id="req-3", status="absent", evidence="no evidence found", confidence=0.6),
        ]
    )
    # classify_absent() loops over absent scores in JD order: req-2 then req-3.
    severities = [
        SeverityClassification(requirement_id="req-2", severity="dealbreaker", rationale="Core infra skill for this role"),
        SeverityClassification(requirement_id="req-3", severity="nice_to_have", rationale="Soft skill, hard to fail on alone"),
    ]
    suggestion = GapSuggestion(
        requirement_id="req-2",
        project_title="Deploy a small service on Kubernetes",
        project_description="Containerize a toy API and deploy it to a local k8s cluster (kind/minikube).",
        skills_targeted=["Kubernetes", "Docker"],
        resources=[],
    )

    return FakeLLMClient(
        {
            "ParsedResume": parsed_resume,
            "ParsedJD": parsed_jd,
            "ScoreBatch": score_batch,
            "SeverityClassification": severities,
            "GapSuggestion": suggestion,
        }
    )


def test_orchestrator_escalates_only_dealbreakers(tmp_path, monkeypatch):
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text("dummy resume text")
    jd_path = tmp_path / "jd.txt"
    jd_path.write_text("dummy jd text")

    # Web search is best-effort and network-dependent; stub it out for the test.
    monkeypatch.setattr("tools.web_search.search", lambda *args, **kwargs: [])

    orchestrator = Orchestrator(_build_fake_llm())
    result = orchestrator.run(str(resume_path), str(jd_path))

    assert len(result.scores) == 3
    assert len(result.severities) == 2  # both absent requirements get classified

    dealbreakers = [s for s in result.severities if s.severity == "dealbreaker"]
    assert [s.requirement_id for s in dealbreakers] == ["req-2"]

    # Only the dealbreaker should have reached the gap closer.
    assert len(result.suggestions) == 1
    assert result.suggestions[0].requirement_id == "req-2"
