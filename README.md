# DSH Pet Lite

**One offline desktop companion. Two carefully separated editions.**

Unofficial non-commercial derivative of [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop).
Animation origin: [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).

[Choose an edition](#choose-your-edition) · [Release status](#download--release-status) · [Benchmarks](docs/PERFORMANCE_REPORT.md) · [Build](docs/BUILD.md) · [Credits](#credits--licenses)

> **Code-only public release.** Full and Ultra Windows packages have been built locally. Public character-binary redistribution is blocked pending clearer asset authorization. The public repository contains no character images, animation, executable packages or inherited Git history containing them.

## Choose your edition

| | Full Animation Lite | Ultra Lite |
|---|---|---|
| Choose it for | All original animation clips and local roaming | Basic interaction and a compact install |
| Animation | **106 clips · 25,423 frames** | **3 clips · 723 frames** |
| Actions | Idle, click, drag, move, turn, random and visual events | Idle, click and drag |
| Playback | Original 24 fps logical timeline | Original 24 fps logical timeline |
| Portable ZIP, local build | **1,034.44 MB** | **55.62 MB** |
| Public binary download | **Not published — rights gate** | **Not published — rights gate** |

Both provide a small transparent topmost window, native transparent-area input pass-through, click and drag interaction, tray controls, pause, hide and exit. Both work offline without DeepSeek Harness, system Python or administrator rights. They create no services, scheduled tasks or autostart entries.

The code is shared; the packages are independent. Ultra physically excludes Full-only frames and its roaming module. Each edition has separate install/settings directories, shortcuts, build identity and checksums. Normally run only one.

## Download & release status

Public source and release notes are available through [GitHub Releases](https://github.com/seiya058904/DSH-Pet-Lite/releases). There are **no public Full/Ultra character ZIPs**. A code-only release is not a completed dual-binary release: **DUAL_BINARY_RELEASE_BLOCKED**.

The local Windows artifacts are named:

- `DSH-Pet-Lite-Full-v1.0.0-win-x64-portable.zip`
- `DSH-Pet-Lite-Ultra-v1.0.0-win-x64-portable.zip`

These identify local validation outputs, not available public downloads.
[Install and uninstall](docs/INSTALL.md) · [Edition details](docs/EDITION_COMPARISON.md) · [Why binaries are blocked](ASSET_LICENSE.md)

## Evidence, with boundaries

Every Full stored frame was checked against the fixed official frame pack after the inherited 72% resize and transparent crop. Every Ultra encoded frame was checked against the previous three-animation Lite commit. See the [clip-by-clip report](docs/ANIMATION_PARITY.md).

Both editions passed real pointer transparency, click, drag, menu-exit and relaunch checks at 100% desktop scaling. Failed probes are retained locally and summarized publicly. Offscreen CI uses synthetic rectangles and verifies software behavior only; it cannot establish visual, input or package acceptance.

Performance comparisons distinguish official full-animation no-chat (A), previous three-animation Lite (B), new Full (C), and new Ultra (D). CPU cycle counts are not CPU percentages or power measurements. See the [methodology](docs/BENCHMARK_METHODOLOGY.md) and [report](docs/PERFORMANCE_REPORT.md).

## Development

Windows x64 · Python 3.12 · PySide6 Essentials / Qt 6.12.0 · PyInstaller onedir.
The product imports only Python standard-library modules and Qt Core/Gui/Widgets. It imports no upstream chat, agents, OCR, audio, updater or network modules.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r lite/requirements-lock.txt
$env:DSH_TEST_EDITION = 'full' # repeat with ultra
$env:DSH_SYNTHETIC_TEST_ASSETS = '1' # public code-only software tests
$env:QT_QPA_PLATFORM = 'offscreen'
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check lite
```

[Build](docs/BUILD.md) · [Build matrix](docs/EDITION_BUILD_MATRIX.md) · [Changelog](CHANGELOG.md)

## Known limits

- Public character binaries and screenshots are withheld. Source alone cannot recreate the character without authorized assets.
- Supported logical character size is 72%; arbitrary enlargement is not offered.
- 125%/150% DPI, 4K, multi-monitor hot-plug, physical network disconnection, GPU, watts and monitor Present cadence have not been verified.
- Full includes every restored clip, but does not reproduce upstream throw physics, arbitrary multi-loop movement or service-dependent behaviors.
- Native CPU-time accounting is unreliable on the host; no zero-CPU claim. Local executables are unsigned.

## Credits & licenses

Code is MIT licensed under the retained upstream notices. **Character material is separate and is not relicensed as MIT.** OC **溟月** is attributed to artist **上善无形**; animation was prepared by the source community. Non-commercial use and attribution restrictions remain applicable.

- Technical upstream: [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop), fixed v4.4.0.
- Animation and earlier project origin: [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).
- [Code license](LICENSE) · [Asset gate](ASSET_LICENSE.md) · [Third-party notices](THIRD_PARTY_NOTICES.md).

Independently maintained; not an official release of either source project or DeepSeek. Report software issues through this repository's Issues.
