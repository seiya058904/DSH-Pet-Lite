param([switch]$RemoveConfig)
$ErrorActionPreference = 'Stop'
$target = [IO.Path]::GetFullPath($PSScriptRoot)
$identity = Get-Content -LiteralPath (Join-Path $target '_internal/build-info.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($identity.edition -notin @('full','ultra')) { throw 'Unknown edition' }
$suffix = (Get-Culture).TextInfo.ToTitleCase($identity.edition)
$product = "DSH-Pet-Lite-$suffix"
$displayName = "DSH Pet Lite $suffix"
$expected = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA "Programs\$product"))
if ($target -ne $expected) { throw 'Run this script only from the actual per-user Lite installation.' }
if ((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Refusing reparse-point installation.' }
$markerPath = Join-Path $target '.dsh-pet-lite-owner.json'
$owner = Get-Content -LiteralPath $markerPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($owner.product -ne $product) { throw 'Missing Lite ownership evidence; refusing removal.' }
$running = Get-Process -Name $product -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq (Join-Path $target "$product.exe") }
if ($running) { throw 'Exit DSH Pet Lite using its tray menu, then run uninstall again.' }
$directories = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($file in $owner.files) {
    $path = [IO.Path]::GetFullPath((Join-Path $target $file.path))
    if (-not $path.StartsWith($target + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Manifest path escapes installation.' }
    if (-not (Test-Path -LiteralPath $path)) { continue }
    $item = Get-Item -LiteralPath $path
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing reparse point: $path" }
    $parent = $item.Directory
    while ($parent -and $parent.FullName -ne $target) {
        if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Refusing reparse-point ancestor.' }
        [void]$directories.Add($parent.FullName)
        $parent = $parent.Parent
    }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $file.sha256) {
        Remove-Item -LiteralPath $path -Force
    } else { Write-Warning "Preserved modified file: $path" }
}
$shell = New-Object -ComObject WScript.Shell
foreach ($path in $owner.shortcuts) {
    $allowed = @((Join-Path ([Environment]::GetFolderPath('Desktop')) "$displayName.lnk"), (Join-Path ([Environment]::GetFolderPath('Programs')) "$displayName.lnk"))
    if ($path -in $allowed -and (Test-Path -LiteralPath $path)) {
        $link = $shell.CreateShortcut($path)
        if ($link.TargetPath -eq (Join-Path $target "$product.exe")) { Remove-Item -LiteralPath $path }
    }
}
# Empty directories only; unknown or modified files are never recursively removed.
foreach ($dir in ($directories | Sort-Object Length -Descending)) {
    if (-not (Get-ChildItem -LiteralPath $dir -Force)) { [IO.Directory]::Delete($dir) }
}
Remove-Item -LiteralPath $markerPath
if (-not (Get-ChildItem -LiteralPath $target -Force)) { [IO.Directory]::Delete($target) }
if ($RemoveConfig) {
    $answer = Read-Host 'Delete only Lite settings.json? Type DELETE to confirm; all other configs stay'
    if ($answer -ceq 'DELETE') {
        $config = Join-Path $env:LOCALAPPDATA "$product\settings.json"
        if (Test-Path -LiteralPath $config) { Remove-Item -LiteralPath $config }
    }
}
Write-Output 'Lite files removed where unchanged. Configuration retained unless explicitly confirmed.'
