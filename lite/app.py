"""Windows-only, offline, single-pet Qt Lite. No imports from upstream pet/."""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

from PySide6.QtCore import QElapsedTimer, QLockFile, Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QImage, QPainter
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QWidget

from edition import EDITIONS, assets_for, build_identity, profile

ASSETS = Path(__file__).resolve().parent / 'assets'
CONFIG_DIR = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'DSH-Pet-Lite'


def read_config(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return {k: data[k] for k in ('x', 'y', 'paused') if k in data and
                (type(data[k]) is bool if k == 'paused' else type(data[k]) is int)}
    except (OSError, ValueError, TypeError):
        return {}


def save_config(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data), encoding='utf-8')
    os.replace(temp, path)


class Pet(QWidget):
    def __init__(self, config_path, *, edition, assets=None, identity=None, mode='animated', ready_file=None, test_control=False, metrics_file=None, seed=None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.profile = profile(edition)
        self.edition = edition
        self.assets = Path(assets) if assets else assets_for(edition)
        self.identity = identity or {'source_sha': 'source checkout', **self.profile}
        self.rng = random.Random(seed)
        self.setWindowTitle(self.profile['title'])
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.config_path = Path(config_path)
        self.config = read_config(self.config_path)
        self.manifest = json.loads((self.assets / 'manifest.json').read_text(encoding='utf-8'))
        if edition == 'ultra' and set(self.manifest['clips']) != {'idle', 'click', 'drag'}:
            raise ValueError('Ultra must contain exactly idle, click and drag')
        self.resize(*self.manifest['size'])
        self.setAccessibleName('DSH Pet Lite 桌宠：拖动移动，点击互动，右键菜单')
        self.clip = 'idle'
        self.index = 0
        self.click_clips = [n for n, c in self.manifest['clips'].items()
                            if c.get('category', n) == 'click']
        self.activity_clips = [n for n, c in self.manifest['clips'].items()
                               if c.get('category') in ('random', 'move', 'turn')]
        self.roaming = None
        if edition == 'full':
            from roaming import Roaming
            self.roaming = Roaming(self)
        self.cache = {}
        self.cache_bytes = 0
        self.cache_limit = 40 * 1024 * 1024
        self.resource_error = None
        self.image = QImage()
        self.paused = bool(self.config.get('paused', False)) or mode == 'paused'
        self.drag_origin = None
        self.dragged = False
        self.ready_file = ready_file
        self.ready_written = False
        self.test_control = test_control
        self.metrics_file = metrics_file
        self.paint_times = [] if metrics_file else None
        self.frame_count = 0
        self.clock = QElapsedTimer()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.advance)
        self.clock.start()
        self.next_frame = 1000 / self.manifest['fps']
        self.menu = QMenu(self)
        self.show_action = self.menu.addAction('显示 / Show', self.show_pet)
        self.hide_action = self.menu.addAction('隐藏 / Hide', self.hide)
        self.pause_action = QAction('暂停动画 / Pause', self, checkable=True)
        self.pause_action.setChecked(self.paused)
        self.pause_action.triggered.connect(self.set_paused)
        self.menu.addAction(self.pause_action)
        library = self.menu.addMenu('全部动画')
        groups = {}
        labels = {'idle': '待机', 'click': '点击反馈', 'drag': '拖拽',
                  'move': '移动动作', 'turn': '转身', 'random': '日常动作', 'events': '情景动作'}
        self.animation_actions = {}
        for name, clip in self.manifest['clips'].items():
            category = clip.get('category', name)
            if category not in groups:
                groups[category] = library.addMenu(labels.get(category, category))
            self.animation_actions[name] = groups[category].addAction(
                clip.get('label', name), lambda checked=False, n=name: self.select_animation(n))
        self.menu.addSeparator()
        self.menu.addAction('关于 / About', self.about)
        self.menu.addAction('退出 / Exit', QApplication.instance().quit)
        icon = QIcon(str(self.assets / 'lite.ico'))
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip(f"{self.profile['title']} {self.profile['version']} · {self.identity['source_sha'][:12]}")
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()
        self.load_frame()
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(self.config.get('x', screen.right()-self.width()-60),
                  self.config.get('y', screen.bottom()-self.height()-50))
        self.ensure_on_screen()
        QApplication.instance().screenRemoved.connect(lambda _s: self.ensure_on_screen())
        if mode != 'hidden':
            self.show_pet()

    def ensure_on_screen(self):
        rect = self.frameGeometry()
        for screen in QApplication.screens():
            if screen.availableGeometry().contains(rect.center()):
                return
        g = QApplication.primaryScreen().availableGeometry()
        self.move(max(g.left(), min(self.x(), g.right()-self.width())),
                  max(g.top(), min(self.y(), g.bottom()-self.height())))

    def load_frame(self):
        key = (self.clip, self.index)
        image = self.cache.get(key)
        if image is None:
            image = QImage(str(self.assets / self.clip / f'{self.index:04}.{self.manifest["format"]}'))
            if image.isNull():
                self.resource_error = f'Missing or invalid animation frame: {key}'
                self.paused = True
                self.pause_action.setChecked(True)
                self.timer.stop()
                self.tray.showMessage(self.profile['title'], self.resource_error)
                # Keep the last valid image and its original offsets for safe recovery.
                if self.image.isNull():
                    raise RuntimeError(self.resource_error)
                self.clip, self.index = self.last_valid_frame
                if self.roaming:
                    self.roaming.plan = None
                    self.roaming.pending = None
                    self.roaming.flip_after_turn = False
                return
            image = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
            # Cache the short idle loop only; action frames are transient, never unbounded.
            if self.clip == 'idle' and self.cache_bytes + image.sizeInBytes() <= self.cache_limit:
                self.cache[key] = image
                self.cache_bytes += image.sizeInBytes()
        self.image = image
        self.last_valid_frame = key

    def arm(self):
        if self.isVisible() and not self.paused:
            self.timer.start(max(1, round(self.next_frame-self.clock.elapsed())))

    def advance(self):
        if self.paused or not self.isVisible():
            return
        self.index += 1
        if self.index >= self.manifest['clips'][self.clip]['frames']:
            self.index = 0
            if self.roaming and (self.clip != 'drag' or self.drag_origin is None):
                self.clip = self.roaming.completed(self.clip)
            elif self.clip != 'drag' or self.drag_origin is None:
                self.clip = 'idle'
        if self.roaming:
            self.roaming.advance()
        self.load_frame()
        self.update()
        self.next_frame += 1000 / self.manifest['fps']
        # No catch-up burst after suspend or a delayed event loop.
        if self.next_frame < self.clock.elapsed():
            self.next_frame = self.clock.elapsed() + 1000 / self.manifest['fps']
        self.arm()

    def play(self, name):
        if self.roaming:
            name = self.roaming.prepare(name)
        self.clip, self.index = name, 0
        self.load_frame()
        self.update()
        self.next_frame = self.clock.elapsed() + 1000 / self.manifest['fps']
        self.arm()

    def select_animation(self, name):
        self.show_pet()
        self.set_paused(False)
        self.play(name)

    def set_paused(self, paused):
        self.paused = bool(paused)
        self.pause_action.setChecked(self.paused)
        self.timer.stop()
        if not self.paused:
            self.next_frame = self.clock.elapsed() + 1000 / self.manifest['fps']
            self.arm()
        self.save()

    def show_pet(self):
        self.ensure_on_screen()
        self.show()
        self.next_frame = self.clock.elapsed() + 1000 / self.manifest['fps']
        self.arm()

    def hideEvent(self, event):
        self.timer.stop()
        self.cache.clear()
        self.cache_bytes = 0
        super().hideEvent(event)

    def paintEvent(self, _event):
        painter = QPainter(self)
        if self.roaming and self.roaming.facing > 0:
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)
        x, y = self.manifest['clips'][self.clip]['offsets'][self.index]
        painter.drawImage(x, y, self.image)
        painter.end()
        self.frame_count += 1
        if self.paint_times is not None and len(self.paint_times) < 60000:
            self.paint_times.append(time.perf_counter())
        if self.ready_file and not self.ready_written:
            Path(self.ready_file).write_text(json.dumps({'pid': os.getpid(),
                'paint_monotonic': time.perf_counter(), 'geometry': self.geometry().getRect(),
                'dpr': self.devicePixelRatioF()}), encoding='utf-8')
            self.ready_written = True

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_origin = event.globalPosition().toPoint()-self.pos()
            self.press_position = event.globalPosition().toPoint()
            self.dragged = False

    def mouseMoveEvent(self, event):
        if self.drag_origin is not None:
            if (event.globalPosition().toPoint()-self.press_position).manhattanLength() >= QApplication.startDragDistance():
                if not self.dragged:
                    self.dragged = True
                    self.play('drag')
                self.move(event.globalPosition().toPoint()-self.drag_origin)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_origin is not None:
            self.drag_origin = None
            self.ensure_on_screen()
            self.play('idle' if self.dragged else self.rng.choice(self.click_clips))
            self.save()

    def contextMenuEvent(self, event):
        self.menu.popup(event.globalPos())

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_pet()

    def save(self):
        try:
            save_config(self.config_path, {'x': self.x(), 'y': self.y(), 'paused': self.paused})
        except OSError as exc:
            self.tray.showMessage('DSH Pet Lite', f'设置未保存 / Settings not saved: {type(exc).__name__}')

    def about(self):
        QMessageBox.about(self, self.profile['title'],
            f"{self.profile['title']} {self.profile['version']}\n"
            f"Build: {self.identity['source_sha']}\n"
            "Unofficial derivative. Non-commercial character assets. Attribution required.\n"
            "Character: 溟月 / 上善无形; community animation.\n"
            "https://github.com/MerZlin/dsh-pet-indesktop\n"
            "https://github.com/PC2005-cloud/dsh-pet")

    def shutdown(self):
        self.timer.stop()
        self.save()
        self.tray.hide()
        if self.metrics_file:
            Path(self.metrics_file).write_text(json.dumps({'paint_times': self.paint_times,
                'frames': self.frame_count, 'cache_bytes': self.cache_bytes}), encoding='utf-8')
        self.close()

    def nativeEvent(self, event_type, message):
        if self.test_control:
            from ctypes import wintypes
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x8000 + 77:
                actions = {1: lambda: self.set_paused(True), 2: lambda: self.set_paused(False),
                           3: self.hide, 4: self.show_pet, 5: QApplication.instance().quit,
                           6: self.write_test_state,
                           7: lambda: self.select_animation(list(self.manifest['clips'])[msg.lParam])
                           if 0 <= msg.lParam < len(self.manifest['clips']) else None}
                action = actions.get(msg.wParam)
                if action:
                    action()
                    return True, 0
        return super().nativeEvent(event_type, message)

    def write_test_state(self):
        if self.test_control and self.ready_file:
            Path(self.ready_file + '.state.json').write_text(json.dumps({
                'time': time.perf_counter(), 'clip': self.clip, 'index': self.index,
                'paused': self.paused, 'timer_active': self.timer.isActive(),
                'visible': self.isVisible(), 'geometry': self.geometry().getRect(),
                'paints': self.frame_count, 'cache_bytes': self.cache_bytes}), encoding='utf-8')


