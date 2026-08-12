"""Deterministic, side-effect-free attention selection for Operator Stack."""

from __future__ import annotations

from typing import Any

_SELECTION_SCHEMA = "operator.attention_selection.v1"
_POLICY_VERSION = "operator.attention_policy.v1"
_SOURCE_SCHEMA = "operator.fleet_snapshot.v1"
_SEVERITY_ORDER = {"critical": 0, "attention": 1, "warning": 2, "info": 3}
_CODE_ORDER = {
    "target_readiness_attention": 0,
    "plugin_configuration_incomplete": 1,
    "fleet_version_skew": 2,
}
_READINESS_ORDER = {"unreachable": 0, "degraded": 1, "not_ready": 2}


def _validate_findings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("snapshot.findings must be a list")
    required_strings = ("code", "severity", "scope", "observed_at", "source", "safe_next_inspection")
    for index, finding in enumerate(value):
        if not isinstance(finding, dict):
            raise ValueError(f"snapshot.findings[{index}] must be an object")
        for field in required_strings:
            if not isinstance(finding.get(field), str) or not finding[field].strip():
                raise ValueError(f"snapshot.findings[{index}].{field} must be a non-empty string")
        if not isinstance(finding.get("evidence"), dict):
            raise ValueError(f"snapshot.findings[{index}].evidence must be an object")
    return value


def _priority(finding: dict[str, Any]) -> tuple[Any, ...]:
    evidence = finding.get("evidence")
    evidence_status = evidence.get("status") if isinstance(evidence, dict) else ""
    return (
        _SEVERITY_ORDER.get(str(finding.get("severity") or "").lower(), 4),
        _CODE_ORDER.get(str(finding.get("code") or ""), 3),
        _READINESS_ORDER.get(str(evidence_status or ""), 3),
        str(finding.get("target") or ""),
        str(finding.get("code") or ""),
        str(finding.get("source") or ""),
        str(finding.get("observed_at") or ""),
    )


def select_attention(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return one selected finding or an explicit no-attention result."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    if snapshot.get("schema_version") != _SOURCE_SCHEMA:
        raise ValueError(f"snapshot.schema_version must be {_SOURCE_SCHEMA}")
    if not isinstance(snapshot.get("observed_at"), str) or not snapshot["observed_at"].strip():
        raise ValueError("snapshot.observed_at must be a non-empty string")
    findings = _validate_findings(snapshot.get("findings"))
    selected = min(findings, key=_priority) if findings else None
    return {
        "schema_version": _SELECTION_SCHEMA,
        "policy_version": _POLICY_VERSION,
        "status": "attention_required" if selected is not None else "no_attention_required",
        "source_schema_version": _SOURCE_SCHEMA,
        "source_observed_at": snapshot["observed_at"],
        "selected_finding": selected,
    }
