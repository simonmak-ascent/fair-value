"""A-002: the packaging contract in pyproject.toml."""

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

sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.skipif(tomllib is None, reason="no TOML parser available")


def _load():
    assert tomllib is not None
    with open(ROOT / "pyproject.toml", "rb") as fh:
        return tomllib.load(fh)


def test_pyproject_exists_and_parses():
    assert (ROOT / "pyproject.toml").is_file()
    assert isinstance(_load(), dict)


def test_project_metadata_present():
    proj = _load()["project"]
    for key in ("name", "version", "requires-python", "dependencies"):
        assert key in proj, f"missing [project].{key}"


def test_mcp_extra_contains_fastmcp():
    extras = _load()["project"].get("optional-dependencies", {})
    assert "mcp" in extras
    names = {d.split(">")[0].split("=")[0].strip().lower() for d in extras["mcp"]}
    assert "fastmcp" in names


def test_fastmcp_is_not_a_required_dependency():
    deps = _load()["project"]["dependencies"]
    assert not any(d.lower().startswith("fastmcp") for d in deps)


def test_mcp_console_entry_point_declared():
    scripts = _load()["project"].get("scripts", {})
    assert scripts.get("valuation-skills-mcp") == "mcp_server.server:main"


def test_build_system_declared():
    bs = _load()["build-system"]
    assert bs.get("build-backend")
    assert bs.get("requires")


def test_package_discovery_includes_src_and_engine():
    tool = _load().get("tool", {}).get("setuptools", {})
    assert "valuation_engine" in tool.get("py-modules", [])

    packages = tool.get("packages")
    if isinstance(packages, list):
        assert "src" in packages
    else:
        includes = (packages or {}).get("find", {}).get("include", [])
        assert any(str(i).startswith("src") for i in includes)


def test_malformed_toml_raises():
    assert tomllib is not None
    with pytest.raises(Exception):
        tomllib.loads("this is = = not valid toml")
