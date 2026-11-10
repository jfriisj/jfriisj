from html.parser import HTMLParser
from pathlib import Path
import unittest

class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.fragments = []
        self.titles = 0
        self.h1s = 0
        self.external_links = []
    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if 'id' in props: self.ids.append(props['id'])
        if tag == 'a':
            href = props.get('href', '')
            if href.startswith('#'): self.fragments.append(href[1:])
            if props.get('target') == '_blank': self.external_links.append(props.get('rel', ''))
        if tag == 'title': self.titles += 1
        if tag == 'h1': self.h1s += 1

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (Path(__file__).resolve().parents[1] / 'index.html').read_text(encoding='utf-8')
        cls.page = Structure()
        cls.page.feed(cls.html)
    def test_title_and_h1(self):
        self.assertEqual((self.page.titles, self.page.h1s), (1, 1))
    def test_fragments(self):
        self.assertFalse(set(self.page.fragments) - set(self.page.ids))
    def test_unique_ids(self):
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
    def test_new_tabs(self):
        self.assertTrue(all('noopener' in rel and 'noreferrer' in rel for rel in self.page.external_links))
    def test_no_external_scripts(self):
        self.assertNotIn('<script src=', self.html.lower())
    def test_language(self):
        self.assertIn('<html lang="da">', self.html)
