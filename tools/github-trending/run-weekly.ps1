$ErrorActionPreference = "Stop"

$Py = "C:\Users\subrid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Collect = Join-Path $ScriptDir "collect.py"

$Today = Get-Date
$Monday = $Today.Date
while ($Monday.DayOfWeek -ne "Monday") {
    $Monday = $Monday.AddDays(-1)
}
$LastMonday = $Monday.AddDays(-7)

& $Py $Collect --week $LastMonday.ToString("yyyy-MM-dd")
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
