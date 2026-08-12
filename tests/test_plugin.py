import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_plugin():
    root = Path(__file__).resolve().parent.parent
    module_name = "protoagent_plugin_operator_policy_test"
    spec = importlib.util.spec_from_file_location(
        module_name,
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    assert spec is not None and spec.loader is not None
    plugin = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = plugin
    spec.loader.exec_module(plugin)
    return plugin


def test_registers_one_pure_attention_selection_tool():
    plugin = _load_plugin()
    registered = []
    registry = SimpleNamespace(register_tool=registered.append)

    plugin.register(registry)

    assert len(registered) == 1
    tool = registered[0]
    assert tool.name == "operator_select_attention"
    assert set(tool.args) == {"snapshot"}
    result = json.loads(
        tool.invoke(
            {
                "snapshot": {
                    "schema_version": "operator.fleet_snapshot.v1",
                    "observed_at": "2026-08-12T02:30:00Z",
                    "status": "ready",
                    "findings": [],
                }
            }
        )
    )
    assert result["status"] == "no_attention_required"
    assert result["selected_finding"] is None
