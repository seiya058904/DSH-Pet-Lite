"""Code-only CI fixtures: synthetic rectangles, never downloaded character art.

This opt-in fixture tests software behavior only. It cannot pass asset parity or
the release bundle gate and is never used by the local real-asset build command.
"""
import json
import os
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture(scope='session', autouse=True)
def synthetic_assets_for_code_only_ci(tmp_path_factory):
    if os.environ.get('DSH_SYNTHETIC_TEST_ASSETS') != '1':
        yield
        return
    from PIL import Image, ImageDraw
    import edition
    original = edition.ROOT
    root = tmp_path_factory.mktemp('synthetic-assets')
    full = {f'action_{i:03}': 'random' for i in range(106)}
    for i in range(5):
        full[f'action_{i:03}'] = 'click'
    full['click'] = full.pop('action_000')
    full['idle'] = full.pop('action_010')
    full['idle'] = 'idle'
    full['drag'] = full.pop('action_011')
    full['drag'] = 'drag'
    for i in (13, 14, 15):
        full[f'action_{i:03}'] = 'move'
    full['action_105'] = 'turn'
    for selected, names in [('full', full), ('ultra', dict(idle='idle', click='click', drag='drag'))]:
        assets = root/('assets' if selected == 'full' else 'assets-ultra')
        assets.mkdir()
        clips = {}
        for name, category in names.items():
            directory = assets/name
            directory.mkdir()
            frames = 241
            image = Image.new('RGBA', (10, 10))
            ImageDraw.Draw(image).rectangle((2, 2, 7, 7), fill=(40, 90, 180, 255))
            for i in range(frames):
                image.save(directory/f'{i:04}.webp', lossless=True)
            clips[name] = {'category': category, 'frames': frames, 'label': name,
                           'offsets': [[0, 0]]*frames}
        manifest = {'size': [461, 259] if selected == 'full' else [201, 248],
                    'fps': 24, 'format': 'webp', 'scale': .72, 'clips': clips}
        (assets/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        if selected == 'full':
            curves = {name: {'stride': 240, 'curve': [0]*51+[min(1, (i-50)/60) for i in range(51, 241)]}
                      for name, category in names.items() if category == 'move'}
            (assets/'move_strides.json').write_text(json.dumps(curves), encoding='utf-8')
    edition.ROOT = root
    yield
    edition.ROOT = original
