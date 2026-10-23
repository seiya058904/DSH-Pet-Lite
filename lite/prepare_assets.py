"""Build-only full official white-v6 library, lossless at the normal .72 scale."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'benchmarks/upstream/full-packs/frames/anim'
OUTPUT = ROOT / 'lite/assets'


def convert(item):
    name, directory = item
    meta = json.loads((directory / 'meta.json').read_text(encoding='utf-8'))
    assert meta['encoder'] == 'libwebp lossless (bgra straight, unblend-white-v6)'
    frames = sorted(directory.glob('f_*.webp'))
    assert len(frames) == meta['frames']
    out = OUTPUT / name
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    offsets = []
    for index, path in enumerate(frames):
        digest.update(path.read_bytes())
        with Image.open(path) as image:
            result = image.convert('RGBA').resize((461, 259), Image.Resampling.LANCZOS)
            box = result.getchannel('A').getbbox() or (0, 0, 1, 1)
            offsets.append(box[:2])
            result.crop(box).save(out / f'{index:04}.webp', 'WEBP', lossless=True, exact=True, method=2)
    print(name, directory.name, len(frames), flush=True)
    return name, {'frames': len(frames), 'source': meta, 'label': directory.name,
                  'category': directory.relative_to(SOURCE).parts[0],
                  'official_frames_sha256': digest.hexdigest(), 'offsets': offsets}


def main():
    directories = sorted(p.parent for p in SOURCE.rglob('meta.json'))
    assert len(directories) == 106, len(directories)
    items = []
    for i, directory in enumerate(directories):
        category = directory.relative_to(SOURCE).parts[0]
        name = {'idle': 'idle', 'drag': 'drag'}.get(category, f'action_{i:03}')
        if directory.name == '点击回应-开心跃动':
            name = 'click'
        items.append((name, directory))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        clips = dict(pool.map(convert, items))
    manifest = {'upstream': '59c8bda3d1078155564267fbcb34fff9d2d80aff',
                'size': [461, 259], 'scale': .72, 'fps': 24, 'format': 'webp', 'clips': clips}
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
