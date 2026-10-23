"""Bounded, lossless build-only experiments; never substitutes for binary metrics."""
import hashlib
import io
import json
import statistics
import time
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile
from PIL import Image
from PySide6.QtGui import QImage
from edition import assets_for

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT/'build/dual-experiments'
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for edition in ('full', 'ultra'):
        assets = assets_for(edition)
        m = json.loads((assets/'manifest.json').read_text(encoding='utf-8'))
        paths = [assets/n/f'{c["frames"]//2:04}.webp' for n,c in m['clips'].items()]
        if edition == 'ultra':
            paths = [assets/n/f'{i:04}.webp' for n in m['clips'] for i in (0, 60, 120, 180, 240)]
        encoded = []
        started = time.perf_counter()
        for path in paths:
            with Image.open(path) as image:
                rgba = image.convert('RGBA')
                data = io.BytesIO()
                rgba.save(data, format='WEBP', lossless=True, exact=True, method=6)
                restored = Image.open(io.BytesIO(data.getvalue())).convert('RGBA')
                assert restored.tobytes() == rgba.tobytes()
                encoded.append(len(data.getvalue()))
        original = sum(p.stat().st_size for p in paths)
        codec = {'sample_frames': len(paths), 'original_bytes': original,
                 'method6_bytes': sum(encoded), 'savings_pct': 100*(1-sum(encoded)/original),
                 'encode_seconds': time.perf_counter()-started, 'pixel_equal': True}
        archive_path = out/f'{edition}-sample.zip'
        with ZipFile(archive_path, 'w', ZIP_STORED) as archive:
            for i, path in enumerate(paths):
                archive.writestr(str(i), path.read_bytes())
        file_times, archive_times = [], []
        for repeat in range(5):
            for kind in (('files', 'archive') if repeat % 2 == 0 else ('archive', 'files')):
                start = time.perf_counter()
                if kind == 'archive':
                    with ZipFile(archive_path) as archive:
                        for i in range(len(paths)):
                            assert not QImage.fromData(archive.read(str(i))).isNull()
                    archive_times.append(time.perf_counter()-start)
                else:
                    for path in paths:
                        assert not QImage(str(path)).isNull()
                    file_times.append(time.perf_counter()-start)
        cache = []
        idle = [assets/'idle'/f'{i:04}.webp' for i in range(m['clips']['idle']['frames'])]
        for budget in (40, 16, 0):
            times = []
            for _ in range(3):
                images, size, decodes = {}, 0, 0
                start = time.perf_counter()
                for _loop in range(3):
                    for path in idle:
                        if path not in images:
                            image = QImage(str(path)).convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
                            decodes += 1
                            if size+image.sizeInBytes() <= budget*1024*1024:
                                images[path] = image
                                size += image.sizeInBytes()
                times.append(time.perf_counter()-start)
            cache.append({'limit_MiB': budget, 'cached_bytes': size, 'decodes': decodes, 'seconds': times})
        results[edition] = {'webp_method6': codec, 'stored_container': {'files_seconds': file_times,
                            'archive_seconds': archive_times, 'median_files': statistics.median(file_times),
                            'median_archive': statistics.median(archive_times)}, 'idle_cache': cache,
                            'manifest_sha256': hashlib.sha256((assets/'manifest.json').read_bytes()).hexdigest(),
                            'scope': 'Build-only warm-file-cache microbenchmark; not independent installed performance'}
        print(edition, json.dumps(results[edition]), flush=True)
    (ROOT/'benchmarks/public/optimization-probes.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
