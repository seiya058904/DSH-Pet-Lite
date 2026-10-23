"""Final installed binary soak: 30 min visible, 5 paused, 5 hidden per edition.

Sequential editions avoid cross-edition interference. Opt-in controls verify
timer state; these do not stand in for the separate physical pointer acceptance.
"""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
import psutil
from edition import EDITIONS, profile
from measure_process import sample, delta
from winprobe import user, windows

ROOT = Path(__file__).resolve().parents[1]


def wait_for(predicate, seconds=20):
    deadline = time.monotonic()+seconds
    while time.monotonic() < deadline:
        try:
            value = predicate()
            if value:
                return value
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(.03)
    raise TimeoutError('Expected installed process state was not reached')


def run(edition, duration, executable=None):
    product = profile(edition)['product']
    exe = executable or Path(os.environ['LOCALAPPDATA'])/'Programs'/product/f'{product}.exe'
    exe = exe.resolve()
    out = ROOT/'benchmarks/v3-local'/f'{edition}-soak-{time.time_ns()}'
    out.mkdir(parents=True, exist_ok=False)
    ready, metrics = out/'ready.json', out/'paints.json'
    statefile = Path(str(ready)+'.state.json')
    env = os.environ.copy()
    env.pop('QT_QPA_PLATFORM', None)
    env['PATH'] = os.pathsep.join([str(Path(os.environ['SystemRoot'])/'System32'), os.environ['SystemRoot']])
    start = time.perf_counter()
    process = subprocess.Popen([str(exe), '--config-dir', str(out/'config'), '--test-control',
                                '--ready-file', str(ready), '--metrics-file', str(metrics), '--seed', '42'],
                               cwd=tempfile.gettempdir(), env=env)
    result = {'edition': edition, 'pid': process.pid, 'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
              'identity': json.loads((exe.parent/'_internal/build-info.json').read_text()),
              'checks': {}, 'phases': [], 'method': 'Installed binary; test controls, not physical pointer acceptance'}
    try:
        first = wait_for(lambda: json.loads(ready.read_text()))
        result['first_qt_paint_s'] = first['paint_monotonic']-start
        hwnd = next(w['hwnd'] for w in windows(process.pid) if w['title'] == profile(edition)['title'])
        def control(action, value=0):
            user.PostMessageW(hwnd, 0x8000+77, action, value)
        def state():
            old = json.loads(statefile.read_text())['time'] if statefile.exists() else 0
            control(6)
            return wait_for(lambda: d if (d := json.loads(statefile.read_text()))['time'] > old else None)
        manifest = json.loads((exe.parent/'_internal/assets/manifest.json').read_text(encoding='utf-8'))
        names = list(manifest['clips'])
        with (out/'samples.jsonl').open('w', encoding='utf-8') as stream:
            previous = sample(process.pid)
            for phase, seconds, action in [('visible', duration, 2), ('paused', 300, 1), ('hidden', 300, 3), ('restored', 15, 4)]:
                control(action)
                if phase == 'restored':
                    control(2)
                phase_start = time.monotonic()
                initial = state()
                result['phases'].append({'phase': phase, 'started': phase_start, 'seconds': seconds})
                clip_index, next_clip = 0, phase_start
                while time.monotonic()-phase_start < seconds:
                    if process.poll() is not None:
                        raise RuntimeError(f'Unexpected exit: {process.returncode}')
                    # Play every clip completely, including turn prelude + move.
                    if phase == 'visible' and time.monotonic() >= next_clip:
                        name = names[clip_index % len(names)]
                        control(7, names.index(name))
                        prelude = 11 if manifest['clips'][name].get('category') == 'move' else 0
                        next_clip = time.monotonic()+manifest['clips'][name]['frames']/manifest['fps']+.5+prelude
                        clip_index += 1
                    current = sample(process.pid)
                    stream.write(json.dumps({'edition': edition, 'phase': phase, **current,
                                             **delta(current, previous)})+'\n')
                    stream.flush()
                    previous = current
                    time.sleep(1)
                final = state()
                result['phases'][-1]['actual_seconds'] = time.monotonic()-phase_start
                if phase in ('paused', 'hidden'):
                    result['checks'][phase+'_timer_stopped'] = not final['timer_active'] and final['index'] == initial['index']
                if phase == 'hidden':
                    result['checks']['hidden_cache_empty'] = final['cache_bytes'] == 0
                (out/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        result['checks']['no_children'] = not psutil.Process(process.pid).children(recursive=True)
        control(5)
        result['exit_code'] = process.wait(15)
        assert all(result['checks'].values()), result['checks']
        result['status'] = 'PASS'
    except Exception as exc:
        result['status'], result['error'] = 'FAIL', repr(exc)
        raise
    finally:
        if process.poll() is None:
            targets = [w for w in windows(process.pid) if w['title'] == profile(edition)['title']]
            if targets:
                user.PostMessageW(targets[0]['hwnd'], 0x8000+77, 5, 0)
                process.wait(15)
        (out/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', choices=EDITIONS, required=True)
    parser.add_argument('--visible-seconds', type=int, default=1800)
    parser.add_argument('--exe', type=Path)
    args = parser.parse_args()
    run(args.edition, args.visible_seconds, args.exe)
