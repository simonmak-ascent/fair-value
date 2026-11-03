#!/usr/bin/env bash
#
# Hold one container at the digest the deployment intends. Safe on a timer: every tick observes the
# node and acts only on a difference.
#
#   converge.sh --container fv-mcp
#
# The desired digest comes from, in order:
#
#   1. /var/lib/container-deploy/<container>.desired   written by a deploy that ran on this node
#   2. ghcr.io/<repo>:desired                          the pointer the deploy moves for the whole fleet
#
# The pointer is intent, never a runtime identity: it is resolved to a digest, the digest is pulled and
# recorded, and that digest is what runs. Peers therefore never need the image pushed to them and the
# deploy never needs SSH — which is why this exists instead of the copy-over-the-VPC path.
#
# The node has no checkout of the application repository, so `/var/lib/container-deploy/<container>.manifest.json`
# must exist (written by a deploy, or once by `bootstrap.sh`). Absence is reported, not guessed around.
set -uo pipefail

CONTAINER=""; STATE_DIR="${STATE_DIR:-/var/lib/container-deploy}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GHCR_ENV="${GHCR_ENV:-/etc/container-deploy/ghcr.env}"

while [ $# -gt 0 ]; do
  case "$1" in
    --container) CONTAINER=${2:?}; shift 2 ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "converge: unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$CONTAINER" ] || { echo "usage: converge.sh --container <name>" >&2; exit 2; }

desired_file="$STATE_DIR/$CONTAINER.desired"
manifest="$STATE_DIR/$CONTAINER.manifest.json"
record="$STATE_DIR/$CONTAINER.json"

if [ ! -r "$manifest" ]; then
  echo "converge: no manifest for $CONTAINER at $manifest — bootstrap this node once (deploy/container/bootstrap.sh)" >&2
  exit 1
fi

repo="$(python3 - "$CONTAINER" "$manifest" <<'PY'
import json, sys
name, path = sys.argv[1], sys.argv[2]
m = json.load(open(path))
for c in (m.get("containers") or [m]):
    if c.get("name") == name:
        print(c.get("repo", "")); break
PY
)"
[ -n "$repo" ] || { echo "converge: $CONTAINER has no repo in its manifest" >&2; exit 1; }

ghcr_login() {
  [ -r "$GHCR_ENV" ] || return 0
  # shellcheck disable=SC1090
  set -a; . "$GHCR_ENV"; set +a
  [ -n "${GHCR_USER:-}" ] && [ -n "${GHCR_TOKEN:-}" ] || return 0
  printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin >/dev/null 2>&1 || true
}

desired=""
if [ -r "$desired_file" ]; then
  desired="$(tr -d '[:space:]' < "$desired_file" | sed 's/^sha256://')"
fi

if [ -z "$desired" ]; then
  ghcr_login
  ptr="ghcr.io/${repo}:desired"
  if docker pull -q "$ptr" >/dev/null 2>&1; then
    desired="$(docker inspect --format '{{index .RepoDigests 0}}' "$ptr" 2>/dev/null | sed 's/.*@sha256://')"
  fi
fi

if [ -z "$desired" ]; then
  echo "converge: no desired digest for $CONTAINER (no local record, and $repo:desired did not resolve)"
  exit 0
fi

name="$(python3 - "$CONTAINER" "$record" "$CONTAINER" <<'PY'
import json, os, sys
container, record_path, fallback = sys.argv[1:4]
try:
    print(json.load(open(record_path)).get("docker_name") or fallback)
except Exception:
    print(fallback)
PY
)"

running="$(docker inspect -f '{{.Config.Image}}' "$name" 2>/dev/null || true)"
case "$running" in
  *"@sha256:${desired}"|*"sha256:${desired}") echo "converge: $CONTAINER already at ${desired:0:19}"; exit 0 ;;
esac

if [ -z "$running" ]; then
  echo "converge: $CONTAINER is not running on $(hostname -s) — converging onto ${desired:0:19}"
else
  echo "converge: $CONTAINER runs a different image — converging onto ${desired:0:19}"
fi

# rollout pulls when the image is absent, so this needs no registry logic of its own.
exec "$HERE/rollout.sh" --container "$CONTAINER" --manifest "$manifest" \
  --digest "$desired" --docker-name "$name" --local-only
