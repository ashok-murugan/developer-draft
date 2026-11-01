<#
.SYNOPSIS
  Thin workspace wrapper for TaskOffloaderAgent — fills in --workspace and --profile and delegates to the CLI.

.DESCRIPTION
  Place this file at <workspace>/.task-offloader/task-offloader.ps1.
  The venv is expected at <workspace>/task-offloader-agent/.venv/ (default install location).
  Override $Exe below if you install the package elsewhere.

.EXAMPLE
  # Run from anywhere inside the workspace:
  .task-offloader\task-offloader.ps1 status
  .task-offloader\task-offloader.ps1 profile check
  .task-offloader\task-offloader.ps1 off                     # disable the whole agent (next tool call)
  .task-offloader\task-offloader.ps1 off summarize_logs      # disable one tool
  .task-offloader\task-offloader.ps1 reset summarize_logs    # restore tool to its default
  .task-offloader\task-offloader.ps1 logs logs\app.log --correlation-id abc123
  .task-offloader\task-offloader.ps1 report
#>
$Workspace = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Exe       = Join-Path $Workspace 'task-offloader-agent\.venv\Scripts\task-offloader.exe'
$Profile   = Join-Path $PSScriptRoot 'profile.toml'

if (-not (Test-Path $Exe)) {
    Write-Error "task-offloader is not installed at '$Exe'.`nSee task-offloader-agent\README.md — run: pip install -e . (inside the venv)."
    exit 1
}
& $Exe --workspace $Workspace --profile $Profile @args
exit $LASTEXITCODE

