"""Native integration-test helper for tool windows omitted by sky.list_windows()."""
import ctypes
import json
import sys
import time
from ctypes import wintypes as w

user = ctypes.windll.user32
user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
user.SendMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
user.SendMessageW.restype = w.LPARAM
user.SetWindowPos.argtypes = [w.HWND, w.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, w.UINT]
user.SetWindowPos.restype = w.BOOL
user.SetForegroundWindow.argtypes = [w.HWND]
user.SetForegroundWindow.restype = w.BOOL
user.PostMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
user.PostMessageW.restype = w.BOOL
CALLBACK = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)


def windows(pid):
    result = []
    def enum(hwnd, _):
        value = w.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(value))
        if value.value == pid:
            text = ctypes.create_unicode_buffer(256)
            user.GetWindowTextW(hwnd, text, 256)
            cls = ctypes.create_unicode_buffer(256)
            user.GetClassNameW(hwnd, cls, 256)
            rect = w.RECT()
            user.GetWindowRect(hwnd, ctypes.byref(rect))
            result.append(dict(hwnd=hwnd, title=text.value, class_name=cls.value, visible=bool(user.IsWindowVisible(hwnd)),
                               rect=[rect.left, rect.top, rect.right, rect.bottom]))
        return True
    user.EnumWindows(CALLBACK(enum), 0)
    return result


def tray_toggle(pid):
    target = next(x for x in windows(pid) if x['title'] == 'QTrayIconMessageWindow')
    # Qt Windows plugin's documented source: MYWM_NOTIFYICON=WM_APP+101, id=0.
    user.PostMessageW(target['hwnd'], 0x8000+101, 0, 0x203)


def tray_quit_upstream(pid):
    """Open the real upstream native tray menu, select its verified last Exit item."""
    class GUIInfo(ctypes.Structure):
        _fields_ = [('cbSize', w.DWORD), ('flags', w.DWORD), ('hwndActive', w.HWND),
                    ('hwndFocus', w.HWND), ('hwndCapture', w.HWND), ('hwndMenuOwner', w.HWND),
                    ('hwndMoveSize', w.HWND), ('hwndCaret', w.HWND), ('rcCaret', w.RECT)]
    def own_popup():
        return next((x for x in windows(pid) if x['visible'] and
                     'Popup' in x['class_name'] and
                     60 < x['rect'][2]-x['rect'][0] < 500 and
                     60 < x['rect'][3]-x['rect'][1] < 900 and x['title'] != '_q_titlebar'), None)
    def click_exit(popup):
        # Qt popup fade-in ignores an immediate release during its opening gesture.
        time.sleep(.35)
        user.SetForegroundWindow(popup['hwnd'])
        foreground_pid = w.DWORD()
        user.GetWindowThreadProcessId(user.GetForegroundWindow(), ctypes.byref(foreground_pid))
        if foreground_pid.value != pid:
            raise RuntimeError('Owned tray popup is not foreground; no click sent')
        x, y = popup['rect'][0]+50, popup['rect'][3]-14
        user.SetCursorPos(x, y)
        time.sleep(.04)
        user.WindowFromPoint.argtypes = [w.POINT]
        user.WindowFromPoint.restype = w.HWND
        hit = user.WindowFromPoint(w.POINT(x, y))
        if hit != popup['hwnd'] and not user.IsChild(popup['hwnd'], hit):
            raise RuntimeError('Exit menu no longer owns the target point; no click sent')
        user.mouse_event(2, 0, 0, 0, 0)
        time.sleep(.06)
        user.mouse_event(4, 0, 0, 0, 0)
    popup = own_popup()
    target = next(x for x in windows(pid) if x['title'] == 'QTrayIconMessageWindow')
    if popup:
        click_exit(popup)
        return
    user.PostMessageW(target['hwnd'], 0x8000+101, (800 << 16) | 1600, 0x7B)
    thread = user.GetWindowThreadProcessId(target['hwnd'], None)
    deadline = time.monotonic()+10
    while time.monotonic() < deadline:
        popup = own_popup()
        if popup:
            click_exit(popup)
            return
        info = GUIInfo()
        info.cbSize = ctypes.sizeof(info)
        user.GetGUIThreadInfo(thread, ctypes.byref(info))
        owner = w.DWORD()
        if info.hwndMenuOwner:
            user.GetWindowThreadProcessId(info.hwndMenuOwner, ctypes.byref(owner))
        if info.flags & 4 and owner.value == pid:
            for key in (0x23, 0x0D):  # End, Enter: source-verified final item is Exit.
                user.keybd_event(key, 0, 0, 0)
                user.keybd_event(key, 0, 2, 0)
            return
        time.sleep(.02)
    raise RuntimeError('Owned tray menu not confirmed; no unscoped keys sent')


if __name__ == '__main__':
    pid = int(sys.argv[1])
    rows = windows(pid)
    if len(sys.argv) == 2:
        print(json.dumps(rows, ensure_ascii=False))
    elif sys.argv[2] == 'control':
        target = next(x for x in rows if x['title'] == 'DSH Pet Lite')
        user.PostMessageW(target['hwnd'], 0x8000+77, int(sys.argv[3]), 0)
    elif sys.argv[2] == 'quit-upstream':
        tray_quit_upstream(pid)
    elif sys.argv[2] == 'menu':
        target = next(x for x in rows if x['visible'] and x['title'] != '_q_titlebar')
        x, y = int(sys.argv[3]), int(sys.argv[4])
        user.PostMessageW(target['hwnd'], 0x7B, target['hwnd'], (y << 16) | (x & 0xFFFF))
