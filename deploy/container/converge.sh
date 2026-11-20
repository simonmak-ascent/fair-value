#!/usr/bin/env bash
#
# Hold one container at the digest the deployment intends. Safe on a timer: every tick observes the
# node and acts only on a difference.
#
#   converge.sh --container fv-mcp
#
# The desired digest comes from, in order:
#
#   1. ghcr.io/<repo>:desired-<container>   the pointer the deploy moves for this container alone
#   2. ghcr.io/<repo>:desired               the legacy repo-wide pointer, accepted only when it names
#                                           this container's own declared digest — never merely because
#                                           this repository declares one role, which a stale tag also
#                                           satisfies
#   3. /var/lib/container-deploy/<container>.desired
#                                           the node's own record, used when neither pointer
#                                           resolves — written by every rollout on this node
#
# A per-container pointer is what makes a peer converge on its own: the record at path 3 is written
# by any rollout here, including one this timer started, so preferring it — as this script did
# until 2026-11-19 — meant a node that had ever converged never moved again.
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
    -h|--help) sed -n '2,28p' "${BASH_SOURCE[0]}"; exit 0 ;;
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
# The contract says owner/name, but one committed manifest declares ghcr.io/browserless/chromium.
# Normalise rather than trust: a prefixed repo makes the RepoDigests pattern and the pull reference
# both wrong.
repo="${repo#ghcr.io/}"

ghcr_login() {
  [ -r "$GHCR_ENV" ] || return 0
  # shellcheck disable=SC1090
  set -a; . "$GHCR_ENV"; set +a
  [ -n "${GHCR_USER:-}" ] && [ -n "${GHCR_TOKEN:-}" ] || return 0
  printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin >/dev/null 2>&1 || true
}

desired=""

RESOLVED=""; PULL_OK=0
resolve() { # <tag> — sets RESOLVED (bare digest) and PULL_OK (the tag exists on the registry)
  RESOLVED=""; PULL_OK=0
  docker pull -q "$1" >/dev/null 2>&1 || return 0
  PULL_OK=1
  # Filter by repository: element 0 is right today, but an image with more than one repo name would
  # make it arbitrary, and an empty list would fall through with no reason logged. The two outcomes
  # are kept apart because falling through after a *successful* pull is how a node moves backwards.
  RESOLVED="$(docker inspect -f '{{range .RepoDigests}}{{println .}}{{end}}' "$1" 2>/dev/null \
    | grep -m1 "^ghcr.io/${repo}@" | sed 's/.*@sha256://')"
  return 0
}

# 1. the per-container pointer — authoritative, and the only source that can tell a peer it has moved
ghcr_login
resolve "ghcr.io/${repo}:desired-${CONTAINER}"
if [ "$PULL_OK" = 1 ] && [ -z "$RESOLVED" ]; then
  # The tag exists, so intent has moved; the inspect simply did not yield a digest. Falling through
  # here would let a stale legacy tag or an old record move a healthy node backwards.
  echo "converge: $CONTAINER — ${repo}:desired-${CONTAINER} exists but did not resolve; not falling back to a possibly older digest" >&2
  exit 1
fi
desired="$RESOLVED"
[ -n "$desired" ] && echo "converge: $CONTAINER intent from ${repo}:desired-${CONTAINER}"

# 2. the legacy repo-wide pointer, accepted ONLY when it names this container's own declared digest —
#    never merely because "this repository declares one role", which a stale tag also satisfies. The
#    earlier version of this comment described that second arm; it was removed after it let a timer
#    move a healthy node onto an older build (see the note at the top of this file).
#    Ahead of the local record because converge-all discovers containers FROM *.desired — every node
#    that has deployed has one, so placing the record first made this branch unreachable and left
#    such a node stuck on the digest it last deployed itself.
if [ -z "$desired" ]; then
  resolve "ghcr.io/${repo}:desired"
  legacy="$RESOLVED"
  if [ -n "$legacy" ]; then
    pinned="$(python3 - "$CONTAINER" "$manifest" <<'PY'
import json, sys
container, path = sys.argv[1], sys.argv[2]
m = json.load(open(path))
for c in (m.get("containers") or [m]):
    if c.get("name") == container:
        print((c.get("image") or "").split("@")[-1].removeprefix("sha256:"))
        break
PY
)"
    # Only when it is this container's declared digest. A publisher may leave this tag stale — the
    # push failure is a warning, not a failure — so accepting it on "this repository has one role"
    # would let a timer move a healthy node onto an older build.
    if [ -n "$pinned" ] && [ "$legacy" = "$pinned" ]; then
      desired="$legacy"
      echo "converge: $CONTAINER intent from the legacy ${repo}:desired"
    else
      echo "converge: ignoring ${repo}:desired (${legacy:0:19}) — it is not this container's declared digest (${pinned:0:19})" >&2
    fi
  fi
fi

# 3. this node's own record — the fallback when neither pointer resolves
if [ -z "$desired" ] && [ -r "$desired_file" ]; then
  desired="$(tr -d '[:space:]' < "$desired_file" | sed 's/^sha256://')"
  [ -n "$desired" ] && echo "converge: $CONTAINER intent from the local record (no pointer resolved)"
fi

if [ -z "$desired" ]; then
  # Not a success: nothing established what this node should run, and converge-all would otherwise
  # report an all-clear for a container it never resolved.
  echo "converge: no desired digest for $CONTAINER — no per-container pointer, no acceptable legacy pointer, no local record" >&2
  exit 1
fi

# The runtime name is declared, not inferred: container.json carries `docker_name` when it differs
# from the manifest name, and every state file is keyed by the manifest name so the two cannot drift.
name="$(python3 - "$CONTAINER" "$manifest" <<'PY'
import json, sys
container, path = sys.argv[1], sys.argv[2]
m = json.load(open(path))
for c in (m.get("containers") or [m]):
    if c.get("name") == container:
        print(c.get("docker_name") or container)
        break
else:
    print(container)
PY
)"

running="$(docker inspect -f '{{.Config.Image}}' "$name" 2>/dev/null || true)"

# A digest this node has already refused is not retried on the timer: the probe passed and the
# production gate did not, so the next tick would restart the live container just to roll it back
# again. Only while that image is what is actually running — the marker must never stand in for a
# container that is gone, which would report an all-clear for an outage.
if [ -r "$STATE_DIR/$CONTAINER.rejected" ]; then
  rejected="$(tr -d '[:space:]' < "$STATE_DIR/$CONTAINER.rejected" | sed 's/^sha256://')"
  if [ -n "$rejected" ] && [ "$desired" = "$rejected" ]; then
    # Only the digest this node actually refused is held. A marker left by an earlier digest must
    # not stop a newer intent from converging: that would park the container down for as long as
    # the file exists, which is the outage this marker is supposed to avoid.
    if [ -z "$running" ]; then
      echo "converge: $CONTAINER is not running and this node previously refused ${rejected:0:19} — start it by hand, or deploy a different digest" >&2
      exit 1
    fi
    echo "converge: $CONTAINER was rejected on this node at ${desired:0:19} — holding the running image until the intent changes"
    exit 0
  fi
fi
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
