from __future__ import annotations

from pathlib import Path

from schemas import PipelineResult

_STATUS_EMOJI = {"present": "✅", "partial": "🟡", "absent": "❌"}


def render_markdown(result: PipelineResult) -> str:
    jd = result.parsed_jd
    req_by_id = {r.id: r for r in jd.requirements}
    severity_by_id = {s.requirement_id: s for s in result.severities}
    suggestion_by_id = {s.requirement_id: s for s in result.suggestions}

    lines = [f"# Gap Report: {jd.role_title}", ""]

    lines.append("## Requirement Coverage")
    lines.append("")
    lines.append("| Requirement | Priority | Status | Evidence |")
    lines.append("|---|---|---|---|")
    for score in result.scores:
        requirement = req_by_id.get(score.requirement_id)
        req_text = requirement.text if requirement else score.requirement_id
        priority = requirement.stated_priority if requirement else "unspecified"
        emoji = _STATUS_EMOJI.get(score.status, "")
        lines.append(f"| {req_text} | {priority} | {emoji} {score.status} | {score.evidence} |")
    lines.append("")

    lines.append("## Dealbreaker Gaps & Portfolio-Prep Plan")
    lines.append("")
    dealbreaker_ids = [
        s.requirement_id for s in result.severities if s.severity == "dealbreaker"
    ]
    if not dealbreaker_ids:
        lines.append("No dealbreaker gaps found. 🎉")
    for req_id in dealbreaker_ids:
        requirement = req_by_id.get(req_id)
        severity = severity_by_id.get(req_id)
        suggestion = suggestion_by_id.get(req_id)
        lines.append(f"### {requirement.text if requirement else req_id}")
        if severity:
            lines.append(f"_Why it matters:_ {severity.rationale}")
            lines.append("")
        if suggestion:
            lines.append(f"**Suggested project: {suggestion.project_title}**")
            lines.append("")
            lines.append(suggestion.project_description)
            lines.append("")
            lines.append(f"Skills targeted: {', '.join(suggestion.skills_targeted)}")
            if suggestion.resources:
                lines.append("")
                lines.append("Resources:")
                for url in suggestion.resources:
                    lines.append(f"- {url}")
        lines.append("")

    nice_to_have_ids = [
        s.requirement_id for s in result.severities if s.severity == "nice_to_have"
    ]
    if nice_to_have_ids:
        lines.append("## Other Gaps (Nice-to-have, not blocking)")
        lines.append("")
        for req_id in nice_to_have_ids:
            requirement = req_by_id.get(req_id)
            severity = severity_by_id.get(req_id)
            lines.append(f"- **{requirement.text if requirement else req_id}** — {severity.rationale}")
        lines.append("")

    return "\n".join(lines)


def save_report(result: PipelineResult, out_dir: str | Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "report.md"
    json_path = out_dir / "result.json"

    md_path.write_text(render_markdown(result), encoding="utf-8")
    json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    return md_path, json_path
