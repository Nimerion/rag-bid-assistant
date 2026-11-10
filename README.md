# rag-bid-assistant

An app that answers questions using sample documents in rag_docs/. The documents are AI-generated and used only for testing.
It finds the relevant passages in the documents and passes them to an AI model
so the answer comes from those documents.

## Project layout

| Path | What it is |
|------|------------|
| `app/` | The app's own code (to be written) |
| `rag_docs/` | The source documents (PDFs) the app searches |
| `build_rag_docs.py` | Script that generates the sample PDFs |
| `requirements.txt` | List of tools the project needs |
| `.venv/` | Private toolbox for this project (not shared via Git) |
| `.env` | Secret settings such as API keys (never shared via Git) |

## Setup

```bash
.venv/bin/pip install -r requirements.txt
```
