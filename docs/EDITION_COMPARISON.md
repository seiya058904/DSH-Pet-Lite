# v1.0.1 storage-only refinement

Build-only `pack_assets.py` creates a deterministic per-clip physical index and
retains every logical frame and offset. Runtime adds one list lookup when an
uncached frame is loaded; cache keys, QImage drawing and scheduling are unchanged.
Python's optional `_hashlib`/OpenSSL backend is excluded. All required Python/Qt
libraries and notices remain. Ultra still has no roaming code or Core assets.

# Core and Ultra

Core embeds only the official core package: 5 click, 3 move, idle, drag and turn,
11 clips / 2,651 frames. Ultra embeds idle/click/drag only, 3 clips / 723 frames.
The 106-clip Full edition and extra1-extra6 are historical local artifacts.

Both use shared app.py, explicit edition.py contracts and separate configuration
roots. Core alone imports roaming.py and its fixed stride curves. One existing
frame timer drives bounded movement; no extra polling timer or worker is added.
The absent random category becomes idle (70/10/20 idle/turn/move). Click chooses
one of the five reactions; every core clip also has a menu entry.

Ultra's PyInstaller module archive excludes roaming.py. It contains neither Core
movement data nor extra frames. verify_bundle.py checks the exact file set and every
asset hash, PYZ imports, Qt PE dependency closure, counts and required licenses.
Its JSON output includes the complete per-file manifest and dependency graph.

Hot idle frames use at most 40 MiB decoded cache; action frames are transient.
Hidden stops the timer and clears cache; pause stops the timer. Atomic writes occur
on relevant user actions and shutdown. Only Core/Ultra are current build options.
