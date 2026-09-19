"""Best-effort, no-API-key web search used by the gap-closer agent.

Scrapes the DuckDuckGo HTML endpoint. This is intentionally "best effort": any
failure (no network, layout change, timeout) is swallowed and an empty list is
returned so the pipeline can keep going with LLM-only suggestions.
"""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

_SEARCH_URL = "https://html.duckduckgo.com/html/"
_HEADERS = {"User-Agent": "Mozilla/5.0 (job-preparation-agent)"}


def search(query: str, max_results: int = 3, timeout: float = 5.0) -> list[dict]:
    try:
        response = requests.post(
            _SEARCH_URL, data={"q": query}, headers=_HEADERS, timeout=timeout
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result")[:max_results]:
            title_el = result.select_one(".result__a")
            snippet_el = result.select_one(".result__snippet")
            if not title_el:
                continue
            results.append(
                {
                    "title": title_el.get_text(strip=True),
                    "url": title_el.get("href", ""),
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                }
            )
        return results
    except Exception:
        return []
