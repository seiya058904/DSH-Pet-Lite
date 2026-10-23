"""Lossless package aliases must preserve every logical Qt image and recovery state."""
import json
import os
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from app import Pet
from edition import assets_for
from pack_assets import pack_assets

EDITION = os.environ.get('DSH_TEST_EDITION', 'core')


def test_pack_preserves_all_logical_pixels_offsets_and_timing(tmp_path):
    source = assets_for(EDITION)
    packed = pack_assets(source, tmp_path / 'packed')
    assert pack_assets(source, tmp_path / 'packed') == packed
    original = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    manifest = json.loads((packed / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['fps'] == original['fps'] == 24
    assert manifest['size'] == original['size']
    total = 0
    for name, clip in manifest['clips'].items():
        indices = clip.pop('frame_indices')
        assert clip == original['clips'][name]
        assert len(indices) == clip['frames'] == len(clip['offsets'])
        for index, physical in enumerate(indices):
            before = QImage(str(source / name / f'{index:04}.webp'))
            after = QImage(str(packed / name / f'{physical:04}.webp'))
            assert not before.isNull() and before.size() == after.size()
            for fmt in (QImage.Format.Format_RGBA8888, QImage.Format.Format_ARGB32_Premultiplied):
                a, b = before.convertToFormat(fmt), after.convertToFormat(fmt)
                assert bytes(a.constBits()) == bytes(b.constBits()), (name, index, fmt)
            total += 1
    assert total == (2651 if EDITION == 'core' else 723)


def test_alias_keeps_logical_state_on_missing_frame(tmp_path):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    packed = pack_assets(assets_for(EDITION), tmp_path / 'packed')
    pet = Pet(tmp_path / 'settings.json', edition=EDITION, assets=packed, mode='hidden', seed=42)
    try:
        indices = pet.frame_indices['idle']
        logical = next(i for i, physical in enumerate(indices) if i != physical)
        pet.index = logical
        pet.load_frame()
        assert pet.last_valid_frame == ('idle', logical)
        before = bytes(pet.image.constBits())
        pet.assets = tmp_path / 'missing'
        pet.play('click')
        assert pet.paused and not pet.timer.isActive()
        assert (pet.clip, pet.index) == ('idle', logical)
        assert bytes(pet.image.constBits()) == before
    finally:
        pet.shutdown()
        pet.deleteLater()
