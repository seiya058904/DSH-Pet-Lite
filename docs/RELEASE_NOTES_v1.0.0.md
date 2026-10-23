# DSH Pet Lite 1.0.0 — code-only public release

**Choose Full** for 106 animation clips and bounded roaming. **Choose Ultra** for
idle/click/drag and the compact three-action resource set. Both are implemented
from one source baseline with independent local Windows packages and settings.

**DUAL_BINARY_RELEASE_BLOCKED.** This public release distributes code and reports
only. Neither Full nor Ultra character binaries, icons, screenshots or animation
files are attached. Public redistribution remains gated by the OC authorization
chain and applicable library-source delivery obligations. Local validation does
not establish permission to publish those materials.

This is an unofficial derivative of [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop).
Animation origin: [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).
OC 溟月 is attributed to artist 上善无形, with community-prepared animation.
Code and non-commercial character-asset conditions are separate.

The local Full and Ultra builds share source `c9c52f9fc8dd773c2d619b55d4a78d3de164a33e`.
The public repository uses sanitized source history and does not contain that
private local Git object. Its source archive is not a standalone pet application.

Read [performance evidence](PERFORMANCE_REPORT.md), [animation coverage](ANIMATION_PARITY.md),
[build instructions](BUILD.md), [install details](INSTALL.md) and [asset gate](../ASSET_LICENSE.md).
Public CI checks both software profiles using synthetic rectangles; it does not
claim real-asset, package or physical GUI acceptance.

Local validation completed: Full 11 tests passed; Ultra 10 passed with the Full-only
roaming test intentionally skipped. Each final executable completed at least 30
minutes visible, five minutes paused and five minutes hidden, then restored and
exited. Physical pointer/menu-exit checks passed after actual uninstall/reinstall.
The four-product comparison used three independent starts per product.

Local package sizes: Full 1,034,437,183 bytes, Ultra 55,620,173 bytes. Independent
Private Bytes means were A 75.70 MB, B 54.24 MB, C 57.47 MB and D 54.34 MB.
Ultra's measured +0.19% change has a 95% interval crossing zero; no clear regression
or improvement is established. CPU-time accounting remains unreliable. Full's
random workload differs from A, so no controlled A-to-C percentage claim is made.

This is a **code-only prerelease**, not the requested completed stable dual-binary
release. The attached source archive and its checksum are the only download artifacts.
