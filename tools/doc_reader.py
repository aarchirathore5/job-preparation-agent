"""Reads resume/JD input files: plain text/markdown directly, PDF via pypdf."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def read_text(path: str | Path) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    return path.read_text(encoding="utf-8")
