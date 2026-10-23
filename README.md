<div align="center">

# DSH Pet Lite

**The desktop pet you want. Without the software you don't.**

A lightweight, offline Windows desktop companion rebuilt from [dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop).  
Two independent editions: **Core** keeps the official 11-clip starter animation set; **Ultra** keeps just the three essentials.

[![Release](https://img.shields.io/github/v/release/seiya058904/DSH-Pet-Lite?label=stable%20release&style=flat-square)](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.0)
![Platform](https://img.shields.io/badge/platform-Windows%20x64-0078D4?style=flat-square)
![Offline](https://img.shields.io/badge/runtime-100%25%20offline-2E7D32?style=flat-square)
![No Harness](https://img.shields.io/badge/DeepSeek%20Harness-not%20required-555?style=flat-square)

[**Download Core · 123.40 MB**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/DSH-Pet-Lite-Core-v1.0.0-win-x64-portable.zip)
&nbsp; · &nbsp;
[**Download Ultra · 53.57 MB**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/DSH-Pet-Lite-Ultra-v1.0.0-win-x64-portable.zip)
&nbsp; · &nbsp;
[Release & checksums](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.0)

<p>
  <img src="docs/images/core-preview.png" alt="DSH Pet Lite Core running on a controlled Windows desktop test backdrop" width="520">
</p>
<sub>Actual Core desktop preview at 100% scaling. Character artwork is subject to separate non-commercial, attribution-bound terms.</sub>

</div>

---

## Why DSH Pet Lite?

The original desktop pet can do much more than display a character: AI conversations, agent integration, monitoring, media and extended animation packs. Those are useful features, but they also bring more code, dependencies and background machinery.

**DSH Pet Lite deliberately makes a different trade-off:** keep the visible pet, real animations and direct desktop interaction; remove the rest. It is a **focused derivative**, not a full-feature replacement for its upstream.

| **64.6% smaller download** | **72.1% less unpacked storage** | **11/11 official starter clips kept** |
|:---:|:---:|:---:|
| **348.97 → 123.40 MB** | **576.93 → 161.14 MB** | **2,651 / 2,651 frames** |
| Official 11-clip base ZIP → Core | Official 11-clip base → Core | No dropped frames or reduced 24 fps timeline |

The comparison above covers the **same 11 animation clips**, but **not the same software features or source-image dimensions**: Lite uses a fixed 72%-scale, lossless, transparently cropped frame representation. This is a valid package-size comparison, not a claim of identical pixel resolution or equivalent application functionality.

### Observed memory footprint

| Measurement | Official v4.4.0 base | Core Lite | Ultra Lite |
|---|---:|---:|---:|
| Included animations | 11 clips / 2,651 frames | **11 clips / 2,651 frames** | **3 clips / 723 frames** |
| Portable ZIP | 348.97 MB | **123.40 MB** | **53.57 MB** |
| Unpacked | 576.93 MB | **161.14 MB** | **91.57 MB** |
| Private Bytes, mean | 75.35 MB | **49.34 MB** | **48.63 MB** |
| Working Set, mean | 114.38 MB | **75.20 MB** | **73.81 MB** |
| First Qt paint, mean | Not instrumented | **0.196 s** | **0.191 s** |

**Measured, with limits:** Core's observed Private Bytes and Working Set are about **34.5%** and **34.3% lower**, respectively, than the official base in these runs. Each figure comes from three independent process starts. **The official app's action schedule was not identical to Core's**, so these are descriptive memory differences, **not controlled proof of a 34% runtime optimization**. Ultra intentionally contains fewer animations and must not be presented as an 11-clip equivalent.

First Qt paint is a Windows/Qt application-side timing proxy, **not** physical monitor presentation. No reliable CPU%, GPU usage or power-savings percentage has been established.

[Full performance report](docs/PERFORMANCE_REPORT.md) · [Test methodology](docs/BENCHMARK_METHODOLOGY.md) · [Raw trial data](benchmarks/public/core-ultra-trials.json)

## Where the performance and size savings come from

This is not just the upstream app with some checkboxes turned off. The runtime, window model, assets and package have been deliberately reduced.

| Optimization | What changed | Why it matters |
|---|---|---|
| **Small window, not a screen-sized overlay** | One local transparent, always-on-top Qt window replaces the upstream full-screen overlay/sprite-controller stack | Avoids maintaining a desktop-sized overlay and unrelated behavior infrastructure |
| **Minimal execution graph** | The app uses Python standard library and Qt **Core / Gui / Widgets** only | No bundled AI/chat, agent bridge, OCR, screenshot recognition, voice/TTS, audio, media player, network updater or system-monitoring stack |
| **No background polling machinery** | No global mouse hook, cursor polling, full-screen watcher, agent listener or updater loop | Fewer sources of wakeups and unnecessary periodic work; no energy-saving percentage is claimed |
| **One animation clock** | Deadline-based, 24 fps single-shot scheduling; Core movement follows that same clock | No extra high-frequency movement polling or catch-up bursts |
| **Load frames when needed** | Small, lossless WebP frames; bounded **40 MiB** hot-idle decoded cache; action frames are transient | Does not load all animations as decoded images into memory |
| **Sleep when invisible** | Pause stops the frame timer; hide stops it **and frees decoded cache** | Avoids continuing animation work when the pet is hidden |
| **Compact animation assets** | The inherited 72%-scale normalization, transparent-margin cropping and asset manifests are retained and verified frame by frame | Smaller shipped images at the supported display scale, without deleting frames or adding lossy recompression |
| **Smaller Windows bundle** | Unneeded Qt plugins/dependencies and unused translation catalogs are excluded | The final translation-pruning pass alone saves about **2 MB compressed / 7 MB unpacked per edition** |
| **No resident helper processes** | Standalone GUI, no Harness, Python installation, FFmpeg helper, service, scheduled task or autostart requirement | A predictable, portable desktop companion without extra runtime services |
| **Write settings only when necessary** | Minimal atomic settings writes on position/state changes and exit | No ongoing configuration-polling or periodic-save work |

Every optimization involves a trade-off. A smaller 16 MiB decoded cache, for instance, **increased repeated frame decoding** in tests, so the 40 MiB limit was retained. More aggressive lossless compression and a custom container were also tested and rejected when their limited gains did not justify additional complexity. See the [optimization evidence](benchmarks/public/v3-optimization-probes.json).

## Choose your edition

| | **Core Lite** | **Ultra Lite** |
|---|---|---|
| Designed for | More lively desktop behavior with the official starter set | Lowest package size and simplest pet behavior |
| Clips | **11** | **3** |
| Frames | **2,651** | **723** |
| Actions | Idle, **5** click reactions, drag, **3** movement clips, turn | Idle, click, drag |
| Movement | Bounded autonomous movement and turning | No roaming module |
| Playback | Original **24 fps** logical timeline | Original **24 fps** logical timeline |
| Download | **123.40 MB** | **53.57 MB** |
| Unpacked | **161.14 MB** | **91.57 MB** |
| Download link | [**Get Core for Windows x64**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/DSH-Pet-Lite-Core-v1.0.0-win-x64-portable.zip) | [**Get Ultra for Windows x64**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/DSH-Pet-Lite-Ultra-v1.0.0-win-x64-portable.zip) |

**Core is the recommended default** if you want the original starter animations and a more expressive companion. **Ultra** is for users who care more about small downloads and minimal behavior. Ultra is a genuinely separate package: it does **not** silently ship Core-only animations or the roaming module.

Both editions include transparent-pixel click-through, direct clicking and dragging, a context menu, tray show/hide/pause/exit controls, saved position, single-instance protection and a native Windows GUI. No account, network connection, administrator rights or DeepSeek Harness is required.

> **About the 106 animations:** the upstream program supports 106 clips across its core and extra asset packs. Its audited **348.97 MB base ZIP embeds 11**, not 106. DSH Pet Lite v1.0.0 releases **Core 11** and **Ultra 3** only; the previous locally tested 106-clip Full build is retired from the public product line.

[Exact Core frame-by-frame audit](docs/CORE_ANIMATION_PARITY.md) · [Edition architecture](docs/EDITION_COMPARISON.md)

## Quick start

1. Download your preferred Windows x64 portable ZIP from the [stable release](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.0).
2. Extract the **entire** ZIP into a folder and launch `DSH-Pet-Lite-Core.exe` or `DSH-Pet-Lite-Ultra.exe`.
3. Click the character for a reaction, drag to reposition it, or right-click to choose an animation and control the pet.
4. Hide/pause/exit through the pet or tray menu. Double-click the tray icon to show the pet again.

**No separate Python or DeepSeek installation is needed.** The portable folder includes its necessary runtime files. Run one edition at a time; settings are isolated between Core and Ultra.

[SHA-256 checksums](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/SHA256SUMS.txt) · [Install, upgrade and uninstall](docs/INSTALL.md)

## Lean by design — what is intentionally missing?

DSH Pet Lite is **not** an AI assistant, a system monitor or a complete clone of the upstream experience. To stay small, it omits:

- AI chat, LLM keys, agent/work-status integration, OCR and screen analysis;
- TTS, audio/music features, resource downloaders and background network services;
- Multiple simultaneous pets, comprehensive settings pages and extra animation packs;
- Arbitrary pet scaling, advanced throw physics and other full-upstream behaviors.

This is intentional: if you want those features, use [the full upstream application](https://github.com/MerZlin/dsh-pet-indesktop). If you just want an animated companion sitting quietly on your desktop, choose Lite.

## Tested, not merely claimed

- **Core:** 13 local tests passed. **Ultra:** 12 passed, 1 Full/Core-specific test skipped by design.
- Both exact release executables passed real Windows pointer transparency, clicking, dragging, physical tray interaction, context/tray-menu exit, restart and install/uninstall validation at **100% desktop scaling**.
- Both public ZIPs have published SHA-256 hashes, verified file inventories and corresponding Qt/PySide6/Shiboken source archives.
- **Limits:** the extended 40-minute stability runs were stopped at the owner's request and are **not** reported as passed. High-DPI probes had unresolved irregularities; true 125%/150% scaling, 4K, multi-monitor, GPU, watts and physical display Present remain unverified. The EXEs are unsigned.
- The final released binaries passed their own installation/interaction checks; the performance table describes separately hashed measurement candidates with the same runtime renderer logic. The small three-start dataset does not establish a statistically significant runtime speedup or CPU reduction.

[Release validation record](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/RELEASE-VALIDATION.json) · [Benchmark evidence archive](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.0/BENCHMARKS-v1.0.0.zip) · [CI](https://github.com/seiya058904/DSH-Pet-Lite/actions/runs/39947606630)

## Build from source

Windows x64 · Python 3.12 · versions pinned in `lite/requirements-lock.txt`. The repository includes the current Core/Ultra build inputs and verification manifests.

See [build instructions](docs/BUILD.md), [benchmark methodology](docs/BENCHMARK_METHODOLOGY.md), and the [release checklist](docs/RELEASE_CHECKLIST.md). The two editions share a tested codebase while shipping separate asset and dependency closures.

## Credits, license and attribution

**Unofficial, non-commercial derivative. Not affiliated with DeepSeek or the upstream maintainers.**

- **Desktop application origin:** [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop) (fixed v4.4.0 source baseline).
- **Animation/project origin:** [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).
- **Character:** OC **溟月**, attributed to artist **上善无形**, with community-prepared animations.
- **Code:** MIT, preserving upstream notices. **Character and animation material:** separate attribution-bound, non-commercial conditions; **not relicensed as MIT**.
- **Distributed Qt libraries:** applicable LGPL and third-party notices, replacement/debugging rights and source-delivery material accompany the release.

The maintainer's stated non-commercial distribution authorization is documented without implying possession of an independently verified signed rights-holder agreement or an exact CC license version.

[Character-asset terms](ASSET_LICENSE.md) · [LICENSE](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Qt/PySide6 source delivery](lite/licenses/SOURCE-DELIVERY.md)
