"""CI conformance check (A-007).

Fails (exit 1) if the MCP tool surface is invalid or the sibling baseline is
not fully covered by this repo's superset. Pure and offline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_server import superset as ss
from mcp_server import tool_surface as ts


def main() -> int:
    problems = list(ts.validate_surface())
    problems += [f"superset gap: {name}" for name in ss.missing_tools()]

    if problems:
        print("CONFORMANCE FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    cov = ss.coverage()
    print(
        f"conformance ok: {len(ts.TOOL_SURFACE)} native tools; "
        f"superset covered {cov['total']}/{cov['total']} "
        f"(native {len(cov['native'])}, delegated {len(cov['delegated'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
