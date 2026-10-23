param([Parameter(Mandatory)][ValidateSet('core','ultra')][string]$Edition,
      [string]$SourceRoot = 'dist/core-ultra')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$suffix = (Get-Culture).TextInfo.ToTitleCase($Edition)
$product = "DSH-Pet-Lite-$suffix"
$displayName = "DSH Pet Lite $suffix"
$source = Join-Path (Join-Path $root $SourceRoot) $product
$target = Join-Path $env:LOCALAPPDATA "Programs\$product"
if (-not (Test-Path -LiteralPath (Join-Path $source "$product.exe"))) { throw 'Build the verified package first.' }
$identity = Get-Content -LiteralPath (Join-Path $source '_internal/build-info.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($identity.edition -ne $Edition) { throw 'Edition identity mismatch' }
if (Test-Path -LiteralPath $target) { throw "Existing installation requires inspection; preserved: $target" }
$shortcuts = @(
    (Join-Path ([Environment]::GetFolderPath('Desktop')) "$displayName.lnk"),
    (Join-Path ([Environment]::GetFolderPath('Programs')) "$displayName.lnk")
)
foreach ($path in $shortcuts) {
    if (Test-Path -LiteralPath $path) { throw "Preserving pre-existing shortcut: $path" }
}
New-Item -ItemType Directory -Path $target | Out-Null
Get-ChildItem -LiteralPath $source | Copy-Item -Destination $target -Recurse
$shell = New-Object -ComObject WScript.Shell
foreach ($path in $shortcuts) {
    $link = $shell.CreateShortcut($path)
    $link.TargetPath = Join-Path $target "$product.exe"
    $link.WorkingDirectory = $target
    $link.Description = 'DSH Pet Lite - personal noncommercial local derivative'
    $link.IconLocation = (Join-Path $target "$product.exe") + ',0'
    $link.Save()
}
$files = Get-ChildItem -LiteralPath $target -Recurse -File | ForEach-Object {
    [pscustomobject]@{ path = $_.FullName.Substring($target.Length + 1); sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
}
[pscustomobject]@{ product = $product; edition = $Edition; version = 1; files = @($files); shortcuts = $shortcuts } |
    ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $target '.dsh-pet-lite-owner.json') -Encoding UTF8
Write-Output $target
