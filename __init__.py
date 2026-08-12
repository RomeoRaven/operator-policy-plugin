"""protoAgent Operator Policy plugin."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

if __package__:
    from .policy import select_attention
else:  # Standalone pytest imports the root entry as top-level ``__init__``.
    from policy import select_attention


@tool
def operator_select_attention(snapshot: dict[str, Any]) -> str:
    """Select the one Operator finding needing attention first, or return all clear.

    The input must be an existing `operator.fleet_snapshot.v1` result. This tool
    performs no collection, network access, writes, notifications, or remediation.
    """
    try:
        result = select_attention(snapshot)
    except (TypeError, ValueError) as exc:
        result = {
            "schema_version": "operator.attention_selection.v1",
            "policy_version": "operator.attention_policy.v1",
            "status": "invalid_snapshot",
            "error": str(exc),
            "selected_finding": None,
        }
    return json.dumps(result, indent=2, sort_keys=True)


def register(registry) -> None:
    """Register the single pure attention-selection tool."""
    registry.register_tool(operator_select_attention)
