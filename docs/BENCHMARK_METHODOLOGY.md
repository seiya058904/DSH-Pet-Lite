# Benchmark methodology

## Four products, two meaningful comparison pairs

A is the official v4.4.0 no-chat full-animation Windows package, ZIP SHA-256
`fa049e31f1b0d184f77639a749f239b55b48c64b2ba14b59d08b3897168b55aa`.
B is the previous three-animation Lite, original executable SHA-256
`53be71cf3b04c34cdb71d577aa6eaae913f2e81e21291e2a250b5d260d7e15f4`.
C and D are Full and Ultra built from `c9c52f9fc8dd773c2d619b55d4a78d3de164a33e`.

Compare A with C for full-animation product cost and B with D for the core
three-animation product. C versus D is a functionality/footprint trade-off.
Historical numbers are explicitly marked; old three-action ZIP results are never
presented as Full results. Decimal MB means 1,000,000 bytes; MiB means 1,048,576.

## CPU and process tree

The external sampler enumerates the root and all descendants, with fresh psutil
process objects. It records GetProcessTimes user+kernel totals through typed Win32
calls, psutil totals as a wrapper cross-check, QueryProcessCycleTime, Private Bytes,
Working Set, threads, handles, I/O, connections and system CPU. Rates use actual
monotonic intervals and the host's 16 logical CPUs. Raw cumulative values remain.

Both CPU-time APIs showed long zero increments during active animation while CPU
cycles continued advancing. CPU percentage is **NOT RELIABLY MEASURED**. Cycles
are never converted with guessed clock frequency or described as energy savings.
No driver, global timer resolution, power policy or administrative trace was changed.

## Timing, independent starts and long runs

First Qt paint means completion of the first instrumented `paintEvent`; it differs
from an IsWindowVisible proxy and is not a photometric screen measurement.
Paint-event P95/P99 intervals diagnose application stalls, not compositor Present FPS.
Process-cold starts retain OS file cache; they are not reboot-cold starts. Independent
trials mean fresh processes, not multiple time windows from one process.

The installed-binary stability runs target at least 1,800 seconds visible, 300
paused and 300 hidden, then restore. Full visits every clip via deterministic
controls with time for the complete clip and any turn prelude; Ultra visits its
three clips. Both use a temporary working directory and Windows-only PATH.
The two long runs overlap: their resource values are concurrent stability
observations, not isolated performance comparisons. Background activity is recorded.

Pointer tests use an owned backdrop, live Win32 hit ownership checks, real cursor
clicks/drag and the actual menu Exit row. Test messages inspect state and control
pause/hide; a Qt tray callback verifies restore. A physical tray-icon click is a
separate unverified claim. Failed attempts are retained, including focus-sensitive input.

## Optimization probes

Sampled stronger lossless WebP encoding saved about 3%, below the practical threshold
for replacing all verified assets. A 16 MiB idle cache needed 449 decodes over three
loops versus 241 with the existing 40 MiB limit; no cache needed 723. A stored
container saved only tens of microseconds per sampled Full frame in warm-cache reads.
These build-only probes do not establish end-to-end improvements. No speculative
rewrite or new decoder shipped. [Raw probes](../benchmarks/public/optimization-probes.json).

Normal playback remains 24 fps with every logical frame. Hidden and paused are the
only deliberate stops. Adverse samples and limitations are not discarded.
