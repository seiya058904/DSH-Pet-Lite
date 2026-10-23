"""Three independent starts per product; matched B/C and U0/U1 workload scripts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import psutil
from dual_soak import wait_for
from measure_process import sample, delta
from winprobe import user, windows

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-root', type=Path, required=True)
    args = parser.parse_args()
    exes = {'A': ROOT/'benchmarks/upstream/dual-package/dsh-pet-standalone-webm.exe',
            'B': ROOT/'dist/v3-baseline/DSH-Pet-Lite-Core/DSH-Pet-Lite-Core.exe',
            'C': args.candidate_root.resolve()/'DSH-Pet-Lite-Core/DSH-Pet-Lite-Core.exe',
            'U0': ROOT/'dist/dual-final/DSH-Pet-Lite-Ultra/DSH-Pet-Lite-Ultra.exe',
            'U1': args.candidate_root.resolve()/'DSH-Pet-Lite-Ultra/DSH-Pet-Lite-Ultra.exe'}
    assert not [p.info for p in psutil.process_iter(['name']) if (p.info['name'] or '').lower().startswith('dsh')]
    out = ROOT/'benchmarks/v3-local'/f'comparison-{time.time_ns()}'
    out.mkdir(parents=True)
    results, trials = [], dict.fromkeys(exes, 0)
    order = ['B', 'C', 'U0', 'U1', 'A', 'C', 'B', 'U1', 'U0', 'A', 'B', 'C', 'U0', 'U1', 'A']
    for product in order:
        trials[product] += 1
        trial = trials[product]
        folder = out/f'{product}-{trial}'
        folder.mkdir()
        env = os.environ.copy()
        env.pop('QT_QPA_PLATFORM', None)
        env['PATH'] = os.pathsep.join([str(Path(os.environ['SystemRoot'])/'System32'), os.environ['SystemRoot']])
        command = [str(exes[product])]
        ready = folder/'ready.json'
        if product == 'A':
            env['APPDATA'] = str(folder)
            config = folder/'dsh-pet-standalone-webm'
            config.mkdir()
            (config/'config.json').write_text(json.dumps({'feature_activation': {'version': 1, 'enabled': []},
                'no_move': True, 'click_sound_enabled': False, 'collision_sound_enabled': False, 'scale': .72}))
        else:
            config = folder/'config'
            config.mkdir()
            (config/'settings.json').write_text(json.dumps({'x': 500, 'y': 430, 'paused': False}))
            command += ['--test-control', '--config-dir', str(config), '--ready-file', str(ready), '--seed', str(100+trial)]
        started = time.perf_counter()
        process = subprocess.Popen(command, env=env, cwd=tempfile.gettempdir())
        row = {'product': product, 'trial': trial, 'exe_sha256': hashlib.sha256(exes[product].read_bytes()).hexdigest(),
               'workload': 'uncontrolled official default, movement disabled; descriptive only' if product == 'A' else
                           '12s warmup; 24s idle reset every 8s; click/drag/idle 8s each; pause 5s; hidden 5s',
               'status': 'RUNNING', 'samples': []}
        try:
            window = wait_for(lambda: next((r for r in windows(process.pid) if r['visible'] and
                               r['title'] not in ('_q_titlebar', 'MSCTFIME UI') and 'Tool' in r['class_name']), None), 30)
            row['visible_window_s'] = time.perf_counter()-started
            if product != 'A':
                first = wait_for(lambda: json.loads(ready.read_text()))
                row['first_qt_paint_s'] = first['paint_monotonic']-started
                manifest = json.loads((exes[product].parent/'_internal/assets/manifest.json').read_text(encoding='utf-8'))
                names = list(manifest['clips'])
            else:
                row['first_qt_paint_s'] = None
            def control(action, value=0):
                if product != 'A':
                    user.PostMessageW(window['hwnd'], 0x8000+77, action, value)
            def select(name):
                if product != 'A':
                    control(7, names.index(name))
            select('idle')
            time.sleep(6)
            select('idle')
            time.sleep(6)
            previous = sample(process.pid)
            phases = [('idle', 'idle', 24), ('click', 'click', 8), ('drag', 'drag', 8), ('idle_after', 'idle', 8),
                      ('paused', None, 5), ('hidden', None, 5)]
            for phase, clip, duration in phases:
                if clip:
                    select(clip)
                elif phase == 'paused':
                    control(1)
                else:
                    control(3)
                for second in range(duration):
                    if phase == 'idle' and second in (8, 16):
                        select('idle')
                    time.sleep(1)
                    current = sample(process.pid)
                    row['samples'].append({'phase': phase if product != 'A' else 'official_default',
                                           **current, **delta(current, previous)})
                    previous = current
            row['children_at_end'] = len(psutil.Process(process.pid).children(recursive=True))
            row['status'] = 'PASS'
        except Exception as exc:
            row['status'], row['error'] = 'FAIL', repr(exc)
            raise
        finally:
            if process.poll() is None:
                target = next((r for r in windows(process.pid) if r['title'].startswith('DSH Pet Lite') or
                              (r['visible'] and 'Tool' in r['class_name'])), None)
                if target:
                    if product == 'A':
                        user.PostThreadMessageW(user.GetWindowThreadProcessId(target['hwnd'], None), 0x12, 0, 0)
                    else:
                        user.PostMessageW(target['hwnd'], 0x8000+77, 5, 0)
                row['exit_code'] = process.wait(20)
            results.append(row)
            (out/'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
            print(product, trial, row['status'], flush=True)
    (ROOT/'benchmarks/public/core-ultra-trials.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
