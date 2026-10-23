# Building locally

Windows x64, Python 3.12 and the exact dependencies in `lite/requirements-lock.txt`
were used. The public code-only checkout deliberately contains no character
frames or icon. These commands require separately authorized local asset inputs;
there is no automatic retrieval or redistribution workaround.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r lite/requirements-lock.txt
$env:DSH_TEST_EDITION = 'full'
.venv\Scripts\python.exe -m pytest -q
$env:DSH_TEST_EDITION = 'ultra'
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check lite
powershell -NoProfile -File lite/build.ps1 -Edition full
powershell -NoProfile -File lite/build.ps1 -Edition ultra
.venv\Scripts\python.exe lite/verify_bundle.py --edition full
.venv\Scripts\python.exe lite/verify_bundle.py --edition ultra
git diff --check
```

`build.ps1` runs the selected tests, static checks, PyInstaller, package validation
and ZIP creation. The two builds share a source commit and version, with separate
work and output names. `-SkipTests` is for a build immediately following separately
recorded passing tests; it is not a release-gate waiver. Existing single-edition
`dist/DSH-Pet-Lite` artifacts are not overwritten.

For code-only software tests, set `DSH_SYNTHETIC_TEST_ASSETS=1` and
`QT_QPA_PLATFORM=offscreen`. The fixture creates test rectangles in pytest's
temporary directory. Never describe those tests as real animation validation.

Qt libraries are dynamically loaded from `_internal`. Compatible replacements
may be used for modified-library debugging. The distribution notices and license
texts are retained. See [asset and library distribution conditions](../ASSET_LICENSE.md).
