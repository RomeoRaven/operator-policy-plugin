# Operator Attention Policy plugin

A small, side-effect-free protoAgent plugin for the Operator Stack.

It takes an existing `operator.fleet_snapshot.v1` result from Operator Control and returns either:

- the one finding that needs attention first, preserving its source evidence and safe next inspection; or
- an explicit `no_attention_required` result when the snapshot has no findings.

## What it does not do

It does not inspect targets, make network requests, write files, store incidents, schedule work, send notifications, operate a dashboard, or remediate anything. Fleet collection remains owned by [Operator Control](https://github.com/RomeoRaven/operator-plugin); protoAgent core remains the telemetry/dashboard/runbook owner.

## Tool

`operator_select_attention(snapshot)` accepts the complete JSON object returned by `operator_snapshot`.

The v1 policy ranks loss of target visibility first, then incomplete enabled-plugin configuration, then fleet version mismatch. Ties are deterministic. Unknown future finding types remain visible but sort after known types.

## Status

Incubation implementation for [RomeoRaven/protoAgent issue #2](https://github.com/RomeoRaven/protoAgent/issues/2). Release and upstream publication remain separate decisions.

## Verify

```bash
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest -q
```

See `PROTO.md` for the canonical owner, policy, and safety contract.

## Platform evidence

Minimum declared protoAgent version: **0.131.3**. The Phase A qualification host
candidate is RR protoAgent **0.136.0** at
`1d80d15e229ac51a419b53c3378db1bea4796379`.

CI coverage (not current-head proof): GitHub Actions is configured to gate pull
requests and pushes to main with Ruff and standalone deterministic pytest on
Linux, native Windows, and macOS. Acceptance must read back the checks for the
exact candidate commit.

| Platform | Current evidence | Limitation / owner |
|---|---|---|
| Linux | Configured gate: Ruff and standalone deterministic pytest | Exact-head integration with Operator Control through the real pA loader remains separately tracked in [RR pA #2](https://github.com/RomeoRaven/protoAgent/issues/2) and the Operator Stack |
| Windows | Configured native gate: Ruff and standalone deterministic pytest | PC1 install/load/composition acceptance is **Not tested** and remains owned by [RR pA #14](https://github.com/RomeoRaven/protoAgent/issues/14) |
| macOS | Configured gate: Ruff and standalone deterministic pytest | Installed-runtime acceptance is **Not tested** |

Current exact-head installed-runtime acceptance: **Not tested**. CI proves the
pure policy only after the exact commit's checks pass; it does not prove real pA
dependency resolution, loader composition, or lifecycle. This matrix is not PC1
acceptance.

## License

[MIT](LICENSE)
