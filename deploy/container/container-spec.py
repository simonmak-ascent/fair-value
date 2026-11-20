#!/usr/bin/env python3
"""Print one container's run declaration from container.json as shell assignments.

This is the single place that knows how a manifest field becomes a `docker run` flag, so the
deploy workflow, the rollout script, the reconciler and a human all read the manifest the same
way. Nothing is retyped in YAML and nothing is defaulted silently in two places.

    . <(container-spec.py fv-web)          # PORT=… PROTO=… HEALTH_PATH=… USER=… etc.
    mapfile -t CMD < <(container-spec.py fv-web --cmd)

Every value is shell-quoted, so sourcing the output cannot execute manifest content.
"""

from __future__ import annotations

import json
import shlex
import sys
from typing import NoReturn

# Fields the container contract requires, with the value used when the manifest omits them.
# A default here is a *declared* default, not a silent one: `check.sh` fails a manifest that
# relies on a default for a field the contract marks as required.
DEFAULTS = {
    "network": "bridge",
    "bind": "0.0.0.0",
    "entrypoint": "exec",
    "health_proto": "http",
    "health_path": "/",
}


def fail(msg: str, code: int = 1) -> NoReturn:
    print(f"container-spec: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load(path: str) -> dict:
    try:
        with open(path) as fh:
            return json.load(fh)
    except FileNotFoundError:
        fail(f"{path} not found — this repository has not declared a container", 2)
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}", 2)
    return {}


def pick(manifest: dict, name: str) -> dict:
    items = manifest.get("containers") or [manifest]
    spec = next((c for c in items if c.get("name") == name), None)
    if spec is None:
        known = ", ".join(c.get("name", "?") for c in items)
        fail(f"no container named '{name}' in container.json (have: {known})")
    return spec


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_cmd = "--cmd" in sys.argv
    want_names = "--names" in sys.argv
    path = "container.json"
    if "--manifest" in sys.argv:
        path = sys.argv[sys.argv.index("--manifest") + 1]
        args = [a for a in args if a != path]

    manifest = load(path)

    if want_names:
        for c in manifest.get("containers") or [manifest]:
            print(c.get("name", ""))
        return 0

    if not args:
        fail("usage: container-spec.py <name> [--cmd|--names] [--manifest path]", 2)

    spec = pick(manifest, args[0])
    cmd = spec.get("cmd") or []
    if want_cmd:
        for part in cmd:
            print(part)
        return 0

    health = spec.get("health") or {}
    run = spec.get("run") or {}

    def q(value: object) -> str:
        return shlex.quote(str(value))

    print(f"PORT={q(spec.get('port', ''))}")
    print(f"IMAGE={q(spec.get('image', ''))}")
    print(f"PROTO={q(health.get('proto', DEFAULTS['health_proto']))}")
    print(f"HEALTH_PATH={q(health.get('path', DEFAULTS['health_path']))}")
    print(f"HEALTH_HOST={q(health.get('host', ''))}")
    print(f"ENVFILE={q(run.get('envFile', ''))}")
    print(f"RUN_USER={q(run.get('user', ''))}")
    print(f"NETWORK={q(run.get('network', DEFAULTS['network']))}")
    print(f"BIND={q(run.get('bind', DEFAULTS['bind']))}")
    print(f"ENTRYPOINT={q(run.get('entrypoint', DEFAULTS['entrypoint']))}")
    print(f"APP_REPO={q(spec.get('repo', ''))}")
    print(f"APP_NAME={q(spec.get('name', ''))}")
    print(f"SPEC_DOCKER_NAME={q(spec.get('docker_name') or spec.get('name', ''))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
