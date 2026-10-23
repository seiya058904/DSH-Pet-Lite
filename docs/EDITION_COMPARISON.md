# Choose an edition

| | Full Animation Lite | Ultra Lite |
|---|---|---|
| Best for | All original animation clips and local roaming | Basic interaction with a smaller disk footprint |
| Animation | 106 clips / 25,423 frames | 3 clips / 723 frames |
| Input | Click, drag, transparent pass-through, context menu | Same core input contract |
| Roaming | Frame-driven, bounded movement and turns | Absent |
| Runtime | Shared Python / Qt Core, Gui, Widgets | Same core, excludes roaming module |
| Resources | Complete original restored library | Exact historical three-action assets |
| Settings | `DSH-Pet-Lite-Full/settings.json` under LOCALAPPDATA | `DSH-Pet-Lite-Ultra/settings.json` under LOCALAPPDATA |
| Public binary download | Blocked pending asset rights | Blocked pending asset rights |

Both run offline without Harness, a system Python installation, administrator
rights, services, tasks or autostart. Both use one small layered window and stop
the animation timer when paused or hidden. Hidden also releases the idle cache.
Only run one edition for ordinary use; installing both does not require both to run.

Source code is shared, but the ZIPs and on-disk dependency/resource closures are
independent. Ultra does not hide a copy of Full's library behind a setting.
More animation content makes Full larger; this is a product trade-off, not a
performance regression of Ultra. See [performance methodology](BENCHMARK_METHODOLOGY.md).
