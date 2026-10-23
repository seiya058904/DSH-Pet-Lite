# DSH Pet Lite: non-commercial derivative, not an official upstream release

Upstream code: https://github.com/MerZlin/dsh-pet-indesktop
Fixed tag v4.4.0, 59c8bda3d1078155564267fbcb34fff9d2d80aff. MIT; see included LICENSE.

Animation origin: https://github.com/PC2005-cloud/dsh-pet
OC 溟月: 上善无形; community animation preparation. Preserve this attribution.
The upstream notice describes CC BY-NC-SA-like personal/noncommercial conditions;
the origin README permits open source use, prohibits commercial use, and requires
the origin GitHub address in every presentation/distribution of a derivative.
Non-commercial distribution follows the authorization and retained attribution
conditions in ASSET_LICENSE.md. No commercial rights are asserted. The animation is the actual
blue-haired character in the fixed upstream sources, not a whale replacement.
Core includes the official 11 core clips; Ultra includes idle, click-happy and drag only.
Transparent margins were cropped and frames resized to 72% with Lanczos,
then saved as lossless RGBA WebP. See assets/manifest.json and build-info.json
for the actual edition, complete logical frame counts and source identity.
The source attribution/conditions continue to apply to these derived frames.

Runtime dynamically loads unmodified Python 3.12 and PySide6 Essentials /
Shiboken / Qt 6.12.0 DLLs. PySide and Shiboken are used under LGPL-3.0;
Qt Core/Gui/Widgets are used under LGPL-3.0. LGPL and GPL texts are included.
You may replace the dynamically loaded compatible libraries and modify this
application; reverse engineering to debug such modifications is permitted.
Corresponding original sources and build information:
https://code.qt.io/cgit/pyside/pyside-setup.git/tag/?h=v6.12.0
https://code.qt.io/cgit/qt/qtbase.git/tag/?h=v6.12.0
https://doc.qt.io/qtforpython-6/licenses.html
https://doc.qt.io/qt-6/licenses-used-in-qt.html

Qt WebP image plugin is from Qt Image Formats v6.12.0 (LGPL-3.0):
https://code.qt.io/cgit/qt/qtimageformats.git/tag/?h=v6.12.0
It incorporates libwebp, Copyright (c) 2010 Google Inc., BSD-3-Clause;
the complete COPYING and additional patent grant are in licenses/libwebp/.

Python: PSF license and incorporated third-party notices in Python-LICENSE.txt.
The optional Python _hashlib/OpenSSL backend is not shipped in v1.0.1.
Python builtin hashing remains; OpenSSL-LICENSE.txt is retained as historical notice.
PyInstaller bootloader: GPL-2.0-or-later with bootloader distribution exception;
see PyInstaller-COPYING.txt. PyInstaller is a build tool, not a resident service.
Microsoft C/C++ runtime DLLs are unmodified redistributables from the Python/Qt
wheels; they remain subject to Microsoft's runtime distribution terms.

No upstream sounds, OCR engines/models, fonts, network clients, FFmpeg or
multimedia binaries are included in Lite. The retained complete upstream
THIRD_PARTY_NOTICES.md describes upstream components; its inclusion does not
mean those omitted components are present in this package.

Complete corresponding library source archives accompany this Release. See SOURCE-DELIVERY.md.
