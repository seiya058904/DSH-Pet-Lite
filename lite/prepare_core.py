"""Rebuild Core from the pinned official core ZIP; no automatic downloading."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'assets-core')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    reference = json.loads((ROOT/'core-source-map.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(args.source.read_bytes()).hexdigest() == reference['core_zip_sha256']
    manifest = json.loads((ROOT/'assets-core/manifest.json').read_text(encoding='utf-8'))
    rows = []
    with ZipFile(args.source) as archive:
        metas = [n for n in archive.namelist() if n.startswith('anim/') and n.endswith('/meta.json')]
        assert len(metas) == 11
        for name in metas:
            meta = json.loads(archive.read(name))
            ref = reference['clips'][meta['source_sha256']]
            clip = manifest['clips'][ref['id']]
            assert meta['fps'] == 24 and meta['frames'] == ref['frames'] == 241
            paths = sorted(n for n in archive.namelist() if n.startswith(name[:-9]) and n.endswith('.webp'))
            assert len(paths) == 241
            source_digest = hashlib.sha256()
            for index, frame in enumerate(paths):
                raw = archive.read(frame)
                source_digest.update(raw)
                with Image.open(io.BytesIO(raw)) as image:
                    scaled = image.convert('RGBA').resize((461, 259), Image.Resampling.LANCZOS)
                box = scaled.getchannel('A').getbbox() or (0, 0, 1, 1)
                expected = scaled.crop(box)
                target = args.output/ref['id']/f'{index:04}.webp'
                assert list(box[:2]) == clip['offsets'][index]
                if not args.verify_only:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    expected.save(target, 'WEBP', lossless=True, exact=True, method=2)
                with Image.open(target) as actual:
                    assert actual.convert('RGBA').tobytes() == expected.tobytes(), (ref['id'], index)
                    assert actual.size == expected.size
            assert source_digest.hexdigest() == ref['official_frames_sha256']
            rows.append({**ref, 'fps': 24, 'normalized_rgba_and_complete_alpha': 'PASS',
                         'trigger': 'menu plus '+ref['category']+' interaction/scheduling'})
    if not args.verify_only:
        for name in ['manifest.json', 'move_strides.json', 'lite.ico']:
            source = ROOT/'assets-core'/name
            destination = args.output/name
            if source.resolve() != destination.resolve():
                destination.write_bytes(source.read_bytes())
    report = {'official_core_zip_sha256': reference['core_zip_sha256'], 'clips': rows,
              'total_clips': len(rows), 'total_frames': sum(r['frames'] for r in rows),
              'normalization': '461x259 at inherited 72% scale; Lanczos, complete alpha crop; RGBA equality',
              'status': 'PASS'}
    destination = ROOT.parent/'benchmarks/public/core-animation-manifest.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'clips': len(rows), 'frames': 2651, 'status': 'PASS'}))


if __name__ == '__main__':
    main()
