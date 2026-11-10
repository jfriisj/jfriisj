"""Checks for the generated site. Run after npm run build."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.fragments = []
        self.titles = 0
        self.h1s = 0
        self.external = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if "id" in props:
            self.ids.append(props["id"])
        if tag == "a":
            href = props.get("href", "")
            if href.startswith("#"):
                self.fragments.append(href[1:])
            if props.get("target") == "_blank":
                self.external.append(props.get("rel", ""))
        if tag == "title":
            self.titles += 1
        if tag == "h1":
            self.h1s += 1

class SiteTests(unittest.TestCase):
    def test_all_expected_routes_exist(self):
        for path in [
            "index.html",
            "projekter/index.html",
            "projekter/operiva/index.html",
            "projekter/realtidsoversaettelse/index.html",
            "projekter/plc-industri/index.html",
            "publikationer/index.html",
            "publikationer/analysis-and-design-of-a-platform-for-real-time-speech-translation/index.html",
        ]:
            with self.subTest(path=path):
                self.assertTrue((DIST / path).is_file(), path)

    def test_document_links_do_not_precede_documents(self):
        for html in DIST.rglob("*.html"):
            content = html.read_text(encoding="utf-8")
            for pdf in re.findall(r'href=["\'](/documents/[^"\']+\.pdf)', content):
                self.assertTrue((DIST / pdf.lstrip("/")).is_file(), str(html) + " -> " + pdf)

    def test_each_page_has_accessible_structure(self):
        for html in DIST.rglob("*.html"):
            with self.subTest(path=str(html)):
                parser = Structure()
                parser.feed(html.read_text(encoding="utf-8"))
                self.assertEqual(parser.titles, 1)
                self.assertEqual(parser.h1s, 1)
                self.assertEqual(len(parser.ids), len(set(parser.ids)))
                self.assertFalse(set(parser.fragments) - set(parser.ids))
                self.assertTrue(all("noopener" in rel and "noreferrer" in rel for rel in parser.external))

    def test_interactive_thesis_is_accessible_and_source_bounded(self):
        page = DIST / "publikationer" / "analysis-and-design-of-a-platform-for-real-time-speech-translation" / "index.html"
        html = page.read_text(encoding="utf-8")
        for expected in (
            'data-thesis',
            'data-architecture-node="orchestrator"',
            'data-flow-step="3"',
            'data-metric="ttft"',
            'data-percentile="p90"',
            "25 / 25",
            "13,9 %",
            "4078.4",
            "4541.4",
            "den fulde oplevede klient-til-klient-latenstid",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, html)
        self.assertNotIn('href="https://github.com/jfriisj/Kandidat/', html)
        self.assertNotIn('PDF er endnu ikke offentliggjort.', html)
        self.assertIn("Original PDF afventer særskilt publiceringsgodkendelse", html)


    def test_english_routes_and_language_metadata(self):
        for path in [
            "en/index.html",
            "en/projekter/index.html",
            "en/projekter/operiva/index.html",
            "en/publikationer/index.html",
            "en/publikationer/analysis-and-design-of-a-platform-for-real-time-speech-translation/index.html",
        ]:
            with self.subTest(path=path):
                self.assertTrue((DIST / path).is_file(), path)
                html = (DIST / path).read_text(encoding="utf-8")
                self.assertIn('<html lang="en">', html)
                self.assertIn('hreflang="da"', html)
                self.assertIn('hreflang="en"', html)
                self.assertIn('rel="canonical"', html)

    def test_same_home_layout_in_both_languages(self):
        da = (DIST / "index.html").read_text(encoding="utf-8")
        en = (DIST / "en/index.html").read_text(encoding="utf-8")
        self.assertIn("Teknologi.", da)
        self.assertIn("Technology.", en)
        self.assertIn("Craftsmanship.", en)
        self.assertIn('href="/en/projekter/"', en)
        self.assertIn('href="/en/publikationer/"', en)
        self.assertIn('hreflang="en"', da)
        self.assertIn('href="/"', en)

    def test_english_content_and_thesis(self):
        en = (DIST / "en/publikationer/analysis-and-design-of-a-platform-for-real-time-speech-translation/index.html").read_text(encoding="utf-8")
        self.assertIn("From speech to speech.", en)
        self.assertIn("Exploring the architecture.", en)
        self.assertIn("Compare latency", en)
        self.assertIn("Traceability and control are strengths.", en)
        self.assertIn('data-flow-step="3"', en)
        self.assertIn('data-architecture-node="orchestrator"', en)
        self.assertNotIn("Original PDF afventer særskilt publiceringsgodkendelse", en)
        project = (DIST / "en/projekter/operiva/index.html").read_text(encoding="utf-8")
        self.assertIn("Independent software initiative", project)
        self.assertIn("domain modelling", project)


    def test_language_alternates_link_to_real_pages(self):
        import json
        from urllib.parse import urlparse
        locales_dir = ROOT / "src" / "i18n" / "locales"
        locales = sorted(path.stem for path in locales_dir.glob("*.json"))
        for locale in locales:
            home = DIST / ("index.html" if locale == "da" else f"{locale}/index.html")
            self.assertTrue(home.exists(), home)
        for html_file in DIST.rglob("*.html"):
            with self.subTest(page=str(html_file.relative_to(DIST))):
                html = html_file.read_text(encoding="utf-8")
                links = re.findall(r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"', html)
                names = [code for code, _ in links]
                self.assertEqual(len(names), len(set(names)))
                self.assertEqual(set(locales) | {"x-default"}, set(names))
                for code, href in links:
                    parsed = urlparse(href)
                    self.assertEqual(parsed.netloc, "friis-jakobsen.dk")
                    relative = parsed.path.lstrip("/")
                    target = DIST / relative / "index.html" if relative else DIST / "index.html"
                    self.assertTrue(target.exists(), f"{html_file}: {code} -> {href}")

    def test_hero_uses_stable_translation_keys(self):
        import json
        keys = (
            "home.meta.title", "home.meta.description",
            "home.hero.line1", "home.hero.line2", "home.hero.line3",
            "home.hero.lead", "home.hero.primaryCta",
            "home.hero.secondaryCta", "home.hero.caption",
        )
        for code in ("da", "en"):
            values = json.loads((ROOT / "src" / "i18n" / "locales" / f"{code}.json").read_text(encoding="utf-8"))
            self.assertTrue(all(isinstance(values.get(key), str) and values[key].strip() for key in keys))
        source = (ROOT / "src" / "components" / "pages" / "HomePage.astro").read_text(encoding="utf-8")
        self.assertIn('tr("home.hero.line1")', source)
        self.assertIn('tr("home.hero.lead")', source)

    def test_language_switcher_is_locale_agnostic(self):
        switcher = (ROOT / "src" / "components" / "LanguageSwitcher.astro").read_text(encoding="utf-8")
        self.assertIn("switchPath(code, pathname)", switcher)
        self.assertNotIn("destination.pathname.endsWith('/en/')", switcher)


    def test_architecture_explorer_source_grounding(self):
        from html import unescape
        for prefix, expected in (("", "Interaktiv systemarkitektur"), ("en/", "Interactive system architecture")):
            page = DIST / prefix / "publikationer" / "analysis-and-design-of-a-platform-for-real-time-speech-translation" / "index.html"
            markup = unescape(page.read_text(encoding="utf-8"))
            with self.subTest(locale=prefix or "da"):
                self.assertIn('data-architecture-explorer', markup)
                self.assertIn('data-architecture-payload', markup)
                for name in ("gateway", "broker", "orchestrator", "worker", "storage", "redis"):
                    self.assertIn('data-architecture-node="' + name + '"', markup)
                self.assertIn('data-architecture-edge="gateway-storage"', markup)
                self.assertIn('data-architecture-edge="broker-orchestrator"', markup)
                self.assertIn('data-architecture-edge="orchestrator-redis"', markup)
                self.assertEqual(len(re.findall(r'data-architecture-step="\d+"', markup)), 11)
                self.assertIn(expected, markup)
                self.assertIn('pipeline.completed', markup)
                self.assertIn('tts_audio_uri', markup)
                self.assertIn('input_uri', markup)
                self.assertIn('output_uri', markup)

    def test_architecture_explorer_controls_and_reduced_motion(self):
        component = (ROOT / "src" / "components" / "ArchitectureExplorer.astro").read_text(encoding="utf-8")
        css = (ROOT / "src" / "styles" / "thesis.css").read_text(encoding="utf-8")
        for marker in ('data-arch-prev', 'data-arch-next', 'data-arch-play', 'data-arch-reset', "aria-pressed", "aria-live"):
            self.assertIn(marker, component)
        self.assertIn('@media(prefers-reduced-motion:reduce)', css)
        self.assertNotIn("fetch(", component)


    def test_academic_project_routes_in_both_languages(self):
        cases = ("adaptive-game-soundtracks", "co-located-vr", "work-storage-caching")
        for language in ("", "en/"):
            for slug in cases:
                with self.subTest(language=language or "da", project=slug):
                    path = DIST / language / "projekter" / slug / "index.html"
                    self.assertTrue(path.is_file(), str(path))
                    html = path.read_text(encoding="utf-8")
                    self.assertIn("data-academic-case", html)
                    self.assertIn("data-chart-select", html)
                    self.assertIn("data-case-step", html)
                    self.assertIn("academic-chart-table", html)
                    self.assertIn("data-chart-tbody", html)
                    self.assertNotIn('href="/documents/', html)

    def test_academic_cases_preserve_measured_results_and_limitations(self):
        cases = {
            "adaptive-game-soundtracks": (
                "30–43 ms", "10.8–15.7×", "6.0–8.8 s",
                "30", "43", "298", "631", "batch",
            ),
            "co-located-vr": (
                "85.1 min", "58.2 ms", "1.21 mm", "86", "5.78",
                "stationary", "Photon",
            ),
            "work-storage-caching": (
                "94.53%", "A2C", "DQN", "LFU", "LRU", "PPO", "TTL",
                "44.19", "RL",
            ),
        }
        for slug, expected in cases.items():
            path = DIST / "en" / "projekter" / slug / "index.html"
            html = path.read_text(encoding="utf-8")
            with self.subTest(project=slug):
                for item in expected:
                    self.assertIn(item, html)

    def test_home_features_only_three_academic_cases(self):
        for language in ("", "en/"):
            html = (DIST / language / "index.html").read_text(encoding="utf-8")
            self.assertEqual(html.count('class="project-card"'), 3)
            for slug in ("adaptive-game-soundtracks", "co-located-vr", "work-storage-caching"):
                self.assertIn("/projekter/" + slug + "/", html)
            self.assertNotIn('href="/projekter/operiva/"', html)

    def test_academic_cases_have_same_numeric_data_and_localized_copy(self):
        import json
        folder = ROOT / "src" / "i18n" / "locales"
        for language in ("da", "en"):
            values = json.loads((folder / (language + ".json")).read_text(encoding="utf-8"))
            for slug in ("adaptive-game-soundtracks", "co-located-vr", "work-storage-caching"):
                for key in ("title","summary","typeLabel","problem","finding","limits","contributions"):
                    name = "academic." + slug + "." + key
                    self.assertIn(name, values)
                    self.assertTrue(values[name].strip())


    def test_ux_primary_ctas_and_no_empty_home_filters(self):
        for language, label in (("", "Se studieprojekter"), ("en/", "Explore academic projects")):
            html = (DIST / language / "index.html").read_text(encoding="utf-8")
            self.assertIn(label, html)
            self.assertIn('href="#projekter"', html)
            self.assertIn('href="#kontakt"', html)
            self.assertNotIn('class="project-filters"', html)
            self.assertIn('class="skip-link"', html)
            self.assertIn('href="#top"', html)
        for language in ("", "en/"):
            html = (DIST / language / "projekter" / "index.html").read_text(encoding="utf-8")
            self.assertIn('class="skip-link"', html)
            self.assertIn('tabindex="-1"', html)

    def test_academic_case_at_a_glance_and_onward_links(self):
        slugs = ("adaptive-game-soundtracks", "co-located-vr", "work-storage-caching")
        for language in ("", "en/"):
            for slug in slugs:
                html = (DIST / language / "projekter" / slug / "index.html").read_text(encoding="utf-8")
                with self.subTest(language=language or "da", slug=slug):
                    self.assertIn("academic-glance-grid", html)
                    self.assertIn("academic-footer-actions", html)
                    self.assertIn("academic.glance", (ROOT / "src" / "components" / "AcademicCase.astro").read_text(encoding="utf-8"))
                    self.assertIn('href="/' + language + '#kontakt"', html)


    def test_dual_contact_addresses_and_localized_purpose(self):
        for locale, personal, business in (
            ("", "Privat og faglig kontakt", "Arbejdsopgaver"),
            ("en/", "Personal and professional contact", "Business enquiries"),
        ):
            with self.subTest(locale=locale or "da"):
                html = (DIST / locale / "index.html").read_text(encoding="utf-8")
                self.assertIn('href="mailto:jonfjakobsen@gmail.com"', html)
                self.assertIn('href="mailto:simpeltnetvaerk@gmail.com"', html)
                self.assertIn(personal, html)
                self.assertIn(business, html)
                self.assertIn("Send e-mail" if not locale else "Send email", html)
                self.assertNotIn('class="contact-disclosure"', html)

    def test_drafts_not_published(self):
        self.assertFalse((DIST / "publikationer" / "_draft-eksempel").exists())
        self.assertNotIn("Eksempel på en kommende teknisk artikel", (DIST / "publikationer" / "index.html").read_text(encoding="utf-8"))

    def test_home_has_links_to_both_archives(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/projekter/"', html)
        self.assertIn('href="/publikationer/"', html)
        self.assertIn("Generative adaptive soundtracks", html)

    def test_source_security(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="da">', html)
        self.assertNotIn("dummypassword", html)

if __name__ == "__main__":
    unittest.main()
