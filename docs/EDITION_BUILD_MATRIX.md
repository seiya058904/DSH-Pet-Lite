# Edition build matrix

| Contract | Core | Ultra |
|---|---|---|
| Explicit build option | `core` | `ultra` |
| Product / EXE | DSH-Pet-Lite-Core | DSH-Pet-Lite-Ultra |
| Source assets | lite/assets-core | lite/assets-ultra |
| Clips / frames | 11 / 2,651 | 3 / 723 |
| Logical canvas | 461x259 | 201x248 |
| Frame cadence | 24 fps | 24 fps |
| Roaming module / curves | Included | Excluded from PYZ and resources |
| Settings directory | %LOCALAPPDATA%/DSH-Pet-Lite-Core | %LOCALAPPDATA%/DSH-Pet-Lite-Ultra |
| Source tests | DSH_TEST_EDITION=core | DSH_TEST_EDITION=ultra |

One shared entry, no upstream application imports. Frozen metadata pins the edition;
a package cannot switch to another edition. Both are separately self-contained.
The CI matrix runs real-asset tests, lint, build, closure and ZIP checks. The local
final binaries separately undergo real desktop and long-run acceptance. The GitHub
Release uploads those exact local bytes, not a different CI rebuild.
