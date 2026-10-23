"""Build-only exact-byte frame deduplication; logical frames and offsets stay intact."""
import hashlib
import json
from pathlib import Path
import shutil


def asset_plan(source):
    source = Path(source)
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    files = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
    files.pop('manifest.json')
    for name, clip in manifest['clips'].items():
        seen, indices = {}, []
        for index in range(clip['frames']):
            relative = f'{name}/{index:04}.{manifest["format"]}'
            data = files[relative].read_bytes()
            digest = hashlib.sha256(data).digest()
            canonical = seen.setdefault(digest, index)
            if canonical != index:
                # A hash match alone is not the content-equality contract.
                assert data == files[f'{name}/{canonical:04}.{manifest["format"]}'].read_bytes()
                del files[relative]
            indices.append(canonical)
        clip['frame_indices'] = indices
    return (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8'), files


def pack_assets(source, build_root):
    data, files = asset_plan(source)
    # Content-addressed build output; never remove unknown or earlier build data.
    identity = hashlib.sha256(data + b''.join(hashlib.sha256(p.read_bytes()).digest()
                                            for _, p in sorted(files.items()))).hexdigest()
    target = Path(build_root) / identity
    expected = set(files) | {'manifest.json'}
    if target.exists():
        assert {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()} == expected
        assert (target / 'manifest.json').read_bytes() == data
        assert all((target / n).read_bytes() == p.read_bytes() for n, p in files.items())
        return target
    target.mkdir(parents=True)
    for name, path in files.items():
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    (target / 'manifest.json').write_bytes(data)
    return target
