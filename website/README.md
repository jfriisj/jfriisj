# friis-jakobsen.dk – personal portfolio

Static personal portfolio based on v0.3. No database or private credentials. CV and publication content must be reviewed before a public launch. PDF cards are placeholders.

## Validate

From repository root:

    python3 -m unittest discover -s website/tests -v
    docker compose -f website/compose.yaml config -q
    docker compose -f website/compose.yaml build

On an approved test host when port 8188 is free:

    docker compose -f website/compose.yaml up -d
    curl -fsS http://127.0.0.1:8188/healthz

## Dockhand manual Git deployment

Follow the owner's existing central-Dockhand operating model and gates:
https://github.com/jfriisj/development-knowledge/blob/main/deploy/dockhand/README.md
https://github.com/jfriisj/development-knowledge/blob/main/deploy/dockhand/onboarding.md

1. Verify the actual central Dockhand host behind https://docker.friis-jakobsen.dk, its Docker environment, backups, permissions and license. Do not assume VM 1214 is the controller, and do not migrate existing stacks.
2. Review/merge this PR. Create a NEW Git stack named friis-jakobsen-portfolio, tracking approved main. Use Compose path website/compose.yaml and context directory website if required by the installed Dockhand version.
3. Enable Build images on deploy. Keep auto-sync, webhooks, schedules and image auto-update OFF. Verify localhost TCP 8188 is available, then manually deploy only the new stack with owner approval.
4. Confirm local health and the deployed commit. Review a fixed base image digest before production use; the Dockerfile currently uses an upstream version tag, not a digest.
5. If cloudflared runs on the same host *with host networking*, add the published application hostname friis-jakobsen.dk with service URL http://localhost:8188, after checking existing DNS and route ownership. If cloudflared is containerized in a different network, localhost means its own container; use an explicitly approved shared Docker network with http://portfolio:8080 or a secure private origin instead. Never open a Docker management port or expose the site port on all interfaces as a shortcut.
6. Verify public HTTPS, correct responsive layout, missing PDFs and link behavior; record target host, Compose project, commit SHA and rollback revision.

## Isolation and rollback

This site does not mount Docker socket, existing networks, volumes or secrets. Its only published port is localhost:8188. To roll back, remove only this site's Cloudflare hostname, then stop or redeploy only the friis-jakobsen-portfolio Git stack. Never modify Gnosis, OpenCode, existing Dockhand instances, Hawser or Tailscale while launching this site.

Status: review candidate, not deployed.


## Target host: ci-runner / Proxmox VM 1214 (selected 2026-11-10)

Owner selected VM 1214 to host this website. Dockhand screenshot shows Ubuntu 24.04.5 LTS, Docker 29.9.2 and Hawser Standard 0.2.52, with running containers for Cloudflare, Dockhand, Hawser, Tailscale, Gnosis and the Gnosis tunnel. SilverBullet is exited. This is visual evidence only, not an audited live runtime or network configuration.

The existing documentation in development-knowledge explicitly identifies VM 1214 as a **remote Docker environment**, not the intended central Dockhand controller. Keep the VM-local Dockhand and its existing stacks untouched. Manage this new portfolio stack from the central controller through the verified VM 1214 Hawser environment; only one Dockhand must own the new portfolio Compose project.

### Read-only preflight on VM 1214

Run from an authorized shell. Never paste secret environment values or Cloudflare credentials:

    hostname
    docker compose ls --all
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    docker network ls --format 'table {{.Name}}\t{{.Driver}}'
    docker inspect cloudflare-cloudflared-1 --format '{{.HostConfig.NetworkMode}}'
    docker inspect cloudflare-cloudflared-1 --format '{{json .NetworkSettings.Networks}}'
    sudo ss -ltn '( sport = :8188 )'

Confirm that ci-runner VM 1214 is the exact selected Dockhand/Hawser environment. Validate existing Gnosis, Tunnel, Dockhand and Hawser health and compare after deployment. Verify Dockhand remote Git build context support, project identity, backups/rollback, operator permissions and port 8188 availability.

**Cloudflare routing:** Cloudflared is containerized on VM 1214. Same VM does not imply shared localhost or shared Docker DNS. If cloudflared is host-networked, localhost:8188 may be usable. If bridge-networked, first review a narrowly scoped shared Docker network and a planned attachment of the existing Cloudflare container, or a separately reviewed private origin method. Preserve all existing Cloudflare hostnames and stacks. Never publish 8188 on 0.0.0.0 as a shortcut.

After separate owner approval, manually deploy only the new Git stack, confirm /healthz and page content via the private origin, then add friis-jakobsen.dk to the existing Cloudflare Tunnel only when origin reachability and DNS ownership are verified. Public HTTPS, mobile/desktop display, existing container health and deployed commit SHA are required acceptance evidence. Keep automatic deployments disabled. Document rollback limited to this site's stack and hostname.

**Status:** GitHub implementation is available; VM 1214 deployment and Cloudflare publication are unverified and not performed by this change.
