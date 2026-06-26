"""Simple keyword-based policy text retrieval tools."""

from __future__ import annotations

from pathlib import Path
import re


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z-]+", text.lower()))


def retrieve_policy_snippets(query: str, docs_dir: str, top_k: int = 3) -> list[dict]:
    """Retrieve top policy-style text snippets using simple keyword overlap.

    This is intentionally deterministic and minimal. It should later be replaced or augmented
    by embedding-based retrieval or RAG.
    """
    query_tokens = _tokenize(query)
    results = []
    for path in Path(docs_dir).glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        doc_tokens = _tokenize(text)
        score = len(query_tokens & doc_tokens)
        if score > 0:
            snippet = text.strip().replace("\n", " ")[:500]
            results.append({"document": path.name, "score": score, "snippet": snippet})
    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
