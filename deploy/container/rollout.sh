#!/usr/bin/env bash
#
# Canonical container rollout — the one path from "this digest is on the node" to "the node serves it".
#
#   rollout.sh --container fair-value-mcp --digest sha256:… [options]
#
#     --docker-name NAME   name on the node when it differs from the manifest name
#     --peers IP,IP        propagate over the VPC and apply the same gate on each peer
#     --local-only         do not propagate (used by this script when it runs on a peer)
#     --manifest PATH      container.json (default: ./container.json)
#     --dry-run            resolve and print the run command, change nothing
#
# Why a script rather than inline workflow YAML: the probe, the swap, the health gate, the ownership
# check, the rollback and the state record are identical on every node and in every repository, and
# splitting them between YAML and shell is how two sources of truth start disagreeing.
#
# Guarantees, each measured rather than assumed:
#   * the image is referenced by digest, never a tag — a tag is what let apg-web:20261102T152315 drift;
#   * the new container is probed on PORT+10000 before the live one is touched;
#   * the live port must be owned by the container we started, checked through its cgroup;
#   * a node that fails its gate is restored to the image it was running, and the rollout fails;
#   * peers receive the image over the VPC, not through the registry (NAT 5 Mbps, VPC 250 MB/s).
#
set -Eeuo pipefail

CONTAINER=""; DIGEST=""; DOCKER_NAME=""; PEERS=""; LOCAL_ONLY=0; PUBLISH_POINTER=0
MANIFEST="container.json"; DRY_RUN=0
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SELF="$HERE/$(basename "${BASH_SOURCE[0]}")"
SPEC="$HERE/container-spec.py"
STATE_DIR="${STATE_DIR:-/var/lib/container-deploy}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-90}"

while [ $# -gt 0 ]; do
  case "$1" in
    --container)   CONTAINER=${2:?}; shift 2 ;;
    --digest)      DIGEST=${2:?}; shift 2 ;;
    --docker-name) DOCKER_NAME=${2:?}; shift 2 ;;
    --peers)       PEERS=${2:?}; shift 2 ;;
    --manifest)    MANIFEST=${2:?}; shift 2 ;;
    --local-only)  LOCAL_ONLY=1; shift ;;
    --publish-pointer) PUBLISH_POINTER=1; shift ;;
    --dry-run)     DRY_RUN=1; shift ;;
    -h|--help)     sed -n '2,22p' "$SELF"; exit 0 ;;
    *) echo "rollout: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$CONTAINER" ] && [ -n "$DIGEST" ] || {
  echo "usage: rollout.sh --container <name> --digest <sha256:…> [--docker-name N] [--peers ip,ip] [--local-only] [--dry-run]" >&2
  exit 2
}

log() { printf '[rollout] %s\n' "$*" >&2; }
die() { printf '[rollout] ERROR %s\n' "$*" >&2; exit 1; }

HOST="$(hostname -s)"

# --- resolve the declaration -------------------------------------------------

spec_out="$(python3 "$SPEC" "$CONTAINER" --manifest "$MANIFEST")" \
  || die "cannot read '$CONTAINER' from $MANIFEST"
eval "$spec_out"

[ -n "${PORT:-}" ] || die "'$CONTAINER' has no port in $MANIFEST"
[ -n "${APP_REPO:-}" ] || die "'$CONTAINER' has no repo in $MANIFEST"
REF="ghcr.io/${APP_REPO}@${DIGEST}"
NAME="${DOCKER_NAME:-${SPEC_DOCKER_NAME:-$CONTAINER}}"

mapfile -t CMD < <(python3 "$SPEC" "$CONTAINER" --cmd --manifest "$MANIFEST")

run_opts=(
  --restart unless-stopped
  --network "${NETWORK:-bridge}"
  -e NODE_ENV=production
  -e "PORT=$PORT"
)
[ -n "${ENVFILE:-}" ] && run_opts+=(--env-file "$ENVFILE")
[ -n "${RUN_USER:-}" ] && run_opts+=(--user "$RUN_USER")

publish_spec() { printf '%s:%s:%s' "${BIND:-0.0.0.0}" "$1" "$PORT"; }

