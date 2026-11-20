#!/usr/bin/env bash
#
# Converge every container this node has deployed. One unit per node, not one per application: the
# set of containers is discovered from the records, so adding an application adds no unit.
#
# Exit codes: 0 when every container is at its declared digest, 1 when any is not (the timer's failed
# state is the alert — silence would otherwise mean "nobody noticed").
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="${STATE_DIR:-/var/lib/container-deploy}"

shopt -s nullglob
found=0
failed=0
for f in "$STATE_DIR"/*.desired; do
  found=$((found + 1))
  c="$(basename "$f" .desired)"
  if ! "$HERE/converge.sh" --container "$c"; then
    echo "converge: $c did not converge" >&2
    failed=$((failed + 1))
  fi
done

[ "$found" -gt 0 ] || { echo "converge: no containers recorded on $(hostname -s)"; exit 0; }
[ "$failed" -eq 0 ] || { echo "converge: $failed of $found container(s) not converged on $(hostname -s)" >&2; exit 1; }
echo "converge: $found container(s) at their declared digests on $(hostname -s)"
