"""Three independent launches of each of four products, with no concurrent pets.

B/D are matched three-action idle workloads. A/C are default full-animation
workloads; random action schedules differ, so their cycle values are descriptive.
"""
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
    installed = Path(os.environ['LOCALAPPDATA'])/'Programs'
    exes = {'A': ROOT/'benchmarks/upstream/dual-package/dsh-pet-standalone-webm.exe',
            'B': installed/'DSH-Pet-Lite.backup-20261023-155041/DSH-Pet-Lite.exe',
            'C': installed/'DSH-Pet-Lite-Full/DSH-Pet-Lite-Full.exe',
            'D': installed/'DSH-Pet-Lite-Ultra/DSH-Pet-Lite-Ultra.exe'}
    names = {p.name.lower() for p in exes.values()}
    if any((p.info['name'] or '').lower() in names for p in psutil.process_iter(['name'])):
        raise RuntimeError('Pet already running; isolated comparison refused')
    out = ROOT/'benchmarks/dual-local'/f'comparison-{time.time_ns()}'
    out.mkdir(parents=True)
    results, trials = [], dict.fromkeys(exes, 0)
    for product in ['B', 'D', 'D', 'B', 'B', 'D', 'A', 'C', 'C', 'A', 'A', 'C']:
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
                'no_move': False, 'click_sound_enabled': False, 'collision_sound_enabled': False, 'scale': .72}))
        else:
            command += ['--test-control', '--config-dir', str(folder/'config'), '--ready-file', str(ready)]
            if product in ('C', 'D'):
                command += ['--seed', str(100+trial)]
        started = time.perf_counter()
        process = subprocess.Popen(command, env=env, cwd=tempfile.gettempdir())
        result = {'product': product, 'trial': trial, 'exe_sha256': hashlib.sha256(exes[product].read_bytes()).hexdigest(),
                  'workload': 'default full animation, unmatched random schedule' if product in ('A', 'C') else 'three-action idle',
                  'status': 'RUNNING'}
        try:
            window = wait_for(lambda: next((r for r in windows(process.pid) if r['visible'] and
                               r['title'] not in ('_q_titlebar', 'MSCTFIME UI') and 'Tool' in r['class_name']), None), 30)
            result['visible_window_s'] = time.perf_counter()-started
            result['window_class'] = window['class_name']
            if product != 'A':
                first = wait_for(lambda: json.loads(ready.read_text()))
                result['first_qt_paint_s'] = first['paint_monotonic']-started
            else:
                result['first_qt_paint_s'] = None
            time.sleep(12)
            rows, previous = [], sample(process.pid)
            for _ in range(45):
                time.sleep(1)
                current = sample(process.pid)
                rows.append({**current, **delta(current, previous)})
                previous = current
            (folder/'samples.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
            result['samples'] = rows
            result['children_at_end'] = len(psutil.Process(process.pid).children(recursive=True))
            result['status'] = 'PASS'
        except Exception as exc:
            result['status'], result['error'] = 'FAIL', repr(exc)
            raise
        finally:
            if process.poll() is None:
                if product == 'A':
                    target = next((r for r in windows(process.pid) if r['visible'] and 'Tool' in r['class_name']), None)
                    if target:
                        user.PostThreadMessageW(user.GetWindowThreadProcessId(target['hwnd'], None), 0x12, 0, 0)
                else:
                    target = next((r for r in windows(process.pid) if r['title'].startswith('DSH Pet Lite')), None)
                    if target:
                        user.PostMessageW(target['hwnd'], 0x8000+77, 5, 0)
                result['exit_code'] = process.wait(20)
            results.append(result)
            (out/'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
            print(product, trial, result['status'], flush=True)
    # The public copy has no paths, PIDs, machine name or private user settings.
    (ROOT/'benchmarks/public/independent-trials.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
