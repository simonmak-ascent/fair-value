"""CI conformance check.

Fails (exit 1) unless the method-spec registry and the derived MCP tool surface
are sound and every registered method is either implemented or explicitly
deferred to an optional dependency. Pure and offline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_server import method_spec as ms
from mcp_server import tool_surface as ts
from mcp_server.engine import is_implemented

#: Methods intentionally not implemented because they require an optional
#: third-party engine (QuantLib) or a heavier numerical scheme.
DEFERRED = {
    "calculate_convertible_bond": {"quantlib", "finite_difference"},
}


def main() -> int:
    problems = list(ms.validate_registry())
    problems += list(ts.validate_surface())

    total = implemented = 0
    for tool in ms.tools():
        for method in ms.methods_for(tool):
            total += 1
            if is_implemented(tool, method):
                implemented += 1
            elif method not in DEFERRED.get(tool, set()):
                problems.append(f"unimplemented method: {tool}.{method}")

    if problems:
        print("CONFORMANCE FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(
        f"conformance ok: {len(ts.TOOL_SURFACE)} tools; "
        f"{implemented}/{total} methods implemented, "
        f"{total - implemented} explicitly deferred"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
