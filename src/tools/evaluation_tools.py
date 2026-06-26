"""Simple deterministic evaluation checks for planning briefs."""

from __future__ import annotations


def evaluate_brief(brief_text: str) -> dict:
    """Evaluate whether a brief contains basic expected elements."""
    lower = brief_text.lower()
    checks = {
        "mentions_evidence_or_score": any(term in lower for term in ["score", "indicator", "deficit"]),
        "mentions_policy_or_planning": any(term in lower for term in ["policy", "planning", "intervention"]),
        "mentions_stakeholders_or_citizens": any(term in lower for term in ["citizen", "resident", "stakeholder"]),
        "mentions_limitations": "limitation" in lower or "synthetic data" in lower,
        "avoids_real_data_claim": "not as real planning evidence" in lower or "synthetic data" in lower,
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "score": sum(checks.values()) / len(checks),
    }
