#!/usr/bin/env python3
"""Print one container's run declaration as shell variable assignments.

The deploy workflow sources this, so the container's port, health and command come
from `container.json` and nothing is retyped in YAML.

    . <(scripts/container-spec.py iv-api)          # PORT=… PROTO=… HEALTH_PATH=…
    mapfile -t CMD < <(scripts/container-spec.py iv-api --cmd)
"""

from __future__ import annotations

import json
import shlex
import sys


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--cmd"]
    want_cmd = "--cmd" in sys.argv
    if not args:
        print("usage: container-spec.py <name> [--cmd]", file=sys.stderr)
        return 2
    name = args[0]
    with open("container.json") as fh:
        d = json.load(fh)
    items = d.get("containers", [d])
    spec = next((c for c in items if c.get("name") == name), None)
    if spec is None:
        print(f"no container named {name} in container.json", file=sys.stderr)
        return 1

    cmd = spec.get("cmd") or []
    if want_cmd:
        for part in cmd:
            print(part)
        return 0

    health = spec.get("health") or {}
    run = spec.get("run") or {}
    print(f"PORT={spec['port']}")
    print(f"PROTO={health.get('proto', 'http')}")
    print(f"HEALTH_PATH={shlex.quote(health.get('path', '/'))}")
    print(f"HEALTH_HOST={shlex.quote(health.get('host', ''))}")
    print(f"ENVFILE={shlex.quote(run.get('envFile', ''))}")
    print(f"IMAGE={shlex.quote(spec.get('image', ''))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
