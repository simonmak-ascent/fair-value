#!/usr/bin/env bash
#
# One-time, privileged: give a node the manifest it needs to converge an application.
#
#   bootstrap.sh <container.json> <container> [<container> …]
#
# Run as root, once per node per application. After this the node converges on its own: the reconciler
# resolves the `:desired` pointer, pulls the digest it names and records what it ran. Nothing needs to
# be pushed to the node again, and the deploy needs no SSH to it.
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "bootstrap.sh: run as root" >&2; exit 1; }
[ $# -ge 2 ] || { echo "usage: bootstrap.sh <container.json> <container> [<container> …]" >&2; exit 2; }

MANIFEST="$1"; shift
[ -f "$MANIFEST" ] || { echo "bootstrap.sh: $MANIFEST not found" >&2; exit 1; }

STATE=/var/lib/container-deploy
RUNNER_USER="${RUNNER_USER:-deploy}"
RUNNER_GROUP="${RUNNER_GROUP:-$(id -gn "$RUNNER_USER")}"
install -d -m 0775 -o "$RUNNER_USER" -g "$RUNNER_GROUP" "$STATE"

for c in "$@"; do
  install -m 0644 -o "$RUNNER_USER" -g "$RUNNER_GROUP" "$MANIFEST" "$STATE/$c.manifest.json"
  echo "bootstrapped $c from $MANIFEST"
done