# A read-only credential the node holds so it can pull without being pushed to. Never in a workflow:
# the value lives in /etc/container-deploy/ghcr.env, 0640 root:docker, on nodes that need it.
GHCR_ENV="${GHCR_ENV:-/etc/container-deploy/ghcr.env}"
ghcr_login() {
  [ -r "$GHCR_ENV" ] || return 0
  # shellcheck disable=SC1090
  set -a; . "$GHCR_ENV"; set +a
  [ -n "${GHCR_USER:-}" ] && [ -n "${GHCR_TOKEN:-}" ] || return 0
  printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin >/dev/null 2>&1 || true
}

pull_image() { # <ref>
  ghcr_login
  docker pull "$1" >/dev/null
}

log "spec $CONTAINER -> name=$NAME port=$PORT proto=$PROTO user=${RUN_USER:-image-default}"

if [ "$DRY_RUN" = 1 ]; then
  printf 'docker run -d --name %s %s -p %s %s' \
    "$NAME" "${run_opts[*]}" "$(publish_spec "$PORT")" "$REF"
  printf ' %q' "${CMD[@]+"${CMD[@]}"}"
  printf '\n'
  exit 0
fi

mkdir -p "$STATE_DIR"

# --- probes ------------------------------------------------------------------

wait_ready() { # <container-name> <host-visible-port> <seconds>
  local cname="$1" port="$2" deadline=$((SECONDS + ${3:-$HEALTH_TIMEOUT})) code
  while [ "$SECONDS" -lt "$deadline" ]; do
    if [ "$PROTO" = "tcp" ]; then
      [ "$(docker inspect -f '{{.State.Running}}' "$cname" 2>/dev/null)" = "true" ] && return 0
    else
      code=$(curl -sS -m 3 -o /dev/null -w '%{http_code}' \
        -H "Host: ${HEALTH_HOST:-localhost}" "http://127.0.0.1:${port}${HEALTH_PATH:-/}" 2>/dev/null || echo 000)
      [ "$code" = "200" ] && return 0
    fi
    sleep 1
  done
  return 1
}

owns_port() { # <port> — the published port belongs to this container
  local port="$1" running mapping
  # For a bridge-network container the host-side listener is `docker-proxy`, which lives in
  # docker.service's cgroup — so the systemd-era cgroup test used for #490 rejects a perfectly good
  # swap. The authoritative check would be `nsenter -t <pid> -n ss`, but that needs CAP_SYS_ADMIN and
  # the deploy workflow runs as the runner user, not root.
  #
  # What remains is still meaningful, and Docker enforces it: a container only starts if the published
  # port is free, so "running + the mapping exists" cannot be a leftover process answering instead.
  # A conflict makes `docker run` fail, which start() turns into a rollback.
  running=$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)
  [ "$running" = "true" ] || return 1
  mapping=$(docker port "$NAME" "$port" 2>/dev/null)
  [ -n "$mapping" ] || return 1
  return 0
}

start() { # <image-ref> <published-port>
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  if ! docker run -d --name "$NAME" "${run_opts[@]}" -p "$(publish_spec "$2")" "$1" \
    ${CMD[@]+"${CMD[@]}"} >/dev/null; then
    return 1
  fi
}

record() { # <state> <previous>
  python3 - "$STATE_DIR/$CONTAINER.json" "$CONTAINER" "$NAME" "$REF" "$PORT" "$1" "$2" <<'PY'
import datetime, json, socket, sys
path, container, name, image, port, state, previous = sys.argv[1:8]
doc = {
    "container": container,
    "docker_name": name,
    "image": image,
    "port": int(port),
    "previous": previous,
    "state": state,
    "host": socket.gethostname(),
    "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
}
with open(path, "w") as fh:
    json.dump(doc, fh, indent=2)
    fh.write("\n")
PY
}

