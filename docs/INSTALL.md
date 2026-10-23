# Install, switch, update and uninstall

Public character binaries are currently **not published**. The following describes
the locally built, personally used editions; it is not a public download promise.

Unzip either independent portable archive and run its named executable. No system
Python, Harness or online account is required. Run one edition at a time for
ordinary use. The binaries are unsigned; code signing was not performed.

For a per-user installation from the source workspace:

```powershell
powershell -NoProfile -File lite/install.ps1 -Edition full
powershell -NoProfile -File lite/install.ps1 -Edition ultra
```

The installer refuses an existing destination or shortcut. It creates separate
Desktop and Start Menu links named **DSH Pet Lite Full** / **DSH Pet Lite Ultra**.
Install directories are `%LOCALAPPDATA%/Programs/DSH-Pet-Lite-Full` and
`%LOCALAPPDATA%/Programs/DSH-Pet-Lite-Ultra`. Settings are stored separately under
`%LOCALAPPDATA%/DSH-Pet-Lite-Full` and `%LOCALAPPDATA%/DSH-Pet-Lite-Ultra`.

The legacy `DSH-Pet-Lite` install and settings are preserved. No silent migration
is attempted. The old three-animation backup is retained as a rollback baseline.
Switch by exiting the current edition from its menu, then launching the other link.

To uninstall, exit that edition and run its installed `Uninstall-DSH-Pet-Lite.ps1`.
Only ownership-listed files with matching hashes are removed. Modified or unknown
files remain. Reparse points and paths outside the exact edition directory are
rejected. Settings remain unless `-RemoveConfig` is explicitly confirmed.
Portable folders have no installed ownership marker and are not accepted by this
uninstaller. No services, tasks, autostart or system power settings are created.

Updates must preserve a verified rollback copy and existing settings. An owned
installation can be validated and backed up with `lite/update_edition.py`; it
refuses running processes or changed payload files. Inspect its update report
before considering any retained backup disposable.
