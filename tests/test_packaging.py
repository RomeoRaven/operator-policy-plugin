from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_pure_policy_and_operator_control_dependency():
    manifest = yaml.safe_load((ROOT / "protoagent.plugin.yaml").read_text())

    assert manifest["id"] == "operator_policy"
    assert manifest["version"] == "0.1.0"
    assert manifest["enabled"] is False
    assert manifest["min_protoagent_version"] == "0.131.3"
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

    readme = (ROOT / "README.md").read_text()
    proto = (ROOT / "PROTO.md").read_text()
    normalized_readme = " ".join(readme.split())
    assert "## Platform evidence" in readme
    assert "| Linux |" in readme
    assert "| Windows |" in readme
    assert "| macOS |" in readme
    assert "CI coverage (not current-head proof)" in readme
    assert "pull requests and pushes to main" in normalized_readme
    assert "every pushed/PR head" not in normalized_readme
    assert "0.136.0" in readme
    assert "1d80d15e229ac51a419b53c3378db1bea4796379" in readme
    assert "qualification host candidate" in normalized_readme
    assert "0.136.0" in proto
    assert "1d80d15e229ac51a419b53c3378db1bea4796379" in proto
    assert "campaign baseline, not installed-runtime acceptance" in " ".join(proto.split())
    assert "Current exact-head installed-runtime acceptance: **Not tested**" in readme
    assert "PC1 install/load/composition acceptance is **Not tested**" in normalized_readme
    assert "not PC1 acceptance" in normalized_readme
    for contradictory_claim in (
        "is installed-runtime acceptance",
        "acceptance is tested and accepted",
        "acceptance is tested and passed",
        "acceptance has passed",
        "CI proves current-head",
        "current-head CI passed",
    ):
        assert contradictory_claim not in normalized_readme


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
