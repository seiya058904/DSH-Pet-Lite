# Performance report

**PARTIAL: local dual editions validated; public dual binaries BLOCKED.**

| Metric | Official full no-chat A | Previous three-action Lite B | Full C | Ultra D |
|---|---:|---:|---:|---:|
| Clips / frames | 106 / 25,423 | 3 / 723 | 106 / 25,423 | 3 / 723 |
| ZIP MB | 348.97 (historical) | 55.60 (historical) | 1,034.44 | 55.62 |
| Expanded MB | 576.93 (historical) | 98.60 (historical) | 1,074.00 | 98.61 |
| Private MB mean / P95 / peak | 75.70 / 77.12 / 77.91 | 54.24 / 54.61 / 54.61 | 57.47 / 58.18 / 59.42 | 54.34 / 54.82 / 54.82 |
| Working Set MB mean / P95 / peak | 114.73 / 116.21 / 117.13 | 78.47 / 78.81 / 78.81 | 82.87 / 83.53 / 84.79 | 78.81 / 79.46 / 79.46 |
| CPU cycles/s mean (millions) | 444.29 | 25.68 | 64.21 | 25.94 |
| First Qt paint mean, seconds | Not instrumented | 0.193 | 0.186 | 0.178 |
| CPU percentage | Not reliable | Not reliable | Not reliable | Not reliable |
| Watts / GPU / physical Present | Not measured | Not measured | Not measured | Not measured |

Memory/cycles use three fresh processes per product, 12-second warm-up then 45 samples per run. B/D are matched idle workloads. A/C use default full-animation behavior with different random schedules; their results are descriptive, not a controlled percentage-improvement claim. First Qt paint is not physical monitor presentation. CPU-time accounting is unreliable.

## Full Animation Lite — Benchmarks

Local ZIP: 1,034,437,183 bytes; expanded: 1,073,996,800 bytes. Visible / paused / hidden soak: 1800.8 / 300.1 / 300.8 seconds. These concurrent soaks are separate from the isolated comparison above.

Visible Qt paint interval P95/P99/maximum: 43.03 / 43.55 / 46.10 ms; 0 intervals exceeded 125 ms. No physical Present FPS is inferred. Pause/hidden stopped the animation timer; hidden cleared the idle cache. Real pointer click/drag, transparent pass-through, actual menu Exit and relaunch passed.

| Phase | Private MB mean / P95 / peak | Working Set MB mean / P95 / peak |
|---|---:|---:|
| visible | 57.80 / 61.33 / 61.60 | 52.13 / 56.27 / 83.22 |
| paused | 61.62 / 61.67 / 61.67 | 54.36 / 54.50 / 54.50 |
| hidden | 29.91 / 29.95 / 29.95 | 22.82 / 22.84 / 22.84 |

[Raw soak samples](../benchmarks/public/full-soak.csv) · [Paint intervals](../benchmarks/public/full-paint-intervals.csv)

## Ultra Lite — Benchmarks

Local ZIP: 55,620,173 bytes; expanded: 98,606,631 bytes. Visible / paused / hidden soak: 1800.7 / 301.0 / 300.2 seconds. These concurrent soaks are separate from the isolated comparison above.

Visible Qt paint interval P95/P99/maximum: 42.98 / 43.45 / 44.47 ms; 0 intervals exceeded 125 ms. No physical Present FPS is inferred. Pause/hidden stopped the animation timer; hidden cleared the idle cache. Real pointer click/drag, transparent pass-through, actual menu Exit and relaunch passed.

| Phase | Private MB mean / P95 / peak | Working Set MB mean / P95 / peak |
|---|---:|---:|
| visible | 56.37 / 57.33 / 57.33 | 53.77 / 80.65 / 80.90 |
| paused | 57.28 / 57.33 / 57.33 | 48.29 / 48.30 / 48.57 |
| hidden | 24.93 / 24.97 / 24.97 | 17.10 / 17.12 / 17.12 |

[Raw soak samples](../benchmarks/public/ultra-soak.csv) · [Paint intervals](../benchmarks/public/ultra-paint-intervals.csv)

### Ultra versus its own baseline

Positive values mean a higher new measurement. Approximate 95% paired t intervals use only three independent pairs.

- private_bytes: +0.19% (-2.52% to +2.90%).
- working_set: +0.43% (-1.83% to +2.70%).
- cycles_per_s: +1.03% (-5.61% to +7.66%).

## Trade-offs & What to Choose

Full preserves all clips and offers bounded roaming; Ultra retains the original three actions. Full lossless frame storage is larger than the official WebM package, so no ZIP-size improvement is claimed. The original 24 fps timeline and input safety outrank lower resource numbers.

Three build-only probes rejected stronger encoding (~3% sampled savings), smaller/no idle cache (more repeated decode work) and a stored container (small absolute warm-cache benefit). This stops these experiments without claiming global optimality. [Probe data](../benchmarks/public/optimization-probes.json).

## Failures and unverified scope

Retained failures include native helper startup, untyped HWND arguments in the test harness, receiver focus/stacking, one focus-sensitive opaque click, and an interrupted pre-fix soak. A missing-frame recovery state bug was fixed and tested before the final packages. An installer module-path failure rolled back the previous install. Successful final GUI checks explicitly activate the owned pet window; the earlier unfocused click failure is not erased.

Only 100% desktop scaling was physically tested. Physical tray-icon clicks, 125%/150% DPI, 4K, multiple monitors/hot-plug, network disconnection, GPU, watts and physical Present remain unverified. The source public CI uses synthetic assets. No character binary or screenshot is publicly distributed.

[Methodology](BENCHMARK_METHODOLOGY.md) · [Full numeric summary](../benchmarks/public/validation-summary.json) · [Independent trials](../benchmarks/public/independent-trials.json) · [Dependency query](../benchmarks/public/dependency-audit.json)
