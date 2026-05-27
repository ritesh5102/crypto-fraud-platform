# Create GitHub repo and push (requires GitHub CLI: https://cli.github.com/)
param(
    [string]$RepoName = "crypto-fraud-intelligence",
    [switch]$Private
)

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "Install GitHub CLI: https://cli.github.com/"
    Write-Host "Then run: gh auth login"
    exit 1
}

$visibility = if ($Private) { "--private" } else { "--public" }
gh repo create $RepoName $visibility --source=. --remote=origin --push
Write-Host "Done: https://github.com/$(gh api user -q .login)/$RepoName"
