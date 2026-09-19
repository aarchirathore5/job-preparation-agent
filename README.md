# Resume–JD Gap & Portfolio-Prep Agent

A small multi-agent CLI that takes a resume + job description and:

1. **ParserAgent** — parses both into structured skill/requirement lists.
2. **ScoringAgent** — scores each JD requirement against the resume: `present` / `partial` / `absent`.
3. **SeverityAgent** — a decision loop over `absent` items that classifies severity
   (`dealbreaker` vs `nice_to_have`) and escalates only dealbreakers.
4. **GapCloserAgent** — for each dealbreaker, does a best-effort web search and suggests a
   minimal project to close the gap.

Output is written as a Markdown report + JSON file.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` to pick a provider (see below), then run:

```bash
python main.py --resume sample_data/sample_resume.txt --jd sample_data/sample_jd.txt
```

Resume/JD inputs can be `.txt`, `.md`, or `.pdf`.

## Providers

Set `LLM_PROVIDER` to exactly one of:

- **`ollama`** — local models via [Ollama](https://ollama.com). Requires `ollama serve` running.
  - `OLLAMA_MODEL` (default `llama3.1`)
  - `OLLAMA_BASE_URL` (default `http://localhost:11434`)
- **`litellm`** — OpenAI credentials via the `litellm` SDK.
  - `OPENAI_API_KEY` (required)
  - `OPENAI_MODEL` (default `gpt-4o-mini`)

Both paths go through the same `litellm.completion()` call in `llm/client.py` — only the model
string and connection kwargs differ.

## Project layout

```
config.py            env var -> LLMSettings
schemas.py            pydantic models shared by all agents
llm/client.py          litellm wrapper with JSON-mode + validation retry
tools/web_search.py    best-effort DuckDuckGo search (no API key, fails silently)
tools/doc_reader.py    reads .txt/.md/.pdf input files
agents/                one file per agent
orchestrator.py        wires the pipeline together
reporting.py           renders the markdown/json report
main.py                CLI entrypoint
```

## Tests

```bash
pytest tests/
```

Tests use a `FakeLLMClient` stub, so no live model or network access is required.