def main():
    identity = build_identity()
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=identity is None)
    parser.add_argument('--mode', choices=['animated', 'paused', 'hidden'], default='animated')
    parser.add_argument('--config-dir', type=Path)
    parser.add_argument('--ready-file')
    parser.add_argument('--test-control', action='store_true')
    parser.add_argument('--metrics-file', help='Opt-in bounded test instrumentation; absent in ordinary launches')
    parser.add_argument('--seed', type=int, help='Reproducible animation choices for tests')
    args = parser.parse_args()
    edition = identity['edition'] if identity else args.edition
    if identity and args.edition and args.edition != edition:
        parser.error('This package cannot run a different edition')
    selected = profile(edition)
    if args.config_dir is None:
        args.config_dir = CONFIG_DIR.parent / selected['product']
    app = QApplication(sys.argv[:1])
    app.setApplicationName(selected['title'])
    app.setQuitOnLastWindowClosed(False)
    args.config_dir.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(args.config_dir / 'instance.lock'))
    if not lock.tryLock(0):
        return 0
    pet = Pet(args.config_dir / 'settings.json', edition=edition,
              assets=ASSETS if identity else assets_for(edition), identity=identity, seed=args.seed, mode=args.mode,
              ready_file=args.ready_file, test_control=args.test_control, metrics_file=args.metrics_file)
    app.aboutToQuit.connect(pet.shutdown)
    result = app.exec()
    lock.unlock()
    return result


if __name__ == '__main__':
    raise SystemExit(main())
