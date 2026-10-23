"""Collect the unmodified corresponding LGPL library sources for this release."""
import hashlib
import json
from pathlib import Path
import re
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URLS = [
    'https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtbase-everywhere-src-6.12.0.tar.xz',
    'https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtimageformats-everywhere-src-6.12.0.tar.xz',
    'https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz',
]


def main():
    out = ROOT/'dist/library-sources'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for url in URLS:
        with urllib.request.urlopen(url+'.sha256', timeout=60) as response:
            expected = re.search(r'\b[a-f0-9]{64}\b', response.read().decode()).group()
        path = out/url.rsplit('/', 1)[-1]
        if not path.exists():
            with urllib.request.urlopen(url, timeout=90) as response, path.open('wb') as stream:
                while chunk := response.read(1024*1024):
                    stream.write(chunk)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, path.name
        with tarfile.open(path) as archive:
            names = archive.getnames()
            assert any(n.endswith('CMakeLists.txt') for n in names)
            assert any('LICENSE' in n for n in names)
        rows.append({'file': path.name, 'url': url, 'sha256': actual,
                     'bytes': path.stat().st_size, 'publisher_checksum_verified': True,
                     'modifications': 'None; official 6.12.0 sources, including embedded third-party code'})
        print(path.name, path.stat().st_size, actual, flush=True)
    target = ROOT/'benchmarks/public/library-sources.json'
    target.write_text(json.dumps(rows, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
