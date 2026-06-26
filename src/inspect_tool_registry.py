"""Inspect the lightweight deterministic tool registry."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tool_registry.executor import list_tools


if __name__ == "__main__":
    for spec in list_tools():
        print(f"{spec.name} | {spec.category} | read_only={spec.read_only} | risk={spec.risk_level}")
        print(f"  {spec.description}")