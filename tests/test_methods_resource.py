"""Producer-side contract gate for the cross-service `fair-value://methods` resource.

apdb-etl consumes this resource to discover calculator parameters and bundles a
normalized copy (gated by its own baseline). To fail *on the producer side* too,
this pins a canonical hash of the resource: any change to the surface must be
reviewed and the baseline regenerated together with the apdb-etl bundle.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mcp_server.method_spec import methods_resource

BASELINE = Path(__file__).resolve().parent.parent / "standards" / "methods-resource-baseline.json"


def canonical_hash(resource: dict) -> str:
    return hashlib.sha256(
        json.dumps(resource, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def test_methods_resource_matches_committed_baseline() -> None:
    resource = methods_resource()
    baseline = json.loads(BASELINE.read_text())

    assert canonical_hash(resource) == baseline["hash"], (
        "fair-value://methods changed. If intentional, run "
        "scripts/write_methods_resource_baseline.py and regenerate the apdb-etl "
        "bundled catalog (pnpm data-plane:gen-catalog)."
    )
    assert resource["server"] == baseline["server"]
    assert resource["version"] == baseline["version"]
    assert len(resource["tools"]) == baseline["tool_count"]


def test_methods_resource_shape() -> None:
    """Structural contract: {server, version, tools:[{tool,title,methods:[…]}]}."""
    resource = methods_resource()
    assert set(resource) >= {"server", "version", "tools"}
    for tool in resource["tools"]:
        assert {"tool", "title", "methods"} <= set(tool)
        for method in tool["methods"]:
            assert {"method", "label", "summary", "required", "optional"} <= set(method)
            assert isinstance(method["required"], list)
            assert isinstance(method["optional"], list)
