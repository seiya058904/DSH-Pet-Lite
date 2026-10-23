param([Parameter(Mandatory)][ValidateSet('full','ultra')][string]$Edition)
$ErrorActionPreference = 'Stop'
$suffix = (Get-Culture).TextInfo.ToTitleCase($Edition)
$product = "DSH-Pet-Lite-$suffix"
$target = Join-Path $env:LOCALAPPDATA "Programs\$product\$product.exe"
$shell = New-Object -ComObject WScript.Shell
$rows = @()
foreach ($folder in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
    $path = Join-Path $folder "DSH Pet Lite $suffix.lnk"
    if (Test-Path -LiteralPath $path) {
        $link = $shell.CreateShortcut($path)
        if ($link.TargetPath -ne $target) { throw "Preserving changed shortcut: $path" }
        $rows += [pscustomobject]@{ path = $path; target = $link.TargetPath }
    }
}
ConvertTo-Json -InputObject @($rows) -Compress
