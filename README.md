<div align="center">

# DSH Pet Lite

**The desktop pet you want. Without the software you don't.**

A lightweight, offline Windows desktop companion rebuilt from [dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop).  
Two independent editions: **Core** keeps the official 11-clip starter animation set; **Ultra** keeps just the three essentials.

[![Release](https://img.shields.io/github/v/release/seiya058904/DSH-Pet-Lite?label=stable%20release&style=flat-square)](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.1)
![Platform](https://img.shields.io/badge/platform-Windows%20x64-0078D4?style=flat-square)
![Offline](https://img.shields.io/badge/runtime-100%25%20offline-2E7D32?style=flat-square)
![No Harness](https://img.shields.io/badge/DeepSeek%20Harness-not%20required-555?style=flat-square)

[**Download Core · 117.02 MB**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/DSH-Pet-Lite-Core-v1.0.1-win-x64-portable.zip)
&nbsp; · &nbsp;
[**Download Ultra · 50.24 MB**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/DSH-Pet-Lite-Ultra-v1.0.1-win-x64-portable.zip)
&nbsp; · &nbsp;
[Release & checksums](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.1)

<p>
  <img src="docs/images/core-preview.png" alt="DSH Pet Lite Core running on a controlled Windows desktop test backdrop" width="520">
</p>
<sub>Actual Core desktop preview at 100% scaling. Character artwork is subject to separate non-commercial, attribution-bound terms.</sub>

</div>

---

## Why DSH Pet Lite?

The original desktop pet can do much more than display a character: AI conversations, agent integration, monitoring, media and extended animation packs. Those are useful features, but they also bring more code, dependencies and background machinery.

**DSH Pet Lite deliberately makes a different trade-off:** keep the visible pet, real animations and direct desktop interaction; remove the rest. It is a **focused derivative**, not a full-feature replacement for its upstream.

| **66.5% smaller download** | **73.8% less unpacked storage** | **11/11 official starter clips kept** |
|:---:|:---:|:---:|
| **348.97 → 117.02 MB** | **576.93 → 151.40 MB** | **2,651 / 2,651 frames** |
| Official 11-clip base ZIP → Core | Official 11-clip base → Core | No dropped frames or reduced 24 fps timeline |

The comparison above covers the **same 11 animation clips**, but **not the same software features or source-image dimensions**: Lite uses a fixed 72%-scale, lossless, transparently cropped frame representation. This is a valid package-size comparison, not a claim of identical pixel resolution or equivalent application functionality.

### Current release A/B evidence

The last optimization changes storage and packaging. Three matched independent
starts per edition compare the exact v1.0.0 release EXEs with the v1.0.1 implementation
candidate. These candidate timings are **not substituted for the final tagged EXE**;
its separate hash and measurements are in the release evidence attachment.

| Metric | v1.0.0 Core | Candidate Core | v1.0.0 Ultra | Candidate Ultra |
|---|---:|---:|---:|---:|
| ZIP MB | 123.40 | **117.02** | 53.57 | **50.24** |
| Unpacked MB | 161.13 | **151.40** | 91.57 | **84.86** |
| Private Bytes mean, MB | 50.21 | 50.29 | 48.50 | 48.98 |
| Working Set mean, MB | 78.41 | 75.57 | 73.05 | 73.48 |
| First Qt paint mean, s | 0.165 | 0.173 | 0.170 | 0.168 |

The new benefit is **smaller downloads and installations**. Runtime observations have
three-pair uncertainty and background-system noise; no stable runtime speedup is
claimed. The older official-v4.4.0 comparison used a different action schedule and
remains descriptive history in the performance report. Ultra still has fewer clips.

First Qt paint is an application-side proxy, not monitor Present. CPU time counters
remain unreliable; cycles are not CPU%, GPU use or power savings.

[Full performance report](docs/PERFORMANCE_REPORT.md) · [Methodology](docs/BENCHMARK_METHODOLOGY.md) · [Versioned exploration summary](benchmarks/public/v1.0.1-exploration.json)

## Where the performance and size savings come from

This is not just the upstream app with some checkboxes turned off. The runtime, window model, assets and package have been deliberately reduced.

| Optimization | What changed | Why it matters |
|---|---|---|
| **Small window, not a screen-sized overlay** | One local transparent, always-on-top Qt window replaces the upstream full-screen overlay/sprite-controller stack | Avoids maintaining a desktop-sized overlay and unrelated behavior infrastructure |
| **Minimal execution graph** | The app uses Python standard library and Qt **Core / Gui / Widgets** only | No bundled AI/chat, agent bridge, OCR, screenshot recognition, voice/TTS, audio, media player, network updater or system-monitoring stack |
| **No background polling machinery** | No global mouse hook, cursor polling, full-screen watcher, agent listener or updater loop | Fewer sources of wakeups and unnecessary periodic work; no energy-saving percentage is claimed |
| **One animation clock** | Deadline-based, 24 fps single-shot scheduling; Core movement follows that same clock | No extra high-frequency movement polling or catch-up bursts |
| **Exact duplicate frame storage** | A build-time index maps all logical frames to byte-identical physical WebP files | Saves about 4.46 MB Core / 1.42 MB Ultra of frame payload, without skipping any logical frame or changing its offsets |
| **Optional backend closure** | Exclude Python's unused `_hashlib` / OpenSSL backend; keep builtin hashing, Qt and all notices | Removes about 5.30 MB installed per edition; no new runtime dependency |
| **Load frames when needed** | Small, lossless WebP frames; bounded **40 MiB** hot-idle decoded cache; action frames are transient | Does not load all animations as decoded images into memory |
| **Sleep when invisible** | Pause stops the frame timer; hide stops it **and frees decoded cache** | Avoids continuing animation work when the pet is hidden |
| **Compact animation assets** | The inherited 72%-scale normalization, transparent-margin cropping and asset manifests are retained and verified frame by frame | Smaller shipped images at the supported display scale, without deleting frames or adding lossy recompression |
| **Smaller Windows bundle** | Unneeded Qt plugins/dependencies and unused translation catalogs are excluded | The v1.0.0 translation-pruning pass alone saved about **2 MB compressed / 7 MB unpacked per edition** |
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
| Download | **117.02 MB** | **50.24 MB** |
| Unpacked | **151.40 MB** | **84.86 MB** |
| Download link | [**Get Core for Windows x64**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/DSH-Pet-Lite-Core-v1.0.1-win-x64-portable.zip) | [**Get Ultra for Windows x64**](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/DSH-Pet-Lite-Ultra-v1.0.1-win-x64-portable.zip) |

**Core is the recommended default** if you want the original starter animations and a more expressive companion. **Ultra** is for users who care more about small downloads and minimal behavior. Ultra is a genuinely separate package: it does **not** silently ship Core-only animations or the roaming module.

Both editions include transparent-pixel click-through, direct clicking and dragging, a context menu, tray show/hide/pause/exit controls, saved position, single-instance protection and a native Windows GUI. No account, network connection, administrator rights or DeepSeek Harness is required.

> **About the 106 animations:** the upstream program supports 106 clips across its core and extra asset packs. Its audited **348.97 MB base ZIP embeds 11**, not 106. DSH Pet Lite v1.0.1 releases **Core 11** and **Ultra 3** only; the previous locally tested 106-clip Full build is retired from the public product line.

[Exact Core frame-by-frame audit](docs/CORE_ANIMATION_PARITY.md) · [Edition architecture](docs/EDITION_COMPARISON.md)

## Quick start

1. Download your preferred Windows x64 portable ZIP from the [stable release](https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.1).
2. Extract the **entire** ZIP into a folder and launch `DSH-Pet-Lite-Core.exe` or `DSH-Pet-Lite-Ultra.exe`.
3. Click the character for a reaction, drag to reposition it, or right-click to choose an animation and control the pet.
4. Hide/pause/exit through the pet or tray menu. Double-click the tray icon to show the pet again.

**No separate Python or DeepSeek installation is needed.** The portable folder includes its necessary runtime files. Run one edition at a time; settings are isolated between Core and Ultra.

[SHA-256 checksums](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/SHA256SUMS.txt) · [Install, upgrade and uninstall](docs/INSTALL.md)

## Lean by design — what is intentionally missing?

DSH Pet Lite is **not** an AI assistant, a system monitor or a complete clone of the upstream experience. To stay small, it omits:

- AI chat, LLM keys, agent/work-status integration, OCR and screen analysis;
- TTS, audio/music features, resource downloaders and background network services;
- Multiple simultaneous pets, comprehensive settings pages and extra animation packs;
- Arbitrary pet scaling, advanced throw physics and other full-upstream behaviors.

This is intentional: if you want those features, use [the full upstream application](https://github.com/MerZlin/dsh-pet-indesktop). If you just want an animated companion sitting quietly on your desktop, choose Lite.

## Tested, not merely claimed

- **Core:** 15 local tests. **Ultra:** 14 tests, 1 Core-specific test skipped by design. Two new tests cover all-frame Qt pixel parity and alias recovery.
- The candidate passed real Windows pointer transparency, clicking, dragging, physical tray interaction, context/tray-menu exit and restart at **100% scaling**. Final tagged EXE and installation results are reported separately in the versioned release validation attachment.
- Both public ZIPs have published SHA-256 hashes, verified file inventories and corresponding Qt/PySide6/Shiboken source archives.
- **Limits:** the extended 40-minute stability runs were stopped at the owner's request and are **not** reported as passed. High-DPI probes had unresolved irregularities; true 125%/150% scaling, 4K, multi-monitor, GPU, watts and physical display Present remain unverified. The EXEs are unsigned.
- The final tagged binaries have separate identity, performance and installation/interaction records. A small three-start dataset does not establish a statistically significant runtime speedup or CPU reduction.

[Release validation record](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/RELEASE-VALIDATION.json) · [Benchmark evidence archive](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/BENCHMARKS-v1.0.1.zip) · [CI](https://github.com/seiya058904/DSH-Pet-Lite/actions)

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
