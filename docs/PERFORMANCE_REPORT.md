# Core / Ultra performance report

The official 348.97 MB base ZIP contains **11 clips / 2,651 frames**, not 106.
The earlier Full comparison mislabeled that scope; it is superseded here.

These measurements use three independent starts of each named executable. B/C
and U0/U1 share explicit idle/click/drag timing, positions and warmup. A uses the
official default with movement disabled and is **descriptive only** for runtime
performance. CPU%, GPU, watts and monitor Present are not validated.

| Metric | Official base A | Initial Core B | Optimized Core C | Previous Ultra U0 | Optimized Ultra U1 |
|---|---:|---:|---:|---:|---:|
| Clips / frames | 11 / 2,651 | 11 / 2,651 | 11 / 2,651 | 3 / 723 | 3 / 723 |
| ZIP MB | 348.97 | 125.45 | 123.40 | 55.62 | 53.57 |
| Expanded MB | 576.93 | 168.18 | 161.14 | 98.61 | 91.57 |
| Private MB mean / P95 / peak | 75.35 / 76.46 / 76.83 | 49.07 / 51.01 / 51.01 | 49.34 / 51.52 / 51.52 | 48.67 / 50.21 / 50.21 | 48.63 / 50.52 / 50.52 |
| Working Set MB mean / P95 / peak | 114.38 / 115.63 / 116.15 | 75.44 / 79.67 / 79.67 | 75.20 / 80.32 / 80.32 | 74.42 / 78.47 / 78.47 | 73.81 / 78.86 / 78.86 |
| CPU cycles/s mean (millions) | 405.69 | 54.70 | 59.72 | 53.41 | 54.86 |
| First Qt paint mean, seconds | Not instrumented | 0.236 | 0.196 | 0.231 | 0.191 |

## Paired uncertainty

Positive changes mean higher measurements; approximate 95% paired t intervals use only three pairs.

- B->C private_bytes: +0.56% (-1.27% to +2.39%).
- B->C working_set: -0.29% (-3.19% to +2.60%).
- B->C cycles_per_s: +8.77% (-42.98% to +60.52%).
- U0->U1 private_bytes: -0.07% (-2.66% to +2.52%).
- U0->U1 working_set: -0.79% (-4.81% to +3.22%).
- U0->U1 cycles_per_s: +2.46% (-16.68% to +21.60%).

## Package scope and accepted optimization

Core ZIP is 64.64% smaller than the audited official base ZIP for the same eleven clips. This includes removing unrelated app dependencies and using the inherited 72%
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
