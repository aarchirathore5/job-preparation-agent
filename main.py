from __future__ import annotations

import argparse
import sys
from datetime import datetime

from dotenv import load_dotenv

from config import ConfigError, load_llm_settings
from llm.client import LLMClient
from orchestrator import Orchestrator
from reporting import save_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume-JD Gap & Portfolio-Prep Agent")
    parser.add_argument("--resume", required=True, help="Path to resume (.txt/.md/.pdf)")
    parser.add_argument("--jd", required=True, help="Path to job description (.txt/.md/.pdf)")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory (default: output/<timestamp>)",
    )
    args = parser.parse_args()

    load_dotenv()

    try:
        settings = load_llm_settings()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    out_dir = args.out_dir or f"output/{datetime.now():%Y%m%d-%H%M%S}"

    llm = LLMClient(settings)
    result = Orchestrator(llm).run(args.resume, args.jd)

    md_path, json_path = save_report(result, out_dir)

    dealbreakers = [s for s in result.severities if s.severity == "dealbreaker"]
    print(f"Role: {result.parsed_jd.role_title}")
    print(f"Requirements scored: {len(result.scores)}")
    print(f"Absent requirements: {len(result.severities)}")
    print(f"Dealbreaker gaps: {len(dealbreakers)}")
    print(f"Project suggestions: {len(result.suggestions)}")
    print(f"\nReport written to: {md_path}")
    print(f"Raw data written to: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
