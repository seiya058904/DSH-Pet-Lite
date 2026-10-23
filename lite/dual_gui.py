"""Installed Full/Ultra Win32 pointer acceptance with an owned receiver window.

Native input is scoped by live WindowFromPoint ownership before each gesture.
Retains every run, including failures. No screenshot of unrelated desktop content.
"""
import argparse
import ctypes
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from PIL import Image, ImageGrab
import psutil
from dual_soak import wait_for
from edition import EDITIONS, profile
from winprobe import user, windows, tray_toggle

ROOT = Path(__file__).resolve().parents[1]
user.WindowFromPoint.argtypes = [w.POINT]
user.WindowFromPoint.restype = w.HWND


def pointer(x, y, pid, right=False):
    owner = w.DWORD()
    user.GetWindowThreadProcessId(user.WindowFromPoint(w.POINT(x, y)), ctypes.byref(owner))
    assert owner.value == pid, ('Pointer target ownership changed', owner.value, pid)
    user.SetCursorPos(x, y)
    time.sleep(.08)
    user.mouse_event(8 if right else 2, 0, 0, 0, 0)
    time.sleep(.08)
    user.mouse_event(16 if right else 4, 0, 0, 0, 0)
    time.sleep(.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=True)
    args = parser.parse_args()
    product = profile(args.edition)['product']
    exe = Path(os.environ['LOCALAPPDATA'])/'Programs'/product/f'{product}.exe'
    out = ROOT/'benchmarks/dual-local'/f'{args.edition}-gui-{time.time_ns()}'
    out.mkdir(parents=True)
    config = out/'config'
    config.mkdir()
    (config/'settings.json').write_text(json.dumps({'x': 500, 'y': 430, 'paused': False}))
    ready, events = out/'ready.json', out/'receiver.jsonl'
    statefile = Path(str(ready)+'.state.json')
    env = os.environ.copy()
    env.pop('QT_QPA_PLATFORM', None)
    env['PATH'] = os.pathsep.join([str(Path(os.environ['SystemRoot'])/'System32'), os.environ['SystemRoot']])
    backdrop = subprocess.Popen([sys.executable, str(ROOT/'lite/gui_receiver.py'), str(events)], env=env)
    process = None
    receiver = None
    result = {'edition': args.edition, 'checks': {}, 'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
              'method': 'Win32 real cursor and mouse input; test messages for state/pause/hide; Qt tray callback for restore'}
    try:
        def receiver_windows():
            ids = [backdrop.pid, *[p.pid for p in psutil.Process(backdrop.pid).children(recursive=True)]]
            return [r for pid in ids for r in windows(pid)]
        receiver = wait_for(lambda: next((r for r in receiver_windows() if r['visible'] and 'backdrop' in r['title']), None))
        receiver_pid = w.DWORD()
        user.GetWindowThreadProcessId(receiver['hwnd'], ctypes.byref(receiver_pid))
        result['receiver_topmost_result'] = user.SetWindowPos(receiver['hwnd'], -1, 0, 0, 0, 0, 0x13)
        result['receiver_foreground_result'] = user.SetForegroundWindow(receiver['hwnd'])
        time.sleep(.5)
        process = subprocess.Popen([str(exe), '--config-dir', str(config), '--test-control', '--ready-file', str(ready)],
                                   cwd=tempfile.gettempdir(), env=env)
        wait_for(lambda: ready.exists())
        hwnd = next(r['hwnd'] for r in windows(process.pid) if r['title'] == profile(args.edition)['title'])
        # Keep the test receiver above unrelated always-on-top applications;
        # raise our pet above it, then confirm native hit ownership before input.
        user.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x13)
        time.sleep(.5)
        result['receiver_windows'] = receiver_windows()
        def control(n):
            user.PostMessageW(hwnd, 0x8000+77, n, 0)
            time.sleep(.1)
        def state():
            old = json.loads(statefile.read_text())['time'] if statefile.exists() else 0
            control(6)
            return wait_for(lambda: s if (s := json.loads(statefile.read_text()))['time'] > old else None)
        def record(name, condition):
            result['checks'][name] = bool(condition)
            assert condition, name
        manifest = json.loads((exe.parent/'_internal/assets/manifest.json').read_text(encoding='utf-8'))
        def opaque_point():
            s = state()
            clip, index = s['clip'], s['index']
            image = Image.open(exe.parent/'_internal/assets'/clip/f'{index:04}.webp').convert('RGBA')
            # Pick near body centre, away from hair/edge transparency.
            choices = [(x, y) for y in range(image.height//3, image.height*2//3)
                       for x in range(image.width//3, image.width*2//3) if image.getpixel((x, y))[3] == 255]
            x, y = choices[len(choices)//2]
            ox, oy = manifest['clips'][clip]['offsets'][index]
            return s['geometry'][0]+ox+x, s['geometry'][1]+oy+y
        control(1)
        s = state()
        style = user.GetWindowLongW(hwnd, -20)
        record('layered_topmost_tool_window', style & 0x80000 and style & 8 and style & 0x80)
        record('expected_small_canvas', s['geometry'][2:] == manifest['size'])
        record('paused_timer_stopped', not s['timer_active'])
        pointer(502, 432, receiver_pid.value)
        record('transparent_corner_delivers_real_click_to_receiver', events.exists() and len(events.read_text().splitlines()) == 1)
        user.SetWindowPos(receiver['hwnd'], -2, 0, 0, 0, 0, 0x13)
        user.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x13)
        user.SetForegroundWindow(hwnd)
        time.sleep(.3)
        pointer(*opaque_point(), process.pid)
        s = state()
        result['after_opaque_click'] = s
        record('opaque_click_triggers_click_animation', manifest['clips'][s['clip']].get('category', s['clip']) == 'click')
        record('opaque_click_not_received_by_background', len(events.read_text().splitlines()) == 1)
        # Receiver client area exclusively; no private desktop or other app included.
        ImageGrab.grab((410, 340, 1090, 940)).save(out/'alpha.png')
        x, y = opaque_point()
        start = state()['geometry'][:2]
        user.SetCursorPos(x, y)
        user.mouse_event(2, 0, 0, 0, 0)
        try:
            for i in range(1, 11):
                user.SetCursorPos(x+i*6, y+i*4)
                time.sleep(.025)
            s = state()
            record('real_drag_moves_and_plays_drag', s['clip'] == 'drag' and s['geometry'][0] >= start[0]+50)
        finally:
            user.mouse_event(4, 0, 0, 0, 0)
        time.sleep(.15)
        s = state()
        saved = json.loads((config/'settings.json').read_text())
        record('release_idle_and_atomic_position_save', s['clip'] == 'idle' and saved['x'] == s['geometry'][0])
        duplicate = subprocess.run([str(exe), '--config-dir', str(config)], env=env, cwd=tempfile.gettempdir(), timeout=15)
        record('same_edition_single_instance', duplicate.returncode == 0)
        control(3)
        s = state()
        record('hidden_stops_and_releases_cache', not s['visible'] and not s['timer_active'] and s['cache_bytes'] == 0)
        tray_toggle(process.pid)
        wait_for(lambda: state()['visible'])
        record('tray_callback_restores', state()['visible'])
        record('no_children', not psutil.Process(process.pid).children(recursive=True))
        modules = [m.path for m in psutil.Process(process.pid).memory_maps()]
        record('no_development_runtime_dependency', not any('.venv' in m.lower() for m in modules))
        pointer(*opaque_point(), process.pid, right=True)
        popup = wait_for(lambda: next((r for r in windows(process.pid) if r['visible'] and 'Popup' in r['class_name']), None))
        time.sleep(.5)
        ImageGrab.grab(tuple(popup['rect'])).save(out/'exit-menu.png')
        # Exit is the last action, source-verified in the shared menu. Real pointer click.
        pointer(popup['rect'][0]+50, popup['rect'][3]-14, process.pid)
        record('real_menu_exit_code_zero', process.wait(15) == 0)
        result['status'] = 'PASS'
        result['dpr'] = json.loads(ready.read_text())['dpr']
        # Relaunch is independently observed; final cleanup uses explicit test control.
        process = subprocess.Popen([str(exe), '--config-dir', str(config), '--test-control'], env=env, cwd=tempfile.gettempdir())
        hwnd = wait_for(lambda: next((r['hwnd'] for r in windows(process.pid) if r['visible'] and r['title'] == profile(args.edition)['title']), None))
        record('relaunch_visible', bool(hwnd))
        user.PostMessageW(hwnd, 0x8000+77, 5, 0)
        process.wait(15)
    except Exception as exc:
        result['status'], result['error'] = 'FAIL', repr(exc)
        raise
    finally:
        if process and process.poll() is None:
            for row in windows(process.pid):
                if row['title'] == profile(args.edition)['title']:
                    user.PostMessageW(row['hwnd'], 0x8000+77, 5, 0)
            process.wait(15)
        if receiver:
            user.PostMessageW(receiver['hwnd'], 0x10, 0, 0)
            backdrop.wait(15)
        (out/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps({'result': str(out/'result.json'), **result}), flush=True)


if __name__ == '__main__':
    main()
