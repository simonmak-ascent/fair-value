#!/usr/bin/env bash
#
# Does this repository actually have a deploy path, or does it only say it has one?
#
#   check.sh <repo-dir>
#
# The compliance contract used to accept `deploy.workflow` on the strength of a file existing. Three
# repositories passed with `release.yml` and `publish.yml` — registry publishing that never touches a
# node — while running images that were days behind main. This checks the deployment, not the word.
set -uo pipefail

REPO="${1:-.}"
CANONICAL="simonmak-ascent/apg-infra/.github/workflows/container-cd.yml@"
fail=0
bad() { printf '  FAIL  %s\n' "$*"; fail=$((fail + 1)); }
ok()  { printf '  ok    %s\n' "$*"; }

[ -f "$REPO/container.json" ] || { echo "  (no container.json — not a container repository)"; exit 0; }
echo "== $REPO"

python3 - "$REPO" <<'PY' || fail=$((fail + 1))
import json, re, sys

repo = sys.argv[1]
problems = []
manifest = json.load(open(f"{repo}/container.json"))
items = manifest.get("containers") or [manifest]

for c in items:
    name = c.get("name", "?")
    if not c.get("port"):
        problems.append(f"{name}: no port — the balancer and the probe both need one")
    image = c.get("image") or ""
    if not image:
        problems.append(f"{name}: no image")
    elif "@sha256:" not in image:
        problems.append(f"{name}: image is not pinned by digest ('{image[:40]}') — a tag can move")
    health = c.get("health") or {}
    if not health.get("path") and health.get("proto", "http") == "http":
        problems.append(f"{name}: health.path is missing for an http service")
    run = c.get("run") or {}
    user = run.get("user") or ""
    if not user:
        problems.append(f"{name}: run.user is missing — the contract forbids root")
    elif user.split(":")[0] in ("0", "root"):
        problems.append(f"{name}: run.user '{user}' is root")
    if run.get("network", "bridge") != "bridge":
        problems.append(f"{name}: run.network must be bridge")
    if not c.get("hosts"):
        problems.append(f"{name}: no hosts — nothing can publish it")
    dn = c.get("docker_name")
    if dn is not None and (not isinstance(dn, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", dn)):
        problems.append(f"{name}: docker_name '{dn}' is not a valid container name")

for p in problems:
    print(f"  FAIL  {p}")
raise SystemExit(1 if problems else 0)
PY

COMPLIANCE="$REPO/compliance.json"
if [ ! -f "$COMPLIANCE" ]; then
  bad "compliance.json is missing — the deploy path is undeclared"
else
  python3 - "$REPO" <<'PY' || fail=$((fail + 1))
import json, os, re, sys

repo = sys.argv[1]
c = json.load(open(f"{repo}/compliance.json"))
d = c.get("deploy") or {}
problems = []

if d.get("kind") != "container":
    problems.append(f"deploy.kind is '{d.get('kind')}' — a container repository must declare 'container'")
wf = d.get("workflow")
if not wf:
    problems.append("deploy.workflow does not name the caller workflow")
else:
    path = f"{repo}/.github/workflows/{wf}"
    try:
        text = open(path).read()
    except FileNotFoundError:
        problems.append(f"deploy.workflow names .github/workflows/{wf}, which does not exist")
        text = ""
    if text and "simonmak-ascent/apg-infra/.github/workflows/container-cd.yml@" not in text:
        vendored = ("deploy/container/rollout.sh" in text
                    and os.path.exists(f"{repo}/deploy/container/rollout.sh")
                    and os.path.exists(f"{repo}/deploy/container/VERSION"))
        if not vendored:
            problems.append(f".github/workflows/{wf} neither calls the canonical container-cd workflow nor runs a vendored deploy/container/rollout.sh — a private copy without a gate")
if not d.get("converge"):
    problems.append("deploy.converge does not name the timer that re-fires without a human")
elif d.get("converge_from") == "apg-infra":
    # Installed from deploy/container/ rather than vendored: one unit on each node, not a copy per
    # repository. check.sh cannot read that unit from here, so it asserts the declaration instead.
    pass
else:
    unit = f"{repo}/deploy/{d['converge']}"
    try:
        t = open(unit).read()
        if "Persistent=true" not in t.replace(" ", ""):
            problems.append(f"deploy/{d['converge']} does not set Persistent=true")
        if "OnBootSec" not in t:
            problems.append(f"deploy/{d['converge']} has no OnBootSec")
    except FileNotFoundError:
        problems.append(f"deploy/{d['converge']} does not exist — or set deploy.converge_from to 'apg-infra'")
if not c.get("e2e"):
    problems.append("e2e is empty — nothing proves the deploy is live")

for p in problems:
    print(f"  FAIL  {p}")
raise SystemExit(1 if problems else 0)
PY
fi

if [ "$fail" -eq 0 ]; then ok "deploy path is declared and present"; else echo "  $fail problem(s)"; fi

# A vendored copy is only acceptable while it is byte-identical to the canonical one. The plugin's
# check can assert that the machinery exists; only this script sees both copies, so this is where
# equality is enforced — otherwise "vendored" would be a polite word for "drifted".
if [ -f "$REPO/deploy/container/rollout.sh" ]; then
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  for f in rollout.sh container-spec.py; do
    if [ ! -f "$REPO/deploy/container/$f" ]; then
      bad "deploy/container/$f is missing — the vendored set is incomplete"
    elif ! cmp -s "$SRC/$f" "$REPO/deploy/container/$f"; then
      bad "deploy/container/$f differs from the canonical copy — re-copy it and update deploy/container/VERSION"
    fi
  done
  if [ -f "$REPO/deploy/container/VERSION" ]; then
    ok "vendored at $(tr -d '\n' < "$REPO/deploy/container/VERSION")"
  else
    bad "deploy/container/VERSION is missing — name the apg-infra commit this was copied from"
  fi
fi

exit "$fail"
