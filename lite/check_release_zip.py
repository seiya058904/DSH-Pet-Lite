"""Validate a complete independent portable ZIP, its identity and legal payload."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from edition import EDITIONS, VERSION, profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=True)
    parser.add_argument('--dist', type=Path, default=Path('dist/core-ultra'))
    args = parser.parse_args()
    product = profile(args.edition)['product']
    path = args.dist/f'{product}-v{VERSION}-win-x64-portable.zip'
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        prefix = product+'/_internal/'
        identity = json.loads(archive.read(prefix+'build-info.json'))
        assert identity['edition'] == args.edition and identity['version'] == VERSION and not identity['dirty']
        for name in ['LICENSE', 'ASSET_LICENSE.md', 'THIRD_PARTY_NOTICES.md',
                     'licenses/SOURCE-DELIVERY.md', 'licenses/LGPL-3.0-only.txt', 'licenses/libwebp/COPYING']:
            assert prefix+name in names, name
        manifest = json.loads(archive.read(prefix+'assets/manifest.json'))
        assert len(manifest['clips']) == (11 if args.edition == 'core' else 3)
        frames = [n for n in names if n.startswith(prefix+'assets/') and n.endswith('.webp')]
        assert len(frames) == (2651 if args.edition == 'core' else 723)
        assert not any('/translations/' in n and n.endswith('.qm') for n in names)
        assert product+'/'+product+'.exe' in names
    print(json.dumps({'edition': args.edition, 'zip': path.name, 'bytes': path.stat().st_size,
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'crc': 'PASS', 'identity': identity}))


if __name__ == '__main__':
    main()
