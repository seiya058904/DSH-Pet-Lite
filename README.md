# DSH Pet Lite

**A small, offline desktop companion. Choose Core or Ultra.**

Unofficial non-commercial derivative of [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop).
Animation origin: [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).
OC **溟月**, artist **上善无形**, community-prepared animation.

[Download v1.0.0](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.0) · [Evidence](docs/PERFORMANCE_REPORT.md) · [Build](docs/BUILD.md) · [Licenses](ASSET_LICENSE.md)

## Choose your edition

| | Core | Ultra |
|---|---|---|
| Best for | The official basic animation set, with local movement | Essential interaction and the smallest package |
| Included clips | **11 / 2,651 frames** | **3 / 723 frames** |
| Actions | Idle, five click reactions, drag, three moves, turn | Idle, click, drag |
| Logical playback | Original 24 fps | Original 24 fps |
| Package size | About **123.4 MB** | About **53.6 MB** |
| Download | [Core Windows x64 ZIP](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/DSH-Pet-Lite-Core-v1.0.0-win-x64-portable.zip) | [Ultra Windows x64 ZIP](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/DSH-Pet-Lite-Ultra-v1.0.0-win-x64-portable.zip) |

[SHA256SUMS](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/SHA256SUMS.txt)

Both are self-contained: no Python installation, Harness, account, online service
or administrator access is required. Each uses one small transparent topmost window
with transparent-pixel input pass-through, click/drag, tray controls, pause, hide,
exit, atomic settings and single-instance protection. No services or autostart.

![Core on an owned test backdrop](docs/images/core-preview.png)
*Actual Core candidate at 100% desktop scaling, captured only over the test backdrop.
Character attribution and non-commercial conditions apply to this image too.*

## Use it

1. Unzip the chosen package into a writable folder.
2. Run `DSH-Pet-Lite-Core.exe` or `DSH-Pet-Lite-Ultra.exe`.
3. Click to interact, drag to move, or right-click for animations and controls.
4. Double-click its tray icon to show it again after hiding. Choose **Exit** to close.

Run one edition at a time. Settings and install directories are separate. The
executables are unsigned. [Install, update and uninstall](docs/INSTALL.md).

## What is actually smaller?

The official v4.4.0 **348.97 MB base ZIP contains 11 clips**, not all 106 clips
supported by the upstream application. Its other 95 animations are separate packs.
Core matches the eleven-clip scope. It removes unrelated application dependencies
and includes lossless frames cropped at the inherited 72% display scale.
Ultra deliberately covers only three clips; its size is not a same-content
comparison with official Core. Historical Full 106-clip experiments are retired.

The latest packaging change removes unused Qt UI translations (the application
never loads a QTranslator), saving about 2 MB compressed and 7 MB installed per
edition. Smaller decoded caches and stronger encoding were tested and rejected
when the benefit was too small or repeated decoding increased. No frame deletion,
fps reduction or unverified lossy encoding is used.

[Measurements and uncertainty](docs/PERFORMANCE_REPORT.md) · [Core frame audit](docs/CORE_ANIMATION_PARITY.md) · [Architecture](docs/EDITION_COMPARISON.md)

## Reproduce

Windows x64, Python 3.12, exact versions in `lite/requirements-lock.txt`.
The repository includes the authorized Core/Ultra asset inputs and their hashes.
The application imports standard Python and Qt Core/Gui/Widgets only; no upstream
chat, OCR, agent, updater, audio or network stack.

[Build and test](docs/BUILD.md) · [Methodology](docs/BENCHMARK_METHODOLOGY.md) · [Release checklist](docs/RELEASE_CHECKLIST.md)

## Boundaries and credits

- Code is MIT under retained upstream notices. Character assets are separate,
  non-commercial and attribution-bound; they are **not relicensed as MIT**.
- Release authorization is the project owner's explicit confirmation; no signed
  third-party permission document or precise Creative Commons version is invented.
- Qt/PySide6/Shiboken source archives accompany the binaries in the same Release,
  with license texts, checksums and replacement/debugging rights.
- Only 100% desktop scaling is physically covered unless a release evidence record
  explicitly adds coverage. 125%/150%, 4K, multiple monitors, physical network
  disconnection, GPU, watts and monitor Present are not claimed as tested.
- CPU process-time counters have been unreliable on the test host. CPU cycles and
  thread-time observations are not claimed as validated CPU% or power savings.
- Core offers bounded movement/turning, not upstream throw physics or extra animations.

[Asset terms](ASSET_LICENSE.md) · [Code license](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Corresponding library source](lite/licenses/SOURCE-DELIVERY.md)
