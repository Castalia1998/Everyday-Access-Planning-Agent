"""Trace writing utilities."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def write_trace(trace_path: str, step_name: str, inputs: dict[str, Any], outputs: dict[str, Any]) -> None:
    """Append a trace event to a JSON file."""
    path = Path(trace_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        events = json.loads(path.read_text(encoding="utf-8"))
    else:
        events = []

    events.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_name": step_name,
            "inputs": inputs,
            "outputs": outputs,
        }
    )
    path.write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")
