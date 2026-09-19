import pytest
from pydantic import ValidationError

from schemas import JDRequirement, RequirementScore, SeverityClassification


def test_requirement_score_confidence_bounds():
    with pytest.raises(ValidationError):
        RequirementScore(requirement_id="req-1", status="absent", evidence="none", confidence=1.5)


def test_requirement_score_valid():
    score = RequirementScore(requirement_id="req-1", status="present", evidence="did X", confidence=0.9)
    assert score.status == "present"


def test_severity_classification_rejects_unknown_value():
    with pytest.raises(ValidationError):
        SeverityClassification(requirement_id="req-1", severity="maybe", rationale="unsure")


def test_jd_requirement_defaults_unspecified_priority():
    requirement = JDRequirement(id="req-1", text="Python", category="language")
    assert requirement.stated_priority == "unspecified"
