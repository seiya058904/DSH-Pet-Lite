import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import Pet, read_config, save_config
from edition import assets_for
import pytest

EDITION = os.environ.get('DSH_TEST_EDITION', 'full')


def events(ms=100):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def test_config_roundtrip_and_corrupt(tmp_path):
    path = tmp_path / 'settings.json'
    assert read_config(path) == {}
    save_config(path, {'x': -15, 'y': 24, 'paused': True})
    assert read_config(path) == {'x': -15, 'y': 24, 'paused': True}
    path.write_text('{broken', encoding='utf-8')
    assert read_config(path) == {}
    assert path.read_text() == '{broken'
    path.write_text(json.dumps({'x': 'bad', 'y': None, 'paused': 1}))
    assert read_config(path) == {}


def test_lifecycle_frames_pause_hide_restore(tmp_path):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    pet = Pet(tmp_path / 'settings.json', edition=EDITION)
    try:
        events(180)
        assert pet.isVisible() and pet.index > 0
        pet.set_paused(True)
        stopped = pet.index
        events()
        assert not pet.timer.isActive() and pet.index == stopped
        pet.set_paused(False)
        events()
        assert pet.index > stopped
        pet.hide()
        stopped = pet.index
        events()
        assert not pet.timer.isActive() and pet.index == stopped
        assert not pet.cache and pet.cache_bytes == 0
        pet.show_pet()
        pet.play('click')
        pet.index = pet.manifest['clips']['click']['frames']-1
        pet.advance()
        assert pet.clip == 'idle' and pet.index == 0
        assert pet.cache_bytes <= pet.cache_limit
        assert pet.width() < 500 and pet.height() < 500
        pet.move(-10000, -10000)
        pet.ensure_on_screen()
        assert any(s.availableGeometry().contains(pet.frameGeometry().center()) for s in app.screens())
        pet.save()
        assert read_config(tmp_path / 'settings.json')['x'] == pet.x()
        assert not any(m == 'pet' or m.startswith('pet.') for m in sys.modules)
    finally:
        pet.shutdown()
        pet.deleteLater()
        events()


def test_all_frames_valid_alpha_and_budget():
    from PIL import Image
    root = assets_for(EDITION)
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    for name, meta in manifest['clips'].items():
        assert meta['frames'] == len(meta['offsets'])
        count = 0
        total = 0
        for path in sorted((root / name).glob('*.'+manifest['format'])):
            with Image.open(path) as image:
                assert image.mode == 'RGBA'
                assert image.getchannel('A').getextrema() == (0, 255)
                total += image.width*image.height*4
                x, y = meta['offsets'][count]
                assert 0 <= x and x + image.width <= manifest['size'][0]
                assert 0 <= y and y + image.height <= manifest['size'][1]
            count += 1
        assert count == meta['frames']
        if name == 'idle':
            assert total < 40*1024*1024


def test_click_and_drag_from_public_events(tmp_path):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    pet = Pet(tmp_path / 'settings.json', edition=EDITION)
    try:
        pet.move(100, 100)
        QTest.mouseClick(pet, Qt.MouseButton.LeftButton, pos=QPoint(80, 100))
        assert pet.clip in pet.click_clips
        QTest.mousePress(pet, Qt.MouseButton.LeftButton, pos=QPoint(80, 100))
        QTest.mouseMove(pet, QPoint(130, 140))
        assert pet.dragged and pet.clip == 'drag'
        QTest.mouseRelease(pet, Qt.MouseButton.LeftButton, pos=QPoint(130, 140))
        assert pet.clip == 'idle' and pet.drag_origin is None
        assert read_config(tmp_path / 'settings.json')['x'] == pet.x()
    finally:
        pet.shutdown()
        pet.deleteLater()
        events()


def test_full_library_menu_and_one_shot_lifecycle(tmp_path):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    pet = Pet(tmp_path / 'settings.json', edition=EDITION, seed=42)
    try:
        assert len(pet.manifest['clips']) == (106 if EDITION == 'full' else 3)
        assert len(pet.click_clips) == (5 if EDITION == 'full' else 1)
        assert len(pet.animation_actions) == len(pet.manifest['clips'])
        assert (len(pet.activity_clips) > 80) if EDITION == 'full' else not pet.activity_clips
        for name in pet.manifest['clips']:
            pet.animation_actions[name].trigger()
            if pet.roaming and pet.roaming.pending:
                pet.index = pet.manifest['clips'][pet.clip]['frames']-1
                pet.advance()
            assert pet.clip == name and not pet.image.isNull()
            pet.index = pet.manifest['clips'][pet.clip]['frames']-1
            pet.advance()
            assert pet.clip in ['idle', *pet.activity_clips] if name == 'idle' else pet.clip == 'idle'
            assert pet.cache_bytes <= pet.cache_limit
        pet.hide()
        assert not pet.timer.isActive() and pet.cache_bytes == 0
    finally:
        pet.shutdown()
        pet.deleteLater()
        events()


def test_edition_is_required_and_ultra_rejects_full_assets(tmp_path):
    QApplication.instance() or QApplication([])
    with pytest.raises(ValueError, match='exactly'):
        Pet(tmp_path / 'settings.json', edition='ultra', assets=assets_for('full'))


def test_missing_action_preserves_last_frame_and_stops(tmp_path):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    pet = Pet(tmp_path/'settings.json', edition=EDITION, seed=42)
    try:
        image_key = pet.image.cacheKey()
        real_assets = pet.assets
        pet.assets = tmp_path
        pet.play('action_014' if pet.roaming else 'click')
        assert pet.resource_error and pet.paused and not pet.timer.isActive()
        assert pet.image.cacheKey() == image_key and pet.clip == 'idle'
        if pet.roaming:
            assert pet.roaming.plan is None and pet.roaming.pending is None
        pet.assets = real_assets
        pet.set_paused(False)
        pet.advance()
        assert pet.clip == 'idle' and pet.timer.isActive()
    finally:
        pet.shutdown()
        pet.deleteLater()
        events()


@pytest.mark.skipif(EDITION != 'full', reason='Ultra deliberately excludes roaming')
def test_roaming_curve_turn_and_interruption(tmp_path):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    pet = Pet(tmp_path / 'settings.json', edition='full', seed=42)
    try:
        g = app.primaryScreen().availableGeometry()
        pet.move(g.left()+250, g.top()+50)
        pet.play('action_013')
        before = pet.x()
        pet.index = 10
        pet.roaming.advance()
        assert pet.x() == before  # Source curve has a stationary lead-in.
        pet.index = 140
        pet.roaming.advance()
        assert pet.x() < before
        pet.play('click')
        assert pet.roaming.plan is None and pet.roaming.pending is None
        pet.move(g.left(), g.top()+50)
        pet.play('action_013')
        assert pet.clip == 'action_105' and pet.roaming.pending == 'action_013'
        pet.index = pet.manifest['clips'][pet.clip]['frames']-1
        pet.advance()
        assert pet.clip == 'action_013' and pet.roaming.facing == 1
        pet.index = 140
        pet.roaming.advance()
        assert pet.x() > g.left() and g.contains(pet.frameGeometry())
        pet.hide()
        assert not pet.timer.isActive()
    finally:
        pet.shutdown()
        pet.deleteLater()
        events()
