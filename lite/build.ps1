param([Parameter(Mandatory)][ValidateSet('core','ultra')][string]$Edition,
      [string]$Output = 'dist/core-ultra', [switch]$SkipTests,
      [string]$Python = '')
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
if (-not $Python) { $Python = Join-Path $root '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $python)) { throw 'Create the isolated .venv and install lite/requirements-build.txt first.' }
$env:DSH_TEST_EDITION = $Edition
if (-not $SkipTests) {
& $python -m pytest -q
if ($LASTEXITCODE) { throw 'Lite tests failed' }
& $python -m ruff check lite
if ($LASTEXITCODE) { throw 'Static checks failed' }
}
$env:DSH_BUILD_EDITION = $Edition
& $python lite/build_identity.py --edition $Edition
if ($LASTEXITCODE) { throw 'Build identity failed' }
$env:DSH_BUILD_INFO = Join-Path $root "build/identity/$Edition/build-info.json"
& $python -m PyInstaller lite/DSH-Pet-Lite.spec --distpath $Output --workpath "build/dual/$Edition" --noconfirm
if ($LASTEXITCODE) { throw 'Build failed' }
& $python lite/verify_bundle.py --edition $Edition --dist $Output
if ($LASTEXITCODE) { throw 'Bundle validation failed' }
& $python lite/package.py --edition $Edition --dist $Output
if ($LASTEXITCODE) { throw 'Zip failed' }
