# Core / Ultra benchmark methodology

## Objects and scope

A is the official v4.4.0 no-chat base ZIP, **11 clips / 2,651 frames**, SHA-256
`fa049e31f1b0d184f77639a749f239b55b48c64b2ba14b59d08b3897168b55aa`.
B is the actual first Core candidate built before translation pruning.
C is the optimized Core candidate. U0 is the previously validated three-animation
Ultra; U1 is the optimized Ultra. Exact EXE hashes are included with each trial.

A/C package-size comparisons cover the same eleven clips. Their source pixel
dimensions/storage differ: Lite keeps the established 72% display-scale lossless
frames. Runtime comparisons with A are descriptive: the official action sequence
is not externally controlled to match C. No runtime improvement percentage against
A is claimed. B/C and U0/U1 use the same workload scripts and display conditions.

Historical Full 106 measurements are not current Core results. The prior report's
official-base full-library label was wrong and is explicitly superseded.

## Independent trials

`lite/benchmark_core_ultra.py` alternates products across three fresh process
starts each. No other pet is running during a trial. A separate temporary settings
directory is used for each start; retained source/ZIP artifacts identify baselines.
The collector is external and not shipped in the app.

Each Lite trial warms for 12 seconds, then samples 24 seconds idle (reset every
8 seconds to exclude automatic movement), 8 seconds click, 8 seconds drag,
8 seconds idle, 5 seconds paused and 5 seconds hidden. Sampling is approximately
one second, with real elapsed intervals recorded. Positions and seed are matched
within each pair. A has movement and optional features disabled but retains its
own action scheduling throughout its 58-second sample; its phases are not called
matched pause/hide observations.

Private Bytes, Working Set, threads, handles, read/write I/O, process tree,
connections, process CPU counters, per-thread cumulative time, context switches
and QueryProcessCycleTime are retained. Memory summaries report mean/P95/peak,
sample count and individual runs. Approximate paired t intervals have only three
independent pairs and are correspondingly uncertain. Repeated samples within a
process are not counted as independent starts. Caches are OS-warm, not reboot-cold.

## CPU and rendering limits

Typed GetProcessTimes and fresh psutil process counters have shown zero increments
while cycles advance. Thread cumulative times/context switches add a third
diagnostic route, but disagreement and threads that may terminate between samples
prevent a validated process CPU% claim. No administrator-only ETW session, driver,
system counter policy or global timer/power setting is enabled to force a number.
Cycles are not converted to CPU%, power or energy savings.

First Qt paint is an application proxy, not physical screen presentation. Qt paint
interval distributions are not monitor Present FPS. GPU and watts are not measured.

## Separate final binary acceptance

The final tag is built from a clean public source checkout. Its exact local ZIPs
are subjected to real desktop interaction and final binary soaks, then uploaded
unchanged. Candidate benchmark hashes and final release hashes are distinguished;
CI builds independently validate source and are not substituted for the tested ZIPs.

Each final edition's long-run target is at least 1,800 seconds visible, 300 paused,
300 hidden, then restore and exit. The script visits every clip for its full
duration, including turn preludes. Concurrent stability runs, if used, are labeled
and are not treated as isolated performance comparisons. Separate short independent
trials provide those comparisons. Final results are delivered in the
`RELEASE-VALIDATION.json` release attachment and accompanying benchmark evidence.

Physical pointer tests use an owned backdrop and verify live WindowFromPoint PID
ownership before input. They test transparent pass-through, opaque click, drag,
menu Exit, restart and single-instance behavior. UIA-observed taskbar icon
rectangles are used for attempts at actual tray clicks; Qt-notification fallback
and real icon clicks have distinct result names. Failures remain in the evidence.

Only actual monitor conditions are reported. System resolution/scaling is not
changed. Untested DPI, 4K, multiple monitors, physical disconnect, GPU, watts and
physical Present stay unverified. Images show only the controlled backdrop/menu.
