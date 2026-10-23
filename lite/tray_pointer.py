"""Physical taskbar clicks, scoped to a freshly observed UIA icon and Explorer PID."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import time
import ctypes
from ctypes import wintypes as w
from winprobe import user


def observe():
    env = os.environ.copy()
    env.pop('PSModulePath', None)
    env.pop('PSMODULEPATH', None)
    shell = shutil.which('pwsh') or 'powershell'
    return json.loads(subprocess.check_output([shell, '-NoProfile', '-File',
        str(Path(__file__).with_name('inspect_tray.ps1'))], env=env, encoding='utf-8-sig',
        creationflags=subprocess.CREATE_NO_WINDOW))


def click(row, *, right=False, double=False):
    x, y = round((row['rect'][0]+row['rect'][2])/2), round((row['rect'][1]+row['rect'][3])/2)
    user.WindowFromPoint.argtypes = [w.POINT]
    user.WindowFromPoint.restype = w.HWND
    owner = w.DWORD()
    user.GetWindowThreadProcessId(user.WindowFromPoint(w.POINT(x, y)), ctypes.byref(owner))
    assert owner.value == row['process'], 'Tray ownership changed; no input sent'
    user.SetCursorPos(x, y)
    for _ in range(2 if double else 1):
        user.mouse_event(8 if right else 2, 0, 0, 0, 0)
        time.sleep(.04)
        user.mouse_event(16 if right else 4, 0, 0, 0, 0)
        time.sleep(.06)
    time.sleep(.25)


def tray_click(title, *, right=False):
    before = observe()
    matches = [r for r in before if r['name'].startswith(title+' ')]
    if not matches:
        buttons = [r for r in before if r['class'] == 'SystemTray.NormalButton' and 'DSH' not in r['name']]
        assert len(buttons) == 1, ('No unique observed overflow button', before)
        click(buttons[0])
        before = observe()
        matches = [r for r in before if r['name'].startswith(title+' ')]
    assert len(matches) == 1, ('No unique visible owned tray icon', before)
    click(matches[0], right=right, double=not right)
    return {'method': 'UIA-observed icon rectangle + real mouse events; no Qt notification injection',
            'icon_name': matches[0]['name'], 'icon_rectangle': matches[0]['rect'], 'right_click': right}
