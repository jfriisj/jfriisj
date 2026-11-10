# friis-jakobsen.dk — personal portfolio

This is version 0.3 of a **static** personal portfolio. The project has no database or site secrets. The CV, project claims, contact details and publication placeholders require review before publication. No PDF files are deployed yet.

## Authoritative infrastructure references

- [Central Dockhand operating model](https://github.com/jfriisj/development-knowledge/blob/main/deploy/dockhand/README.md)
- [Dockhand manual onboarding gates](https://github.com/jfriisj/development-knowledge/blob/main/deploy/dockhand/onboarding.md)
- [Official Dockhand Git-stack deployment](https://dockhand.pro/manual/)

**Selected target (owner-confirmed 2026-11-10):** Proxmox VM 1214, Docker environment `ci-runner`.

**Observed from user-provided Dockhand screenshot:** Ubuntu 24.04.5 LTS, Docker 29.9.2, Hawser Standard 0.2.52; running containers include cloudflared, VM-local Dockhand, Tailscale, Hawser and Gnosis. SilverBullet is exited. These observations are not a full host or health audit.

**Observed from owner-provided read-only commands:** `cloudflare-cloudflared-1` uses Docker `NetworkMode=development-proxy`, and a Docker bridge network with that exact name already exists on VM 1214. This supports connecting a **new standalone** portfolio container to that external network without modifying or restarting cloudflared.

## Docker networking

The Compose project in `website/compose.yaml`:

- Uses `development-proxy` as an **external** network. It does not create, delete, or own that shared network.
- Declares the unique, project-specific DNS alias `friis-jakobsen-portfolio`.
- Serves unencrypted HTTP **inside the bridge network** on port 8080; the public browser connection uses Cloudflare HTTPS.
- Publishes **no host ports**.
- Uses no persistent volumes, Docker socket mounts or environment secrets.
- Runs Nginx as a non-root user with a read-only filesystem and health check.

Intended Cloudflare Tunnel public-hostname route, only **after approval and successful deployment**:

| Setting | Value |
| --- | --- |
| Public hostname | `friis-jakobsen.dk` |
| Service type | `HTTP` |
| Service URL | `http://friis-jakobsen-portfolio:8080` |
| Tunnel | Reuse the existing Tunnel backing `cloudflare-cloudflared-1` on VM 1214 |

`localhost:8188` from the older Compose proposal **does not work** for this Docker bridge connection and is intentionally removed. The alias is resolvable only from containers attached to `development-proxy`. Never expose the Docker API, Hawser, or port 8080 directly to the internet.

## Read-only preflight on VM 1214

From an authorized shell; do not share credentials, tokens, unredacted `docker inspect` environments or tunnel configuration secrets:

```sh
hostname
docker compose ls --all
docker network inspect development-proxy --format '{{range .Containers}}{{println .Name}}{{end}}'
docker inspect cloudflare-cloudflared-1 --format '{{.HostConfig.NetworkMode}}'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

Check the central Dockhand controller (the existing `https://docker.friis-jakobsen.dk/` interface) points through Hawser to **VM 1214**, with the expected Docker environment. The VM-local Dockhand remains the owner of its existing legacy stacks; do not migrate, adopt, recreate or upgrade them as part of website deployment. Two controllers must not operate on the **same** Compose project.

Check that the external network really contains the existing Cloudflare container and that the network is intended for application origins. Record existing Gnosis, Cloudflare, Tailscale, Hawser, Dockhand health and recovery paths. Check any existing `friis-jakobsen.dk` DNS record and Cloudflare Tunnel hostname assignment before editing either.

## Validate source changes

From the repository root:

```sh
python3 -m unittest discover -s website/tests -v
docker compose -f website/compose.yaml config -q
docker compose -f website/compose.yaml build
```

CI builds and validates the website, but **does not deploy** anything.

## Owner-approved manual Git stack

1. Review and merge the portfolio deployment PR. Verify the target external `development-proxy` network exists on VM 1214 and that its use is approved.
2. From the **central Dockhand**, select the `ci-runner` environment via its established Hawser Standard connection. Create **only a new Git stack**, `friis-jakobsen-portfolio`.
3. Configure repository `jfriisj/jfriisj`, branch `main`, compose path `website/compose.yaml`, and default context directory (the `website/` directory). Enable **Build images on deploy**. Keep auto-sync, webhook deployment, scheduled deployment, and image auto-update **off**.
4. Verify that the build uses the reviewed source revision. Before production launch, review and pin an approved immutable base-image digest (the current Dockerfile references an explicit version tag only). After owner approval, **manually deploy only this new stack**.
5. Confirm the new container is healthy and accessible from the `development-proxy` network. For instance, from an approved test container on that network, request `http://friis-jakobsen-portfolio:8080/healthz` and the root page. Do not assume `cloudflared` has a shell or HTTP diagnostic tools.
6. Only then add the `friis-jakobsen.dk` public-hostname route to the **existing** Cloudflare Tunnel and verify its DNS conflicts/ownership. Keep all pre-existing tunnel routes unchanged.
7. Verify public HTTPS, correct site content on phone and desktop, project/PDF placeholders, and the existing services' health. Record target VM, actual Git revision, new stack identity, DNS change, and rollback plan.

**Rollback:** Remove **only** the new Cloudflare published hostname if needed; stop or redeploy **only** the new portfolio stack. Do not delete the external `development-proxy` network or touch Gnosis, OpenCode, VM-local Dockhand, Tailscale or Hawser.

**Status:** GitHub preparation only. No VM deployment, live DNS change or Cloudflare configuration change has been performed by this repository update.
