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

## License

[MIT](LICENSE)
