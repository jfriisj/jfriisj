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
