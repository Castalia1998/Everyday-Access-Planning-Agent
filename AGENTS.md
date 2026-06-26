# AGENTS.md

## Project Goal

This project is a minimal **Everyday Access Planning Agent** demo for stakeholder-facing urban intelligence. It focuses on MRT station-area everyday environments, combining structured station-area indicators, unstructured policy-style text, and synthetic citizen feedback to generate evidence-grounded planning briefs.

## Development Principles

1. Make the smallest working change needed for the current task.
2. Do not add speculative features.
3. Keep code readable, modular, and testable.
4. Prefer deterministic, auditable tools before adding LLM-based reasoning.
5. Every agent step should be traceable.
6. Every recommendation should distinguish observed data, analytical inference, policy recommendation, and limitations.

## Data Rules

1. All included data are synthetic demo data.
2. Singapore-style MRT station area names are used for readability, but the values are not real measurements.
3. Do not claim that synthetic data represents real Singapore conditions.
4. Do not fabricate citations, laws, policy commitments, or empirical facts.

## Tool Design Rules

Each tool should have:
- a clear function name
- typed inputs where possible
- predictable outputs
- basic error handling
- a short docstring explaining when the tool should be used

## Evaluation Rules

Generated planning briefs should be evaluated for:
1. evidence grounding
2. spatial reasoning
3. stakeholder relevance
4. uncertainty and limitations
5. absence of unsupported claims

## Testing Rules

Add or update tests whenever a tool is created or changed. Run tests before considering a task complete.
