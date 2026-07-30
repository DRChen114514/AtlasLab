# AtlasLab

AtlasLab is a multi-agent system for Chinese math modeling competitions, featuring automated problem analysis, solution generation, and paper authoring via a LangGraph-powered LLM pipeline.

---

## Features

- **Multi-Agent Pipeline** — LangGraph-based agents (supervisor, analysts, writers, coders, reviewers) collaborate end-to-end.
- **Local Web UI** — A Node.js workbench (`http://127.0.0.1:5173`) with guided onboarding, model provider configuration, and run monitoring.
- **PDF to Markdown** — Built-in extraction (PyMuPDF / pypdf) for problem statements and reference materials.
- **Checkpoint Recovery** — Failed runs can be resumed from the last checkpoint.
- **RAG Support** — Vector search over a corpus of mathematical modeling textbooks and algorithm references.

---

## Quick Start

### Prerequisites

- **Python** 3.11–3.13 (`uv` recommended)
- **Node.js** 18+
- **Ollama** or an OpenAI-compatible API endpoint

### Setup

```bash
git clone <repo-url> && cd AtlasLab
npm install
python3 -m venv .venv && source .venv/bin/activate
uv sync  # or: pip install -e .
```

Copy `.env.example` to `.env` and fill in your API keys and model preferences.

### Launch

```bash
npm start
```

Open `http://127.0.0.1:5173` in your browser. The first-run wizard will guide you through model configuration.

### CLI Mode

```bash
math-agent solve <problem-file>
```

---

## Project Structure

```
AtlasLab
├── AtlasLab.py              # Desktop backend launcher (port 18080)
├── frontend/                # Web UI (Node.js server)
├── src/math_agent/          # Core multi-agent pipeline
├── scripts/                 # E2E test and utility scripts
├── corpus/models/           # Math modeling algorithm references
├── problems/                # Competition problem definitions (JSON)
├── docs/                    # Design docs and plans
└── tests/                   # Test suite
```

---

## Tech Stack

- **Orchestration**: LangGraph + SQLite checkpointing
- **LLM Gateway**: LiteLLM (multi-provider)
- **Backend**: Python 3.11+ (PyMuPDF, pydantic, Jinja2, matplotlib)
- **Frontend**: Node.js, vanilla HTML/CSS/JS
- **Search**: sqlite-vec for RAG

---

## License

MIT
