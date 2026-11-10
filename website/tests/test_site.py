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
            "ikke den fulde oplevede klient-til-klient-latenstid",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, html)
        self.assertNotIn('href="https://github.com/jfriisj/Kandidat/', html)
        self.assertNotIn('PDF er endnu ikke offentliggjort.', html)
        self.assertIn("Original PDF afventer særskilt publiceringsgodkendelse", html)

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
