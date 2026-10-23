# v1.0.1 build notes

The source asset tree intentionally retains every original logical frame file.
`pack_assets.py` deduplicates exact encoded bytes into a content-addressed local
build directory; it never deletes previous/unknown output. Reusing that directory
requires an exact file/content match. No new build or runtime dependency is added.
Build identity records both source and packaged manifest SHA-256. Bundle/ZIP gates
verify logical counts and the exact referenced physical set, all PE imports and
absence of `_hashlib`/libcrypto. Tests compare all logical Qt pixels and offsets.

# Build and verify

Windows x64 and Python 3.12.10. The checked-in Core/Ultra images are the authorized
non-commercial inputs, not a hidden dependency on a local Full tree or Git object.
Retain their notices. The application has no asset downloader.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r lite/requirements-lock.txt
$env:DSH_TEST_EDITION = 'core'
$env:QT_QPA_PLATFORM = 'offscreen'
.venv\Scripts\python.exe -m pytest -q
$env:DSH_TEST_EDITION = 'ultra'
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check lite
powershell -NoProfile -File lite/build.ps1 -Edition core
powershell -NoProfile -File lite/build.ps1 -Edition ultra
.venv\Scripts\python.exe lite/verify_bundle.py --edition core --dist dist/core-ultra
.venv\Scripts\python.exe lite/verify_bundle.py --edition ultra --dist dist/core-ultra
git diff --check
```

Builds use lite/DSH-Pet-Lite.spec, separate work paths and explicit embedded edition,
version, source commit and manifest digest. Output is dist/core-ultra. -Python may
select another isolated Python 3.12 environment; no absolute path is baked into
the source instructions. -Output selects a separate staging directory.

The exact original core ZIP SHA-256 is in lite/core-source-map.json. Authorized
source: https://github.com/MerZlin/dsh-pet-indesktop/releases/tag/assets-v1
To audit it against the included normalized assets:

```powershell
.venv\Scripts\python.exe lite/prepare_core.py --source path/to/core.zip --verify-only
```

Omit --verify-only and specify a new --output directory to regenerate the lossless
frames with locked Pillow. Metadata, alpha bounds, every frame and source digests
are checked. Ultra preserves the established three-action assets.

CI uses real checked-in assets for both profiles, lint/tests/build/closure/ZIP CRC.
Optional DSH_SYNTHETIC_TEST_ASSETS=1 is software-only test coverage, never animation
acceptance. Offscreen checks do not prove desktop input or transparency.

Release attachments are the same local final ZIP bytes validated on the desktop;
CI rebuilds are independent checks and are not silently substituted. Complete
corresponding LGPL sources and their hashes accompany the release.
