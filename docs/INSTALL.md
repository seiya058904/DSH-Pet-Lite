# Updating to v1.0.1

Use the owned update tool below, or extract the new portable ZIP into a fresh
folder. Overlaying a previous portable folder leaves obsolete duplicate frame
files behind and does not realize the full storage reduction. Settings paths and
schema are unchanged; the owned updater retains the complete previous install.

# Install, switch and remove

The portable ZIP runs directly after extraction. Start the named Core or Ultra EXE.
No Python, Harness, network account, services or administrator access is required.
Run one pet at a time; exit the current pet before switching.

For a per-user install from the source checkout and verified build:

```powershell
powershell -NoProfile -File lite/install.ps1 -Edition core -SourceRoot dist/core-ultra
powershell -NoProfile -File lite/install.ps1 -Edition ultra -SourceRoot dist/core-ultra
```

Each creates its own Desktop/Start Menu shortcut and installs under
%LOCALAPPDATA%/Programs/DSH-Pet-Lite-Core or DSH-Pet-Lite-Ultra. Settings are separate
in %LOCALAPPDATA%/DSH-Pet-Lite-Core and DSH-Pet-Lite-Ultra. No upstream configuration
is silently migrated. Existing destinations or shortcuts are preserved/refused.

Updates through lite/update_edition.py require the old edition to be stopped and
all installation files to match the ownership manifest. Unknown/modified files or
reparse points cause refusal. The previous install and shortcuts are backed up,
and a failed install restores them. Do not remove rollback folders blindly.

To uninstall, exit the pet and run its installed Uninstall-DSH-Pet-Lite.ps1. It
accepts only the exact owned per-user edition directory, checks hashes and removes
only unchanged listed files and verified shortcuts. Empty directories are removed
without recursive deletion. Settings remain by default. Portable directories
without an installed ownership marker are not accepted by that script.

The requesting user's final machine installation is Core only, overriding the
earlier document's default Ultra choice. Ultra is still validated and published
as an independent portable edition. Historical Full archives and user settings
are retained outside the current installation flow.