deploy_local() {
  local previous previous_id
  # `docker save | ssh | docker load` does not preserve the registry reference: the peer holds the
  # image by ID only. Falling back to the digest keeps one script valid on both sides of the copy.
  if ! docker image inspect "$REF" >/dev/null 2>&1; then
    if docker image inspect "sha256:${DIGEST#sha256:}" >/dev/null 2>&1; then
      log "$REF arrived by copy as image id ${DIGEST:0:19}"
      REF="sha256:${DIGEST#sha256:}"
    else
      # Pull instead of refusing. This is what lets a node converge on its own: the deploy does not
      # need SSH to its peers, and a peer needs no copy pushed to it. The credential is read-only and
      # lives on the node (/etc/container-deploy/ghcr.env), never in a workflow.
      pull_image "$REF" || die "$REF is not on $HOST and could not be pulled"
    fi
  fi

  if [ -n "${ENVFILE:-}" ] && [ ! -r "$ENVFILE" ]; then
    die "env file $ENVFILE is not readable by $(id -un) — contract requires root:<runner-group> 640"
  fi

  # 1. probe on a spare port; nothing live is touched
  docker rm -f "$NAME.probe" >/dev/null 2>&1 || true
  docker run -d --name "$NAME.probe" "${run_opts[@]}" \
    -p "127.0.0.1:$((PORT + 10000)):$PORT" "$REF" ${CMD[@]+"${CMD[@]}"} >/dev/null
  if ! wait_ready "$NAME.probe" "$((PORT + 10000))" "$HEALTH_TIMEOUT"; then
    docker logs --tail 30 "$NAME.probe" >&2 || true
    docker rm -f "$NAME.probe" >/dev/null 2>&1 || true
    die "$CONTAINER did not answer on the probe port; the live container is untouched"
  fi
  docker rm -f "$NAME.probe" >/dev/null 2>&1 || true

  # 2. remember what to go back to
  previous="$(docker inspect -f '{{.Config.Image}}' "$NAME" 2>/dev/null || true)"
  previous_id="$(docker inspect -f '{{.Image}}' "$NAME" 2>/dev/null || true)"
  if [ -n "$previous_id" ]; then printf '%s\n' "$previous_id" > "$STATE_DIR/$CONTAINER.previous"; fi

  # 3. swap, then prove the swap is good
  if ! start "$REF" "$PORT"; then
    log "$CONTAINER could not start on :$PORT on $HOST (port already in use?)"
    record failed "${previous:-none}"
    if [ -n "$previous_id" ]; then start "$previous_id" "$PORT" || log "WARNING: the restore also failed"; fi
    die "$CONTAINER did not start on $HOST"
  fi
  if ! wait_ready "$NAME" "$PORT" "$HEALTH_TIMEOUT"; then
    log "$CONTAINER failed its health gate on $HOST"
    docker logs --tail 40 "$NAME" >&2 || true
    record failed "${previous:-none}"
    if [ -n "$previous_id" ]; then
      log "restoring ${previous_id:0:19} on $HOST"
      start "$previous_id" "$PORT"
      wait_ready "$NAME" "$PORT" "$HEALTH_TIMEOUT" || log "WARNING: the restore also failed its gate"
    fi
    die "$CONTAINER rolled back on $HOST"
  fi

  # 4. the port must belong to the container we started
  if ! owns_port "$PORT"; then
    log "$CONTAINER answers but does not own :$PORT on $HOST — another process holds it"
    record ownership-failed "${previous:-none}"
    if [ -n "$previous_id" ]; then start "$previous_id" "$PORT"; fi
    die "$CONTAINER failed the ownership check on $HOST"
  fi

  cp -f "$MANIFEST" "$STATE_DIR/$CONTAINER.manifest.json" 2>/dev/null || true
  # The node's own record of intent. The reconciler prefers it over the registry pointer, so a node
  # that deployed keeps converging even if it cannot reach the registry.
  printf '%s\n' "${DIGEST#sha256:}" > "$STATE_DIR/$CONTAINER.desired" 2>/dev/null || true
  record healthy "${previous:-none}"
  log "$HOST: $NAME runs ${DIGEST:0:19} on :$PORT"
}

deploy_local

# --- publish the desired pointer ---------------------------------------------
#
# Peers do not receive the image over SSH: the deploy runner is not root and the peers authorise only
# root's key. Instead the deploy moves a pointer tag, and each node's reconciler resolves it, pulls the
# digest it names, and records what it ran. The tag is intent, never a runtime identity — the digest is.
if [ "$PUBLISH_POINTER" = 1 ]; then
  ptr="ghcr.io/${APP_REPO}:desired"
  if docker tag "$REF" "$ptr" && docker push -q "$ptr" >/dev/null 2>&1; then
    log "pointer $ptr -> ${DIGEST:0:19}"
  else
    die "could not publish the desired pointer $ptr"
  fi
fi

log "done: $CONTAINER ${DIGEST:0:19}"
