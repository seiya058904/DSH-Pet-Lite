# Build and validation matrix

| Gate | Full | Ultra |
|---|---|---|
| Explicit source selector | `--edition full` | `--edition ultra` |
| Test selector | `DSH_TEST_EDITION=full` | `DSH_TEST_EDITION=ultra` |
| Build selector | `lite/build.ps1 -Edition full` | `lite/build.ps1 -Edition ultra` |
| Resource root | `lite/assets` | `lite/assets-ultra` |
| Executable | `DSH-Pet-Lite-Full.exe` | `DSH-Pet-Lite-Ultra.exe` |
| Expected clips / frames | 106 / 25,423 | 3 / 723 |
| Extra controller | `roaming` | Must be absent from PYZ |
| Extra data | Pinned movement curves | Must be absent |
| Public CI | Synthetic software tests | Synthetic software tests |
| Public character binary CI / Release | BLOCKED | BLOCKED |

Each package embeds `build-info.json` with edition, version, source SHA, dirty-input
flag and manifest SHA-256. A frozen package rejects an attempt to select the other
edition. The package verifier checks the actual PYZ graph, every asset hash, file
closure, required license files and Qt PE imports. It is not merely a flag check.

The public Actions matrix uses synthetic rectangles only. It does **not** certify
the real animation pack, physical Windows input or distributable product binaries.
A green code-only workflow cannot satisfy the blocked dual-binary release gate.
