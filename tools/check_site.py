"""Check generated pages, local links, fragment targets, and publishable files."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links = set(), []
        self.path = path
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, (self.path, 'duplicate ID', attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

pages = {p.resolve(): Page(p) for p in ROOT.glob('*.html')}
assert len(pages) == 4
for path, page in pages.items():
    assert '\ufffd' not in path.read_text(), (path, 'invalid UTF-8 replacement')
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        assert target.is_relative_to(ROOT), (path, 'link outside project', link)
        assert target.is_file(), (path, 'missing file', link)
        if url.fragment:
            assert target in pages and unquote(url.fragment) in pages[target].ids, (path, 'missing anchor', link)
print('site: PASS (4 pages, UTF-8, local assets, navigation, download links, anchors)')
