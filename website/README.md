# friis-jakobsen.dk – personlig portfolio

Version 0.4 moves the existing responsive portfolio from a single HTML file to a statically generated [Astro](https://astro.build) site with Markdown content collections. The layout, homepage animation, network topology and hosting provider remain unchanged.

**Host:** Proxmox VM 1214 (`ci-runner`), via central Dockhand / Hawser.
**Network:** existing `development-proxy` Docker bridge (shared with existing `cloudflare-cloudflared-1`).
**Cloudflare origin:** `http://friis-jakobsen-portfolio:8080`, routed to `https://friis-jakobsen.dk`.
**Deploy policy:** manually sync, rebuild and deploy the reviewed `main` revision; no webhooks/auto-update.
**Sources:** [deployment model](https://github.com/jfriisj/development-knowledge/blob/main/deploy/dockhand/README.md), [onboarding](https://github.com/jfriisj/development-knowledge/blob/main/deploy/dockhand/onboarding.md).

## Local development

Node.js 24 or newer is required.

```sh
cd website
npm install
npm run dev
npm run build
cd ..
python3 -m unittest discover -s website/tests -v
```

Run generated-site tests **after** `npm run build`. CI validates Markdown metadata/PDF files, builds Astro, checks static routes and links, validates Compose and builds the Docker image. CI never deploys.

## Add a project

Create `src/content/projects/<slug>.md`. Example:

```yaml
---
title: "Mit projekt"
summary: "En konkret beskrivelse af projektets formål og faglige resultater."
category: network
typeLabel: "Data & netværk"
tags: ["Netværk", "Fejlfinding"]
featured: false
order: 100
draft: true
---
Her beskriver jeg problem, metode, løsning og resultat.
```

Categories: `software`, `research`, `automation`, `network`, `electrical`, `business`.

## Add an article or report

Create `src/content/publications/<slug>.md`:

```yaml
---
title: "Rapportens titel"
summary: "En kort, præcis beskrivelse af rapportens indhold og anvendelse."
type: rapport
tags: ["Software", "Analyse"]
authors: ["Jon Friis Jakobsen"]
date: 2026-11-10
featured: false
draft: true
---
Rapportens resumé og faglige kontekst skrives her.
```

Types: `rapport`, `artikel`, `opgave`, `andet`.

When the actual, publication-approved PDF exists, add it as `public/documents/<filename>.pdf` and add the metadata field `pdf: "/documents/<filename>.pdf"` (case-sensitive). Local PDF references are checked before every build for path correctness, existence and a PDF header. The generated detail page then exposes **Open PDF**, **Download PDF** and an in-browser reader. Without `pdf`, those actions are not shown. External publications can use `externalUrl: "https://..."` without pretending to host a PDF.

Each new entry starts with `draft: true`; **change explicitly to `draft: false`** after reviewing facts, confidentiality, customer information, personal information, copyrights, publication rights and PDF content. A published Markdown file is also visible in the *public GitHub repository*; uploading a PDF to `public/` makes it publicly downloadable from the site and GitHub. Do not commit confidential documents.

Changes to Markdown automatically update index/list/detail pages on the next `npm run build`; no database or CMS is required.

## Deployment via Dockhand

After PR review and merge:

1. In central Dockhand, verify the correct `ci-runner` remote environment and the **existing** `friis-jakobsen-portfolio` Git stack.
2. Git Sync `main` and **rebuild the image** (Astro generates static HTML during the Docker multi-stage build), then manually deploy only this stack.
3. Verify the container remains healthy and that the existing Cloudflare origin `http://friis-jakobsen-portfolio:8080` reaches the new site through `development-proxy`.
4. Check HTTPS `https://friis-jakobsen.dk`, desktop/mobile layout, homepage animation, `/projekter/`, `/publikationer/` and publication pages.
5. Confirm the Gnosis/Cloudflare/Tailscale/Hawser/Dockhand services are unaffected; record the deployed commit SHA and roll back **only this stack** if needed.

The immutable image-digest pinning and lockfile hardening are follow-up production tasks; direct Astro dependency version is pinned, but transitive npm dependencies are not yet locked. No existing Docker network, tunnel, DNS record or service is modified by this PR.

**Status:** Source change only until owner approves manual deployment. Version 0.3 remains live until Dockhand rebuilds/redeploys.
