# Read-only UI Automation of Windows taskbar/overflow; no coordinate guessing.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$children = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)
$rows = @()
foreach ($window in $children) {
    $c = $window.Current
    if ($c.ClassName -notmatch 'Shell_TrayWnd|NotifyIconOverflowWindow|TopLevelWindowForOverflowXamlIsland') { continue }
    $items = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($element in $items) {
        $e = $element.Current
        if ($e.Name -notmatch 'DSH Pet Lite|隐藏的图标|显示隐藏|hidden icons|Show Hidden|溢出' -or $e.IsOffscreen) { continue }
        $r = $e.BoundingRectangle
        $rows += [pscustomobject]@{name=$e.Name; class=$e.ClassName; process=$e.ProcessId; parentClass=$c.ClassName; rect=@($r.Left,$r.Top,$r.Right,$r.Bottom)}
    }
}
ConvertTo-Json -InputObject @($rows) -Compress
