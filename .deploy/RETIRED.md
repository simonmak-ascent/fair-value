# RETIRED — do not use, do not delete

Nothing in this repository invokes `.deploy/`. Deployment is by digest: `.github/workflows/image.yml`
publishes, `container.json` pins, `.github/workflows/deploy-digest.yml` runs `deploy/container/rollout.sh`.
This directory is the **slot platform** (`apps.yaml` → `kinds/<kind>.sh` → systemd slots + a Caddy
vhost), which the estate no longer publishes with.

**Why it is still here.** `apg-infra` deleted its own copy in `03586c6 chore: delete the obsolete host
and deploy material (#142)`, so there is no canonical one left. Measured 2026-11-20: **7 of these 11
files differ** from that deleted copy —

| file | status vs `apg-infra@03586c6^` |
|---|---|
| `kinds/next-website.sh`, `kinds/node-service.sh`, `kinds/static.sh` | differ |
| `apps.yaml`, `README.md`, `lib.sh`, `runner-bootstrap.sh` | differ |
| `kinds/docker-service.sh`, `kinds/terraform.sh`, `launchers/pylaunch.py`, `launchers/wsgilaunch.py` | identical |

so this is the last live version, not a duplicate — and `kinds/next-website.sh` is the recipe that
produced the `fv-web` image currently serving on all three nodes (`fv-web:20261029T083714`), which has
no registry copy and no recorded source commit.

**Do not delete this directory** while the frontage's build path is undecided (`TASKS.md` 2.1). If it
is deleted later, record here what replaced it and confirm the `fv-web` image is reproducible from a
committed Dockerfile first.
