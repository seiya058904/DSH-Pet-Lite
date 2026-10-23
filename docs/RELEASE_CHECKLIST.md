# Stable-release gates

The stable Release is published only after these gates pass. The final result
record is [RELEASE-VALIDATION.json](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/RELEASE-VALIDATION.json),
which identifies the actual tested binary and source hashes. This checklist is not
a substitute for that evidence.

| Gate | Evidence / acceptance |
|---|---|
| Core asset scope | Official core hash, eleven matching clip source digests, 2,651 pixel-compared frames |
| Ultra scope | Exactly three clips / 723 unchanged frames; no roaming module or Core movement data |
| Package closure | Real file set/hashes, PYZ and Qt PE imports, licenses, identity, ZIP CRC |
| Source | Clean fixed public commit; no private local Git history copied |
| Software tests | Both edition profiles and ruff; CI uses real tracked assets |
| Desktop input | Real transparent/opaque clicks, drag, menu Exit, relaunch, duplicate suppression |
| Tray | Separate evidence for physical icon clicks and injected notification fallback |
| Stability | Each final EXE: SKIPPED_BY_USER (v4); short stability, complete clips and repeated starts instead; not a long-soak PASS, restore/exit |
| Installation | Owned update/refusal, actual uninstall/reinstall; settings and rollback preserved |
| Performance | Three independent starts per product; matched pair scripts; failures/uncertainty retained |
| Rights | Owner-confirmed non-commercial assets; accurate origin/artist attribution; separate code license |
| Library sources | Complete Qtbase, Qtimageformats, PySide/Shiboken sources, publisher checksums and notices |
| Public download | Both exact tested ZIPs plus checksums, no draft/prerelease; anonymous full download, CRC/hash/entry/license checks |
| Final machine | User-requested Core only installed/running; old owned shortcuts retired; historical assets safe |

No PASS is inferred for untested high DPI, multi-monitor, GPU/power, physical
network disconnection or monitor Present. The original code-only prerelease is
retained unchanged as history and is not the stable binary release.
