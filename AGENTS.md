# DSH Pet Lite public code-only repository

No subagents or remote changes without explicit user authorization.
Preserve user changes. Do not add character art, icons, binaries, private logs or asset downloaders.
Read ASSET_LICENSE.md and docs/BUILD.md. Source launch requires an explicit edition.
Run both DSH_TEST_EDITION profiles, ruff check lite and git diff --check.
Public CI uses DSH_SYNTHETIC_TEST_ASSETS=1 and does not prove product GUI or animation parity.
Keep GUI objects on their owner thread. No polling while hidden/paused.
