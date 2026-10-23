"""Fail on forbidden modules/resources or dangling imports of pruned Qt DLLs."""
import json
import argparse
import hashlib
import os
from pathlib import Path
from edition import EDITIONS, assets_for, profile
from pack_assets import asset_plan

import pefile
from PyInstaller.archive.readers import CArchiveReader

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--edition', choices=EDITIONS, required=True)
parser.add_argument('--dist', type=Path, default=root / 'dist/core-ultra')
args = parser.parse_args()
product = profile(args.edition)['product']
bundle = args.dist / product
forbidden = ('pet', 'numpy', 'cv2', 'rapidocr', 'onnxruntime', 'edge_tts', 'keyring',
             'winrt', 'psutil', 'PIL', 'imageio_ffmpeg')
archive = CArchiveReader(str(bundle / f'{product}.exe')).open_embedded_archive('PYZ.pyz')
modules = sorted(archive.toc)
bad = [m for m in modules if any(m == x or m.startswith(x+'.') for x in forbidden)]
assert not bad, bad
if args.edition == 'ultra':
    assert 'roaming' not in modules
identity = json.loads((bundle / '_internal/build-info.json').read_text())
assert identity['edition'] == args.edition
source_assets = assets_for(args.edition)
bundled_assets = bundle / '_internal/assets'
manifest_bytes, expected = asset_plan(source_assets)
actual = {p.relative_to(bundled_assets).as_posix(): p for p in bundled_assets.rglob('*') if p.is_file()}
assert actual.keys() == expected.keys() | {'manifest.json'}, 'Resource closure mismatch'
assert actual['manifest.json'].read_bytes() == manifest_bytes
assert hashlib.sha256(manifest_bytes).hexdigest() == identity['manifest_sha256']
for name, path in expected.items():
    assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(actual[name].read_bytes()).digest(), name
manifest = json.loads((bundled_assets / 'manifest.json').read_text(encoding='utf-8'))
assert len(manifest['clips']) == (11 if args.edition == 'core' else 3)
assert sum(c['frames'] for c in manifest['clips'].values()) == (2651 if args.edition == 'core' else 723)
assert manifest['fps'] == 24
if args.edition == 'core':
    assert sorted(c['category'] for c in manifest['clips'].values()) == sorted(
        ['idle', 'drag', 'turn'] + ['click']*5 + ['move']*3)
files = list(bundle.rglob('*'))
assert not [p for p in files if p.is_file() and (p.suffix.lower() in ('.onnx', '.webm', '.mp3')
                                               or 'ffmpeg' in p.name.lower())]
names = {p.name.lower() for p in files if p.is_file()}
assert '_hashlib.pyd' not in names and 'libcrypto-3.dll' not in names
pe_imports = {}
all_pe_imports = {}
system32 = Path(os.environ['SystemRoot']) / 'System32'
for path in files:
    if path.suffix.lower() in ('.dll', '.pyd', '.exe'):
        pe = pefile.PE(str(path), fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                                              pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT']])
        imports = [e.dll.decode() for e in [*getattr(pe, 'DIRECTORY_ENTRY_IMPORT', []),
                                           *getattr(pe, 'DIRECTORY_ENTRY_DELAY_IMPORT', [])]]
        qt = [name for name in imports if name.lower().startswith('qt6')]
        assert all(name.lower() in names for name in qt), (path, qt)
        unresolved = [name for name in imports if name.lower() not in names
                      and not name.lower().startswith(('api-ms-', 'ext-ms-'))
                      and not (system32 / name).is_file()]
        assert not unresolved, (path, unresolved)
        pe_imports[str(path.relative_to(bundle))] = qt
        all_pe_imports[str(path.relative_to(bundle))] = imports
        pe.close()
for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'licenses/LGPL-3.0-only.txt',
             'licenses/Python-LICENSE.txt', 'licenses/LITE-NOTICES.md',
             'licenses/libwebp/COPYING', 'licenses/libwebp/PATENTS',
             'assets/manifest.json'):
    assert (bundle / '_internal' / name).is_file(), name
result = {'edition': args.edition, 'identity': identity, 'modules': modules, 'qt_imports': pe_imports,
          'all_pe_imports': all_pe_imports, 'pe_closure': 'bundled DLLs or Windows System32/API sets',
          'asset_files_sha256': {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in actual.items()},
          'file_manifest': [{'path': p.relative_to(bundle).as_posix(), 'bytes': p.stat().st_size,
                             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                            for p in files if p.is_file()],
          'files': len([p for p in files if p.is_file()]),
          'bytes': sum(p.stat().st_size for p in files if p.is_file()),
          'forbidden_modules': bad}
(root / 'build').mkdir(exist_ok=True)
(root / f'build/verified-{args.edition}-bundle.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k: result[k] for k in ('files', 'bytes', 'forbidden_modules')}))
