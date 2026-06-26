"""Schemas for the lightweight deterministic tool registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    """Metadata describing one deterministic planning tool."""

    name: str
    description: str
    category: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    read_only: bool
    risk_level: str