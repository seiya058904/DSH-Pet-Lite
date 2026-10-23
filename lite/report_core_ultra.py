"""Summarize actual independent runs without turning unmatched workloads into gains."""
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]


def stats(values):
    values = sorted(values)
    return {'n': len(values), 'mean': statistics.mean(values),
            'p95': values[math.ceil(.95*len(values))-1], 'peak': values[-1]}


def main():
    rows = json.loads((ROOT/'benchmarks/public/core-ultra-trials.json').read_text())
    assert len(rows) == 15 and all(r['status'] == 'PASS' and r['exit_code'] == 0 for r in rows)
    grouped = {}
    fields = ['private_bytes', 'working_set', 'cycles_per_s', 'threads', 'handles', 'read_bytes',
              'write_bytes', 'native_cpu_s', 'thread_cpu_s', 'voluntary_context_switches']
    for product in ['A', 'B', 'C', 'U0', 'U1']:
        trials = [r for r in rows if r['product'] == product]
        visible = [s for r in trials for s in r['samples'] if s['phase'] not in ('paused', 'hidden')]
        grouped[product] = {field: stats([s[field] for s in visible]) for field in fields}
        grouped[product]['first_qt_paint_s'] = stats([r['first_qt_paint_s'] for r in trials]) if product != 'A' else None
        grouped[product]['exe_sha256'] = trials[0]['exe_sha256']
        grouped[product]['trials'] = len(trials)
        grouped[product]['phases'] = {phase: {field: stats([s[field] for r in trials for s in r['samples']
                                                    if s['phase'] == phase]) for field in fields}
                                    for phase in {s['phase'] for r in trials for s in r['samples']}}
    changes = {}
    for old, new in [('B', 'C'), ('U0', 'U1')]:
        changes[old+'->'+new] = {}
        for field in ['private_bytes', 'working_set', 'cycles_per_s']:
            def means(product):
                return [statistics.mean(s[field] for s in r['samples'] if s['phase'] not in ('paused', 'hidden'))
                        for r in rows if r['product'] == product]
            differences = [(b/a-1)*100 for a, b in zip(means(old), means(new))]
            mean = statistics.mean(differences)
            margin = 4.3026527299*statistics.stdev(differences)/math.sqrt(3)
            changes[old+'->'+new][field] = {'mean_change_percent': mean,
                'approximate_95pct_paired_t_interval': [mean-margin, mean+margin], 'independent_pairs': 3}
    package_paths = {'B': ROOT/'dist/v3-baseline/core-package.json',
                     'C': ROOT/'dist/v3-candidate/core-package.json',
                     'U0': ROOT/'dist/dual-final/ultra-package.json',
                     'U1': ROOT/'dist/v3-candidate/ultra-package.json'}
    packages = {key: json.loads(path.read_text()) for key, path in package_paths.items()}
    packages['A'] = {'zip_bytes': 348968895, 'expanded_bytes': 576934579}
    summary = {'products': grouped, 'packages': packages, 'paired_changes': changes,
               'cpu_percent': 'NOT RELIABLY MEASURED: process counters disagree with thread counters; no conversion from cycles',
               'scope': 'A official base 11; B initial Core; C optimized Core candidate; U0 previous Ultra; U1 optimized Ultra candidate',
               'official_runtime_comparison': 'Descriptive only; official action schedule not controlled to match C',
               'release_boundary': 'Independent measurements use candidate EXE hashes above. Final release binaries are separately GUI/soak validated and attached evidence identifies them.'}
    (ROOT/'benchmarks/public/core-ultra-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    text = '''# Core / Ultra performance report

The official 348.97 MB base ZIP contains **11 clips / 2,651 frames**, not 106.
The earlier Full comparison mislabeled that scope; it is superseded here.

These measurements use three independent starts of each named executable. B/C
and U0/U1 share explicit idle/click/drag timing, positions and warmup. A uses the
official default with movement disabled and is **descriptive only** for runtime
performance. CPU%, GPU, watts and monitor Present are not validated.

| Metric | Official base A | Initial Core B | Optimized Core C | Previous Ultra U0 | Optimized Ultra U1 |
|---|---:|---:|---:|---:|---:|
| Clips / frames | 11 / 2,651 | 11 / 2,651 | 11 / 2,651 | 3 / 723 | 3 / 723 |
'''
    order = ['A', 'B', 'C', 'U0', 'U1']
    for label, field in [('ZIP MB', 'zip_bytes'), ('Expanded MB', 'expanded_bytes')]:
        text += '| '+label+' | '+' | '.join(f'{packages[k][field]/1e6:.2f}' for k in order)+' |\n'
    for label, field in [('Private MB mean / P95 / peak', 'private_bytes'), ('Working Set MB mean / P95 / peak', 'working_set')]:
        text += '| '+label+' | '+' | '.join(' / '.join(f'{grouped[k][field][s]/1e6:.2f}' for s in ['mean', 'p95', 'peak']) for k in order)+' |\n'
    text += '| CPU cycles/s mean (millions) | '+' | '.join(f"{grouped[k]['cycles_per_s']['mean']/1e6:.2f}" for k in order)+' |\n'
    text += '| First Qt paint mean, seconds | Not instrumented | '+' | '.join(f"{grouped[k]['first_qt_paint_s']['mean']:.3f}" for k in order[1:])+' |\n'
    text += '\n## Paired uncertainty\n\nPositive changes mean higher measurements; approximate 95% paired t intervals use only three pairs.\n\n'
    for pair, metrics in changes.items():
        for field, result in metrics.items():
            lo, hi = result['approximate_95pct_paired_t_interval']
            text += f"- {pair} {field}: {result['mean_change_percent']:+.2f}% ({lo:+.2f}% to {hi:+.2f}%).\n"
    gain = (1-packages['C']['zip_bytes']/packages['A']['zip_bytes'])*100
    text += f'\n## Package scope and accepted optimization\n\nCore ZIP is {gain:.2f}% smaller than the audited official base ZIP for the same eleven clips. '
    text += '''This includes removing unrelated app dependencies and using the inherited 72%
display-scale lossless frames; source resolution/storage representation differs.
It is a package-size comparison, not a CPU improvement claim. Ultra has fewer
animations and is compared with its own prior version, not advertised as equivalent
to official Core.

Removing unused Qt translation catalogs saves about 2 MB compressed / 7 MB expanded
per edition. It does not alter character frames, renderer or timer behavior.
Method-6 re-encoding saved only about 3% in the bounded sample; shrinking idle cache
from 40 to 16 MiB increased decoding from 241 to 449 frames over three loops.
The stored-container sample saved tens of microseconds per frame and added
complexity. Those alternatives were rejected. This is not a global-optimum claim.

## Final binary validation boundary

The table is the independently sampled candidate, with exact EXE hashes in the
raw evidence. The final tagged public-source build has separate identity and
archive hashes. Final desktop interaction, installed update/uninstall/reinstall,
long-soak results and exact released ZIP hashes are in the versioned
[RELEASE-VALIDATION.json](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/RELEASE-VALIDATION.json)
attachment. The release does not replace tested local ZIPs with CI rebuilds.
These records must pass before a stable release is published.

Only 100% desktop scaling is physically tested. High DPI, 4K, multi-monitor,
physical network disconnection, GPU, watts and physical Present remain unverified.
Paint intervals are Qt application observations, not monitor presentation.
Process CPU-time counters remain unreliable; thread cumulative times and context
switches are additional diagnostics, not validated CPU% or power measurements.

[Raw independent samples](../benchmarks/public/core-ultra-trials.json) ·
[Complete statistics, threads/handles/I/O and phase samples](../benchmarks/public/core-ultra-summary.json) ·
[Optimization probes](../benchmarks/public/v3-optimization-probes.json) ·
[Methodology](BENCHMARK_METHODOLOGY.md)
'''
    (ROOT/'docs/PERFORMANCE_REPORT.md').write_text(text, encoding='utf-8')
    print(json.dumps(changes))


if __name__ == '__main__':
    main()
