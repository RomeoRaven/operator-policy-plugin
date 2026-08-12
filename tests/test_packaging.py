from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_pure_policy_and_operator_control_dependency():
    manifest = yaml.safe_load((ROOT / "protoagent.plugin.yaml").read_text())

    assert manifest["id"] == "operator_policy"
    assert manifest["version"] == "0.1.0"
    assert manifest["enabled"] is False
    assert manifest["repository"] == "https://github.com/RomeoRaven/operator-policy-plugin"
    assert manifest["homepage"] == "https://agent.protolabs.studio"
    assert manifest["requires_plugins"] == ["operator_control"]
    assert manifest["capabilities"] == {"network": [], "filesystem": "none"}
    assert "config" not in manifest
    assert "secrets" not in manifest
    assert "settings" not in manifest
    license_text = (ROOT / "LICENSE").read_text()
    assert license_text.startswith("MIT License\n")
    assert "Copyright (c) 2026 RomeoRaven" in license_text


def test_packaging_and_ci_cover_declared_platforms():
    project = (ROOT / "pyproject.toml").read_text()
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert 'version = "0.1.0"' in project
    assert 'requires-python = ">=3.11"' in project
    for runner in ("ubuntu-latest", "windows-latest", "macos-latest"):
        assert runner in workflow
    assert "pytest -q" in workflow
    assert "ruff check ." in workflow
    assert "ruff format --check ." in workflow


def test_proto_is_the_only_agent_grounding_file():
    assert (ROOT / "PROTO.md").is_file()
    assert not (ROOT / "AGENTS.md").exists()
    assert not (ROOT / "CLAUDE.md").exists()
