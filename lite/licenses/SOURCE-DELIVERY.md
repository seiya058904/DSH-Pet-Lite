# Corresponding library sources and replacement

For LGPL-3.0 network distribution, equivalent access to the complete unmodified
corresponding library sources is provided alongside the binary ZIPs, at no charge:
https://github.com/seiya058904/DSH-Pet-Lite/releases/tag/v1.0.1

The application uses unmodified official PyPI PySide6-Essentials 6.12.0 and
shiboken6 6.12.0 wheels. This application does not patch their DLLs.
The source archives include their CMake files, build tooling and bundled third-party
source. PySide setup includes Shiboken sources. Qtbase includes Core, Gui, Widgets,
Windows platform/style and their embedded dependencies; Qtimageformats includes WebP.
Unused Qt translations and unused modules are not distributed.

| Archive | SHA-256 |
|---|---|
| [qtbase-everywhere-src-6.12.0.tar.xz](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/qtbase-everywhere-src-6.12.0.tar.xz) | `a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307` |
| [qtimageformats-everywhere-src-6.12.0.tar.xz](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/qtimageformats-everywhere-src-6.12.0.tar.xz) | `0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762` |
| [pyside-setup-everywhere-src-6.12.0.tar.xz](https://github.com/seiya058904/DSH-Pet-Lite/releases/download/v1.0.1/pyside-setup-everywhere-src-6.12.0.tar.xz) | `099c1a597cf33c1b000e11cf68a0b82d216fb802bf81726efc720394f10c7751` |

Publisher origin URLs and checksums are also recorded in the source repository's
benchmarks/public/library-sources.json. The archives are source deliveries, not
a promise that merely linking an upstream website meets the obligation.

To rebuild on Windows x64, use the official sources' README/CMake instructions
with MSVC, CMake and Ninja, and Python 3.12 for the bindings. Qtbase builds the
Core/Gui/Widgets libraries; configure Qtimageformats against that Qt installation.
Build pyside-setup with its setup.py/build tooling against the matching Qt prefix.
The exact dependency versions used by the app are in lite/requirements-lock.txt.
Upstream build instructions:
https://doc.qt.io/qt-6/windows-building.html
https://doc.qt.io/qtforpython-6/building_from_source/windows.html

For replacement, exit the pet, preserve a rollback copy, and replace the compatible
DLLs/plugins in _internal/PySide6 (and Shiboken libraries in _internal/shiboken6).
Compatible modified libraries may be used and debugged. The program performs no
runtime library hash/signature enforcement. Its separate build verifier is a
release audit tool, not a runtime restriction. Local installer ownership hashes
prevent unsafe overwrites/deletions and do not prevent execution of modified libraries.
The application source and rebuilding instructions are available at the same tag.
Byte-identical rebuilding of the upstream official wheels is not claimed.
