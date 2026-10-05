"""A-008: MCP Registry manifest integrity (version lockstep + required fields)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        tomllib = None

pytestmark = pytest.mark.skipif(tomllib is None, reason="no TOML parser")


def _manifest():
    return json.loads((ROOT / "server.json").read_text())


def _version():
    assert tomllib is not None
    with open(ROOT / "pyproject.toml", "rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def test_required_fields_present():
    manifest = _manifest()
    for key in (
        "name",
        "title",
        "description",
        "version",
        "packages",
        "repository",
        "icons",
    ):
        assert key in manifest, f"server.json missing {key}"


def test_version_locked_to_pyproject():
    manifest = _manifest()
    assert manifest["version"] == _version()


def test_package_version_locked_to_manifest():
    import mcp_server

    assert mcp_server.__version__ == _manifest()["version"] == _version()


def test_package_is_pypi_uvx():
    pkg = _manifest()["packages"][0]
    assert pkg["registryType"] == "pypi"
    assert pkg["identifier"] == "fair-value"
    assert pkg["runtimeHint"] == "uvx"


def test_icon_referenced_and_present():
    manifest = _manifest()
    icon = manifest["icons"][0]["src"]
    assert "assets/icon.svg" in icon
    assert (ROOT / "assets" / "icon.svg").is_file()


def test_version_mismatch_is_detectable():
    manifest = _manifest()
    assert manifest["version"] != "999.999.999"


def test_registry_length_limits():
    manifest = _manifest()
    assert len(manifest["description"]) <= 100
    assert len(manifest["title"]) <= 100


def test_readme_has_mcp_name_marker():
    readme = (ROOT / "README.md").read_text()
    assert f"mcp-name: {_manifest()['name']}" in readme


def test_remote_endpoint_declared():
    remotes = _manifest().get("remotes", [])
    assert remotes, "server.json should declare a hosted remote"
    assert any(r.get("type") == "streamable-http" for r in remotes)
