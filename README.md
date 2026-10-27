![A symbolic desktop companion and animation frames](docs/images/readme-cover.svg)

# DSH Pet Lite

An unofficial, offline Windows desktop pet derived from [dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop). Choose the full starter animation set or a smaller edition, then keep the companion on your desktop without a service or account.

[Download Core](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/DSH-Pet-Lite-Core-v1.0.1-win-x64-portable.zip) · [Download Ultra](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/DSH-Pet-Lite-Ultra-v1.0.1-win-x64-portable.zip) · [Release and checksums](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.1)

*Original symbolic illustration, not a screenshot or a depiction of the licensed character.*

## Choose an edition

- **Core:** the 11 animations in the official starter package, including idle, click reactions, dragging, movement, and turning.
- **Ultra:** three animations for idle, click, and drag; it has no autonomous roaming.

Both editions support a transparent, always-on-top pet window, transparent-pixel click-through, saved position, single-instance protection, and tray controls for pause, hide, restore, and quit. They run independently and do not require DeepSeek Harness, a system Python installation, an account, administrator rights, or an internet connection.

![Core desktop pet shown over light and dark Windows backgrounds](docs/images/core-preview.png)

*Core in a real Windows test session at 100% scaling. Character attribution and non-commercial terms apply.*

## Install and use

1. Download the Core or Ultra portable ZIP for Windows x64.
2. Extract the **entire archive** to a normal folder and launch `DSH-Pet-Lite-Core.exe` or `DSH-Pet-Lite-Ultra.exe`.
3. Click the pet to react, drag it to reposition, or use its context menu and tray icon for controls.

Run one edition at a time. The executable needs its accompanying bundled files; do not move the EXE by itself. Neither edition installs a service or automatic startup. The executables are unsigned. See the [installation and removal guide](docs/INSTALL.md) and release checksums before use.

## Design and limits

Core preserves the starter package's logical animation frames and timing using lossless cropped frames at the supported display scale. Ultra is a separate smaller package with fewer clips. The [animation parity record](docs/CORE_ANIMATION_PARITY.md) and [benchmark methodology](docs/BENCHMARK_METHODOLOGY.md) describe what was compared; package-size reductions do not establish a controlled CPU, GPU, power, or startup-speed improvement.

The recorded long soak was canceled and is not a pass. High DPI, 4K and multiple monitors, and physical display presentation remain unverified. In a very narrow logical work area, Core may repeatedly turn when neither side has enough room for its movement step; that observation came from Qt offscreen testing and does not apply to Ultra's movement path. See the [performance report](docs/PERFORMANCE_REPORT.md) for measured results and limitations.

## Build and verify

The source uses Python 3.12, PySide6/Qt, and PyInstaller. On Windows, create an isolated environment and install the locked requirements:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r lite/requirements-lock.txt
$env:QT_QPA_PLATFORM = 'offscreen'
$env:DSH_TEST_EDITION = 'core'
.venv\Scripts\python.exe -m pytest -q
$env:DSH_TEST_EDITION = 'ultra'
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check lite
```

Builds, bundle closure, source-asset checks, and ZIP verification are described in [build notes](docs/BUILD.md). Offscreen tests do not establish real desktop input, transparency, tray behavior, or a completed soak on every system.

## Credits and rights

This is an **unofficial, non-commercial derivative**, not an official release from DeepSeek or either upstream maintainer.

- Desktop-app upstream: [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop); animation and earlier project origin: [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).
- Character: OC **Mingyue**, attributed to **Shangshan Wuxing**, with community-prepared animation. The original-language attribution is preserved in the [asset terms](ASSET_LICENSE.md).
- Code is covered by the [MIT license](LICENSE) with original notices retained. Character artwork and animation are separate, attribution-bound, non-commercial, and subject to the upstream share-alike conditions; they are not MIT-licensed. The owner's recorded non-commercial authorization is not represented as a separately verified signed rights-holder agreement.
- Qt, PySide6, and Shiboken retain their own LGPL terms; see [third-party notices](THIRD_PARTY_NOTICES.md) and [source delivery](lite/licenses/SOURCE-DELIVERY.md).
