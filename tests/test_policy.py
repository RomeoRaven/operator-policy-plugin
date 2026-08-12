from policy import select_attention


def _snapshot(*findings):
    return {
        "schema_version": "operator.fleet_snapshot.v1",
        "observed_at": "2026-08-12T02:30:00Z",
        "status": "ready" if not findings else "attention_required",
        "findings": list(findings),
    }


def test_returns_explicit_all_clear_when_snapshot_has_no_findings():
    assert select_attention(_snapshot()) == {
        "schema_version": "operator.attention_selection.v1",
        "policy_version": "operator.attention_policy.v1",
        "status": "no_attention_required",
        "source_schema_version": "operator.fleet_snapshot.v1",
        "source_observed_at": "2026-08-12T02:30:00Z",
        "selected_finding": None,
    }


def test_selects_loss_of_target_visibility_before_other_attention():
    version_skew = {
        "code": "fleet_version_skew",
        "severity": "attention",
        "scope": "fleet",
        "observed_at": "2026-08-12T02:30:00Z",
        "source": "GET /api/runtime/status",
        "classification": "signal",
        "evidence": {"versions": []},
        "safe_next_inspection": "Confirm intended versions.",
    }
    unreachable = {
        "code": "target_readiness_attention",
        "severity": "attention",
        "scope": "target",
        "target": "s1",
        "observed_at": "2026-08-12T02:30:00Z",
        "source": "GET /healthz and GET /api/runtime/status",
        "classification": "diagnostic",
        "evidence": {"status": "unreachable"},
        "safe_next_inspection": "Inspect reachability.",
    }

    result = select_attention(_snapshot(version_skew, unreachable))

    assert result["status"] == "attention_required"
    assert result["selected_finding"] == unreachable


def test_rejects_wrong_schema_instead_of_reporting_all_clear():
    malformed = _snapshot()
    malformed["schema_version"] = "operator.snapshot.v1"

    try:
        select_attention(malformed)
    except ValueError as exc:
        assert str(exc) == "snapshot.schema_version must be operator.fleet_snapshot.v1"
    else:
        raise AssertionError("wrong-schema snapshot was accepted")


def test_rejects_missing_snapshot_status_instead_of_reporting_all_clear():
    malformed = _snapshot()
    del malformed["status"]

    try:
        select_attention(malformed)
    except ValueError as exc:
        assert str(exc) == "snapshot.status must be ready or attention_required"
    else:
        raise AssertionError("missing-status snapshot was accepted")


def test_selection_is_input_order_independent_and_preserves_evidence():
    later_target = {
        "code": "target_readiness_attention",
        "severity": "attention",
        "scope": "target",
        "target": "zeta",
        "observed_at": "2026-08-12T02:30:00Z",
        "source": "GET /healthz and GET /api/runtime/status",
        "classification": "diagnostic",
        "evidence": {"status": "degraded", "marker": "keep-zeta"},
        "safe_next_inspection": "Inspect unavailable evidence.",
    }
    first_target = {
        **later_target,
        "target": "alpha",
        "evidence": {"status": "degraded", "marker": "keep-alpha"},
    }

    forward = select_attention(_snapshot(later_target, first_target))
    reverse = select_attention(_snapshot(first_target, later_target))

    assert forward == reverse
    assert forward["selected_finding"] == first_target


def test_exact_documented_ties_use_complete_finding_content_not_input_order():
    first = {
        "code": "plugin_configuration_incomplete",
        "severity": "attention",
        "scope": "target",
        "target": "alpha",
        "observed_at": "2026-08-12T02:30:00Z",
        "source": "GET /api/runtime/status",
        "classification": "diagnostic",
        "evidence": {"plugins": [{"id": "alpha"}]},
        "safe_next_inspection": "Inspect plugin settings.",
    }
    second = {
        **first,
        "evidence": {"plugins": [{"id": "zeta"}]},
    }

    forward = select_attention(_snapshot(second, first))
    reverse = select_attention(_snapshot(first, second))

    assert forward == reverse
    assert forward["selected_finding"] == first


def test_rejects_malformed_findings_before_ranking():
    malformed = _snapshot({"code": "target_readiness_attention"})

    try:
        select_attention(malformed)
    except ValueError as exc:
        assert str(exc) == "snapshot.findings[0].severity must be a non-empty string"
    else:
        raise AssertionError("malformed finding was ranked")


def test_readiness_status_does_not_reorder_non_readiness_findings():
    lexical_first = {
        "code": "plugin_configuration_incomplete",
        "severity": "attention",
        "scope": "target",
        "target": "alpha",
        "observed_at": "2026-08-12T02:30:00Z",
        "source": "GET /api/runtime/status",
        "classification": "diagnostic",
        "evidence": {"plugins": [{"id": "alpha"}]},
        "safe_next_inspection": "Inspect plugin settings.",
    }
    misleading_status = {
        **lexical_first,
        "target": "zeta",
        "evidence": {"plugins": [{"id": "zeta"}], "status": "unreachable"},
    }

    result = select_attention(_snapshot(misleading_status, lexical_first))

    assert result["selected_finding"] == lexical_first
