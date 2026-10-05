#!/usr/bin/env python3
"""Regenerate standards/methods-resource-baseline.json from the live surface.

Run after an intentional change to the `fair-value://methods` resource, then
regenerate the apdb-etl bundled catalog (`pnpm data-plane:gen-catalog`).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mcp_server.method_spec import methods_resource

OUT = Path(__file__).resolve().parent.parent / "standards" / "methods-resource-baseline.json"


def main() -> None:
    resource = methods_resource()
    params = sorted(
        {
            p
            for tool in resource["tools"]
            for method in tool["methods"]
            for p in (method.get("required", []) + method.get("optional", []))
        }
    )
    baseline = {
        "hash": hashlib.sha256(
            json.dumps(resource, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "server": resource["server"],
        "version": resource["version"],
        "tool_count": len(resource["tools"]),
        "method_count": sum(len(t["methods"]) for t in resource["tools"]),
        "param_count": len(params),
        "note": (
            "Canonical hash of the fair-value://methods resource. If this changes "
            "intentionally, update this file and regenerate the apdb-etl bundled "
            "catalog (pnpm data-plane:gen-catalog)."
        ),
    }
    OUT.write_text(json.dumps(baseline, indent=2) + "\n")
    print(f"wrote {OUT} ({baseline['hash']}, {baseline['method_count']} methods)")


if __name__ == "__main__":
    main()
