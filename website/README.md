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


## Interactive thesis case study (v0.5)

The thesis entry at
\`/publikationer/analysis-and-design-of-a-platform-for-real-time-speech-translation/\`
renders \`src/components/ThesisExperience.astro\` rather than the generic Markdown
detail template. Its editorial case-study experience provides:

- keyboard-accessible architecture exploration based on central orchestration;
- a conceptual VAD → ASR → MT → TTS stepper (not a live speech demo);
- measured TTFT/TTFA P50/P90 at concurrency c=1–5 with an accessible HTML table;
- source qualifications, limitations and responsive/reduced-motion styles.

**Research source:** the private \`jfriisj/Kandidat\` repository, \`multilanguage\`
branch, report LaTeX chapters 06 (design), 08 (evaluation) and 11 (conclusion).
The inspected source head was \`27fa606c7f3362fc45aeda5d63bee035ca17d135\`.
The chart numbers are transcribed from evaluation tables, not queried live.
The web article is a curated explanation, not a full thesis transcription.
If the source results change, update the arrays, descriptions and tests together.

**Publication boundary:** \`Kandidat\` is private. Do not link to its PDF as
though it were publicly accessible. Do not copy the PDF, diagrams, datasets
or other non-public materials into this public repository without an explicit
rights and confidentiality review. A separately cleared local PDF can be
added later through the validated \`pdf\` frontmatter field.

To review, run \`npm run build\` and \`python3 -m unittest discover -s tests\`,
then inspect the interactive route with and without JavaScript and with
keyboard navigation and reduced motion. A commit to GitHub never deploys
the stack: merge, then manually Git Sync → Rebuild → Deploy in Dockhand.

## JSON-driven internationalization (v0.6)

The site has **one** Astro implementation of each layout, homepage, project detail, publication index and interactive thesis. Text is selected by the **filename** in `src/i18n/locales/*.json`, and non-Danish locale routes are statically generated by `getStaticPaths()`. No duplicated landing pages, client-side machine translation, database, or language-specific routing code is required.

Current URLs:
- Danish default: `/`, `/projekter/`, `/publikationer/` and detail pages.
- English: `/en/`, `/en/projekter/`, `/en/publikationer/` and the **same slugs** for detail pages.

To add French, for example:
1. Copy `src/i18n/locales/en.json` to `src/i18n/locales/fr.json`.
2. Translate **all values**, retaining each key exactly (keys are stable lookup identifiers, originally derived from the Danish copy).
3. Run `npm run build` and site tests. The build fails if any required key is absent, any extra key is present, or any value is blank.
4. Open the site at `/fr/` and navigate via the automatically generated language picker. Check page content, project descriptions, interactive thesis, links, metadata, and spelling before merging.

Locale discovery uses `import.meta.glob` at build time; each new JSON file creates all locale routes and language-switcher entries automatically. **Adding a language still requires a rebuild and manual Dockhand deployment.** Do not add an incomplete JSON file to `main`: the build deliberately rejects it instead of presenting partially Danish content as a translation.

The Danish project body remains canonical in Markdown. Localized body copy for the current projects is provided as translated strings in the locale JSON catalog. Structured project metadata, measured evaluation data, SVG diagrams and shared UI components remain language-neutral. For complex future long-form content, consider separate Markdown per locale while preserving the same shared Astro layout.

Language-specific canonical and `hreflang` tags are generated for each route. There is no automatic language-based redirect; existing public Danish URLs are stable.

**Release workflow:** PR review + green CI → merge to `main` → manually Git Sync → Rebuild → Deploy only the portfolio stack in Dockhand. Cloudflare and the shared Docker bridge do not change.
