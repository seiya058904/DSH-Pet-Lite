# Character assets and redistribution gate

**Public Full and Ultra binaries: BLOCKED. Code-only distribution is permitted.**

DSH Pet Lite is an unofficial derivative of
[MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop), based on
v4.4.0 (`59c8bda3d1078155564267fbcb34fff9d2d80aff`). Animation origin:
[PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet).
The depicted character is the blue-haired OC **溟月**, attributed by the direct
upstream to artist **上善无形**, with animation prepared by community contributors.
It is not an original character created by this project, and is not a blue whale.

## Separate permissions

The direct upstream's code is MIT licensed, copyright 2026 Merzlin. Its MIT
notice is retained in LICENSE. The animation-origin project's code also carries
an MIT notice, copyright 2026 PC2005-cloud. Code licenses do not grant rights to
the depicted character or all animation assets.

The animation-origin README allows open-source use of animation, prompts and
source videos, prohibits commercial use, and requires its GitHub link wherever
a derivative is introduced, displayed or distributed. This is evidence of an
intended non-commercial derivative ecosystem.

The direct upstream's THIRD_PARTY_NOTICES.md describes the OC material as subject
to CC BY-NC-SA-like personal, non-commercial conditions. It does not specify a
precise Creative Commons version or establish the artist-to-animation-contributor
authorization chain. The word "like" is not an SPDX license identifier.

For this release, those gaps leave material uncertainty about public redistribution
of the character in a new binary, modified frames and promotional screenshots.
Accordingly, neither edition's character assets, executable package, icon,
screenshots nor source Git history containing them is published. This is a
release-gate decision, not a claim that the source authors prohibit all sharing.

## What would unblock binaries

A sufficiently clear statement from the relevant rights holders covering the
character and derived animation, public non-commercial binary redistribution,
screenshots and modified frames, with specific attribution and any share-alike
requirements. No request has been sent on the user's behalf.

Local copies remain for the requesting user's personal non-commercial use.
There is no automatic asset downloader in the public code-only repository.
Supplying a download script would not resolve the authorization gap.

## Software libraries

Local builds dynamically load unmodified PySide6 Essentials / Shiboken / Qt
6.12.0 libraries. LGPL and GPL texts and applicable bundled third-party notices
are in `lite/licenses`. Compatible DLL replacement and debugging modifications
are permitted. A public binary release would also need a complete corresponding
source delivery mechanism or valid offer, beyond simply linking an upstream tag.
The current public release contains source code and notices, not these DLLs.

References checked for this gate:

- [Animation-origin licensing section](https://github.com/PC2005-cloud/dsh-pet#许可)
- [Fixed direct-upstream notice](https://github.com/MerZlin/dsh-pet-indesktop/blob/59c8bda3d1078155564267fbcb34fff9d2d80aff/THIRD_PARTY_NOTICES.md)
- [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations)
- [Qt for Python licenses](https://doc.qt.io/qtforpython-6/licenses.html)
