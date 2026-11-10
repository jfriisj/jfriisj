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
                links = re.findall(r'<link\\s+rel="alternate"\\s+hreflang="([^"]+)"\\s+href="([^"]+)"', html)
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

    def test_drafts_not_published(self):
        self.assertFalse((DIST / "publikationer" / "_draft-eksempel").exists())
        self.assertNotIn("Eksempel på en kommende teknisk artikel", (DIST / "publikationer" / "index.html").read_text(encoding="utf-8"))

    def test_home_has_links_to_both_archives(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/projekter/"', html)
        self.assertIn('href="/publikationer/"', html)
        self.assertIn("Operiva", html)

    def test_source_security(self):
        html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="da">', html)
        self.assertNotIn("dummypassword", html)

if __name__ == "__main__":
    unittest.main()
