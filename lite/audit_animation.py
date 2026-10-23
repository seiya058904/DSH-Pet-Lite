"""Verify each logical Full frame against the pinned official resize and crop.

Ultra hashes are compared with the historical git object, not the Full resize.
This proves stored pixels, not compositor presentation or behavioral parity.
"""
import hashlib
import io
import json
import subprocess
import tarfile
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT/'benchmarks/public'
    output.mkdir(parents=True, exist_ok=True)
    results = {}
    failed = []
    for edition in ('full', 'ultra'):
        assets = ROOT/'lite'/('assets' if edition == 'full' else 'assets-ultra')
        m = json.loads((assets/'manifest.json').read_text(encoding='utf-8'))
        rows = []
        old = {}
        if edition == 'ultra':
            archive = tarfile.open(fileobj=io.BytesIO(subprocess.check_output(
                ['git', 'archive', '863353c5', 'lite/assets'], cwd=ROOT)))
            old = {str(Path(item.name).relative_to('lite/assets')).replace('\\', '/'):
                   hashlib.sha256(archive.extractfile(item).read()).hexdigest()
                   for item in archive.getmembers() if item.isfile()}
        for name, clip in m['clips'].items():
            failures = []
            h = hashlib.sha256()
            official = ROOT/'benchmarks/upstream/full-packs/frames/anim'/clip.get('category', name)/clip.get('label', '')
            if edition == 'full':
                candidates = list((ROOT/'benchmarks/upstream/full-packs/frames/anim').rglob('meta.json')) if not official.exists() else []
                if candidates:
                    official = next(p.parent for p in candidates if p.parent.name == clip['label'])
                source_frames = sorted(official.glob('f_*.webp'))
                assert len(source_frames) == clip['frames']
            for i in range(clip['frames']):
                path = assets/name/f'{i:04}.webp'
                h.update(path.read_bytes())
                with Image.open(path) as frame:
                    pixels = frame.convert('RGBA')
                    if edition == 'full':
                        with Image.open(source_frames[i]) as source:
                            scaled = source.convert('RGBA').resize(tuple(m['size']), Image.Resampling.LANCZOS)
                        x, y = clip['offsets'][i]
                        expected = scaled.crop((x, y, x+pixels.width, y+pixels.height))
                        if expected.tobytes() != pixels.tobytes():
                            failures.append(i)
                    elif digest(path) != old[f'{name}/{i:04}.webp']:
                        failures.append(i)
            rows.append({'id': name, 'category': clip.get('category', name),
                         'source': clip['source']['source'], 'frames': clip['frames'],
                         'fps': m['fps'], 'duration_s': clip['frames']/m['fps'],
                         'encoded_frames_sha256': h.hexdigest(),
                         'pixel_or_historical_hash_failures': failures,
                         'status': 'FAIL' if failures else 'PASS',
                         'trigger': 'menu; pointer drag while held' if name == 'drag' else
                                    'menu; click' if clip.get('category', name) == 'click' else
                                    'menu; local animation scheduler'})
            failed.extend((edition, name, i) for i in failures)
            print(edition, name, rows[-1]['status'], flush=True)
        report = {'edition': edition, 'upstream': m['upstream'], 'clips': len(rows),
                  'frames': sum(row['frames'] for row in rows),
                  'categories': dict(Counter(row['category'] for row in rows)),
                  'manifest_sha256': digest(assets/'manifest.json'), 'animations': rows,
                  'scope': 'Stored pixels at supported 72% size; not physical display presentation'}
        (output/f'{edition}-animation-manifest.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        results[edition] = {k:v for k,v in report.items() if k != 'animations'}
    (output/'animation-parity.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    assert not failed, failed


if __name__ == '__main__':
    main()
