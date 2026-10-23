"""Publish de-identified numeric evidence only after both final soaks and trials pass."""
import csv
import json
import math
from pathlib import Path
import platform
import statistics

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT/'benchmarks/public'


def stats(values):
    values = sorted(values)
    return {'n': len(values), 'mean': statistics.mean(values),
            'p95': values[max(0, math.ceil(.95*len(values))-1)],
            'p99': values[max(0, math.ceil(.99*len(values))-1)],
            'peak': values[-1], 'minimum': values[0]}


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    summary = {'environment': {'os': platform.platform(), 'architecture': platform.machine(),
               'logical_cpus': 16, 'dpi_tested': '100%', 'python': platform.python_version(),
               'qt': '6.12.0'}, 'editions': {}, 'cpu_status': 'NOT RELIABLY MEASURED',
               'public_dual_binary_release': 'BLOCKED',
               'soak_comparison_boundary': 'Concurrent stability runs, not isolated performance comparisons'}
    for edition in ('full', 'ultra'):
        folder = sorted((ROOT/'benchmarks/dual-local').glob(f'{edition}-soak-*'))[-1]
        result = json.loads((folder/'result.json').read_text())
        assert result['status'] == 'PASS', result
        raw = [json.loads(line) for line in (folder/'samples.jsonl').read_text().splitlines()]
        phase_stats = {}
        for phase in ('visible', 'paused', 'hidden', 'restored'):
            rows = [r for r in raw if r['phase'] == phase]
            phase_stats[phase] = {field: stats([r[field] for r in rows]) for field in
                ('private_bytes', 'working_set', 'cycles_per_s', 'threads', 'handles', 'processes', 'connections', 'system_cpu_pct')}
            phase_stats[phase]['private_bytes_first_last'] = [rows[0]['private_bytes'], rows[-1]['private_bytes']]
            phase_stats[phase]['cpu_time_increment_s'] = rows[-1]['native_cpu_s']-rows[0]['native_cpu_s']
        rows = []
        for r in raw:
            row = dict(r)
            row['elapsed_s'] = row.pop('monotonic')-raw[0]['monotonic']
            rows.append(row)
        write_csv(PUBLIC/f'{edition}-soak.csv', rows)
        visible = next(p for p in result['phases'] if p['phase'] == 'visible')
        times = json.loads((folder/'paints.json').read_text())['paint_times']
        times = [t for t in times if visible['started'] <= t <= visible['started']+visible['actual_seconds']]
        intervals = [(b-a)*1000 for a,b in zip(times, times[1:])]
        write_csv(PUBLIC/f'{edition}-paint-intervals.csv', [{'interval_ms': v} for v in intervals])
        gui_results = [json.loads(p.read_text()) for p in sorted((ROOT/'benchmarks/dual-local').glob(f'{edition}-gui-*/result.json'))]
        gui = gui_results[-1]
        assert gui['status'] == 'PASS' and gui['exe_sha256'] == result['exe_sha256']
        package = json.loads((ROOT/f'dist/dual-final/{edition}-package.json').read_text())
        summary['editions'][edition] = {'identity': result['identity'], 'exe_sha256': result['exe_sha256'],
            'package': package, 'soak_status': result['status'], 'checks': result['checks'],
            'phase_seconds': {p['phase']: p['actual_seconds'] for p in result['phases']},
            'resources': phase_stats, 'visible_paint_intervals_ms': stats(intervals),
            'paint_intervals_over_125_ms': sum(v > 125 for v in intervals),
            'first_qt_paint_s_concurrent_run': result['first_qt_paint_s'],
            'gui_checks': gui['checks'], 'recorded_gui_attempts': len(gui_results),
            'recorded_gui_failures': sum(r['status'] != 'PASS' for r in gui_results)}
    trials = json.loads((PUBLIC/'independent-trials.json').read_text())
    grouped = {}
    for product in 'ABCD':
        runs = [r for r in trials if r['product'] == product]
        assert len(runs) == 3 and all(r['status'] == 'PASS' and r['exit_code'] == 0 for r in runs)
        rows = [s for r in runs for s in r['samples']]
        grouped[product] = {field: stats([s[field] for s in rows]) for field in
                           ('private_bytes', 'working_set', 'cycles_per_s', 'threads', 'handles', 'system_cpu_pct')}
        grouped[product]['independent_runs'] = 3
        grouped[product]['run_means'] = {field: [statistics.mean(s[field] for s in r['samples']) for r in runs]
                                      for field in ('private_bytes', 'working_set', 'cycles_per_s')}
        grouped[product]['visible_window_s'] = stats([r['visible_window_s'] for r in runs])
        grouped[product]['first_qt_paint_s'] = stats([r['first_qt_paint_s'] for r in runs]) if product != 'A' else None
    summary['independent_trials'] = grouped
    changes = {}
    for field in ('private_bytes', 'working_set', 'cycles_per_s'):
        b, d = grouped['B']['run_means'][field], grouped['D']['run_means'][field]
        percents = [100*(new-old)/old for old,new in zip(b,d)]
        mean = statistics.mean(percents)
        margin = 4.303*statistics.stdev(percents)/math.sqrt(3)
        changes[field] = {'D_vs_B_change_percent': mean, 'approximate_95pct_t_interval': [mean-margin, mean+margin],
                          'independent_pairs': 3}
    summary['ultra_regression_comparison'] = changes
    (PUBLIC/'validation-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    historical = json.loads((ROOT/'benchmarks/performance-summary.json').read_text())
    old = {key: historical[key] for key in ('upstream_zip_bytes', 'upstream_expanded_bytes', 'lite_zip_bytes', 'lite_expanded_bytes')}
    old['scope'] = 'Historical package sizes only; original reports retained locally'
    (PUBLIC/'historical-package-sizes.json').write_text(json.dumps(old, indent=2), encoding='utf-8')
    def memory(product, field):
        s = grouped[product][field]
        return f"{s['mean']/1e6:.2f} / {s['p95']/1e6:.2f} / {s['peak']/1e6:.2f}"
    def timing(product):
        s = grouped[product]['first_qt_paint_s']
        return f"{s['mean']:.3f}" if s else 'Not instrumented'
    table = [
        '| Metric | Official full no-chat A | Previous three-action Lite B | Full C | Ultra D |',
        '|---|---:|---:|---:|---:|',
        '| Clips / frames | 106 / 25,423 | 3 / 723 | 106 / 25,423 | 3 / 723 |',
        '| ZIP MB | 348.97 (historical) | 55.60 (historical) | 1,034.44 | 55.62 |',
        '| Expanded MB | 576.93 (historical) | 98.60 (historical) | 1,074.00 | 98.61 |',
        '| Private MB mean / P95 / peak | '+' | '.join(memory(p, 'private_bytes') for p in 'ABCD')+' |',
        '| Working Set MB mean / P95 / peak | '+' | '.join(memory(p, 'working_set') for p in 'ABCD')+' |',
        '| CPU cycles/s mean (millions) | '+' | '.join(f"{grouped[p]['cycles_per_s']['mean']/1e6:.2f}" for p in 'ABCD')+' |',
        '| First Qt paint mean, seconds | '+' | '.join(timing(p) for p in 'ABCD')+' |',
        '| CPU percentage | Not reliable | Not reliable | Not reliable | Not reliable |',
        '| Watts / GPU / physical Present | Not measured | Not measured | Not measured | Not measured |']
    report = '# Performance report\n\n**PARTIAL: local dual editions validated; public dual binaries BLOCKED.**\n\n'
    report += '\n'.join(table)+'\n\n'
    report += ('Memory/cycles use three fresh processes per product, 12-second warm-up then 45 samples per run. '
               'B/D are matched idle workloads. A/C use default full-animation behavior with different random '
               'schedules; their results are descriptive, not a controlled percentage-improvement claim. '
               'First Qt paint is not physical monitor presentation. CPU-time accounting is unreliable.\n\n')
    for edition, heading in [('full', 'Full Animation Lite — Benchmarks'), ('ultra', 'Ultra Lite — Benchmarks')]:
        data = summary['editions'][edition]
        cadence = data['visible_paint_intervals_ms']
        report += f'## {heading}\n\n'
        report += (f"Local ZIP: {data['package']['zip_bytes']:,} bytes; expanded: {data['package']['expanded_bytes']:,} bytes. "
                   f"Visible / paused / hidden soak: {data['phase_seconds']['visible']:.1f} / "
                   f"{data['phase_seconds']['paused']:.1f} / {data['phase_seconds']['hidden']:.1f} seconds. "
                   'These concurrent soaks are separate from the isolated comparison above.\n\n')
        report += (f"Visible Qt paint interval P95/P99/maximum: {cadence['p95']:.2f} / {cadence['p99']:.2f} / "
                   f"{cadence['peak']:.2f} ms; {data['paint_intervals_over_125_ms']} intervals exceeded 125 ms. "
                   'No physical Present FPS is inferred. Pause/hidden stopped the animation timer; hidden cleared '
                   'the idle cache. Real pointer click/drag, transparent pass-through, actual menu Exit and relaunch passed.\n\n')
        report += '| Phase | Private MB mean / P95 / peak | Working Set MB mean / P95 / peak |\n|---|---:|---:|\n'
        for phase in ('visible', 'paused', 'hidden'):
            def phase_memory(field):
                s = data['resources'][phase][field]
                return f"{s['mean']/1e6:.2f} / {s['p95']/1e6:.2f} / {s['peak']/1e6:.2f}"
            report += f"| {phase} | {phase_memory('private_bytes')} | {phase_memory('working_set')} |\n"
        report += f'\n[Raw soak samples](../benchmarks/public/{edition}-soak.csv) · [Paint intervals](../benchmarks/public/{edition}-paint-intervals.csv)\n\n'
    report += '### Ultra versus its own baseline\n\nPositive values mean a higher new measurement. Approximate 95% paired t intervals use only three independent pairs.\n\n'
    for field, data in changes.items():
        lo, hi = data['approximate_95pct_t_interval']
        report += f"- {field}: {data['D_vs_B_change_percent']:+.2f}% ({lo:+.2f}% to {hi:+.2f}%).\n"
    report += ('\n## Trade-offs & What to Choose\n\nFull preserves all clips and offers bounded roaming; Ultra retains the original three actions. '
               'Full lossless frame storage is larger than the official WebM package, so no ZIP-size improvement is claimed. '
               'The original 24 fps timeline and input safety outrank lower resource numbers.\n\n'
               'Three build-only probes rejected stronger encoding (~3% sampled savings), smaller/no idle cache '
               '(more repeated decode work) and a stored container (small absolute warm-cache benefit). '
               'This stops these experiments without claiming global optimality. [Probe data](../benchmarks/public/optimization-probes.json).\n\n'
               '## Failures and unverified scope\n\n'
               'Retained failures include native helper startup, untyped HWND arguments in the test harness, receiver focus/stacking, '
               'one focus-sensitive opaque click, and an interrupted pre-fix soak. A missing-frame recovery state bug was fixed and '
               'tested before the final packages. An installer module-path failure rolled back the previous install. '
               'Successful final GUI checks explicitly activate the owned pet window; the earlier unfocused click failure is not erased.\n\n'
               'Only 100% desktop scaling was physically tested. Physical tray-icon clicks, 125%/150% DPI, 4K, multiple monitors/hot-plug, '
               'network disconnection, GPU, watts and physical Present remain unverified. The source public CI uses synthetic assets. '
               'No character binary or screenshot is publicly distributed.\n\n'
               '[Methodology](BENCHMARK_METHODOLOGY.md) · [Full numeric summary](../benchmarks/public/validation-summary.json) · '
               '[Independent trials](../benchmarks/public/independent-trials.json) · [Dependency query](../benchmarks/public/dependency-audit.json)\n')
    (ROOT/'docs/PERFORMANCE_REPORT.md').write_text(report, encoding='utf-8')
    print(json.dumps({'soaks': {e: summary['editions'][e]['soak_status'] for e in ('full','ultra')}, 'ultra_changes': changes}))


if __name__ == '__main__':
    main()
