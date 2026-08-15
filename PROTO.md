# PROTO.md — Operator Attention Policy

This is the repository's single agent-grounding source.

## Purpose and owner boundary

This standalone protoAgent plugin is the executable policy member of `RomeoRaven/operator-stack`, tracked by `RomeoRaven/protoAgent` issue #2. It owns only validation and deterministic attention selection over an existing `operator.fleet_snapshot.v1` result.

Minimum declared protoAgent version is 0.131.3, the earliest retained bundle-integrated host baseline for this implementation. The current qualification host candidate is RR protoAgent 0.136.0 at `1d80d15e229ac51a419b53c3378db1bea4796379`; that identity is a campaign baseline, not installed-runtime acceptance.

`RomeoRaven/operator-plugin` owns fleet collection, normalization, finding construction, source attribution, and secret handling. protoAgent core owns fleet telemetry aggregation/UI and generic operating guidance. Do not move those responsibilities here.

## Interface

The deep module interface is:

```python
select_attention(snapshot: dict) -> dict
```

The plugin exposes one tool, `operator_select_attention(snapshot)`, over the same seam.

Input: one complete `operator.fleet_snapshot.v1` object already returned by Operator Control.

Output:

- `operator.attention_selection.v1`;
- versioned policy identifier `operator.attention_policy.v1`;
- exactly one untouched selected finding, including its existing source evidence and safe next inspection; or
- `no_attention_required` with `selected_finding: null`.

## Policy order

The v1 priority tuple is deterministic and documented:

1. severity: `critical`, `attention`, `warning`, `info`, then unknown;
2. finding category: target readiness, incomplete enabled plugin, fleet version skew, then unknown;
3. target-readiness state: unreachable, degraded, not ready;
4. stable target ID, finding code, source, and observation time;
5. canonical complete finding content as the final total-order fallback.

The policy prioritizes loss of visibility first. It does not guess which runtime version is intended, change finding evidence, or authorize action.

## Safety contract

- Pure function and pure tool wrapper: no network, filesystem, config, secrets, background surface, scheduler, notification, or remediation.
- Requires `operator_control` as a host plugin dependency but does not import or call its implementation.
- Wrong schema, missing/inconsistent top-level status, or malformed finding envelopes fail closed as `invalid_snapshot` at the tool seam.
- Input order cannot change the selected result.
- The selected finding is returned unchanged so provenance remains auditable.
- Unknown future finding codes sort after known v1 categories rather than being discarded.

## Acceptance criteria

1. Empty valid snapshots return `no_attention_required`.
2. Loss of target visibility outranks incomplete-plugin and version-skew findings at the same severity.
3. Selection is independent of input order and preserves the selected finding exactly.
4. Wrong schemas and malformed finding envelopes are rejected rather than reported healthy.
5. The plugin registers exactly one `operator_select_attention` tool with one `snapshot` argument.
6. The manifest declares no network, filesystem, configuration, settings, or secrets.
7. Linux, native Windows, and macOS CI execute lint, format, and the plugin tests.

## Commands

```bash
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest -q
```

## Files

- `policy.py` — validation, versioned ranking, and pure selection result.
- `__init__.py` — one protoAgent tool wrapper and registration.
- `protoagent.plugin.yaml` — disabled-by-default pure-policy manifest.
- `tests/` — behavior, plugin, packaging, and platform-CI contracts.
- `README.md` — operator-facing use and limits.

## Development rules

- Use RED → GREEN → REFACTOR for behavior changes.
- Preserve the single-function policy seam.
- Do not add evidence collection or import protoAgent/operator-plugin implementation modules.
- Do not add persona prose, dashboards, runbooks, scheduling, notifications, incidents, cost/capacity analysis, or writes.
- Keep manifest and project versions in lockstep.
