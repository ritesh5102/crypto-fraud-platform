# Publish crypto-fraud-platform to GitHub
# Usage: .\scripts\push-github.ps1 [-RepoName crypto-fraud-intelligence] [-Private]

param(
    [string]$RepoName = "crypto-fraud-intelligence",
    [string]$GitHubUser = "AvishkarMadhwai123",
    [switch]$Private
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$remoteUrl = "https://github.com/$GitHubUser/$RepoName.git"

Write-Host "Project root: $root" -ForegroundColor Cyan

# Refresh PATH for GitHub CLI
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

$gh = Get-Command gh -ErrorAction SilentlyContinue

if ($gh) {
    Write-Host "Using GitHub CLI..." -ForegroundColor Green
    gh auth status 2>&1 | Out-Host
    if (-not (git remote get-url origin 2>$null)) {
        git remote add origin $remoteUrl
    }
    $visibility = if ($Private) { "--private" } else { "--public" }
    gh repo create $RepoName $visibility --source=. --remote=origin --push 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Repo may already exist — pushing to origin main..." -ForegroundColor Yellow
        git push -u origin main
    }
    Write-Host "`nRepository: https://github.com/$GitHubUser/$RepoName" -ForegroundColor Green
    exit 0
}

Write-Host "GitHub CLI (gh) not found." -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Manual push (one-time setup) ===" -ForegroundColor Cyan
Write-Host @"

1. Create an empty repo on GitHub (no README):
   https://github.com/new?name=$RepoName

2. Then run in PowerShell:

   cd `"$root`"
   git remote remove origin 2>`$null
   git remote add origin $remoteUrl
   git branch -M main
   git push -u origin main

3. When prompted, sign in with GitHub (browser or Personal Access Token).

"@ -ForegroundColor White

if (git remote get-url origin 2>$null) {
    Write-Host "Current remote:" (git remote get-url origin)
    $try = Read-Host "Try git push now? (y/n)"
    if ($try -eq "y") {
        git push -u origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Success: $remoteUrl" -ForegroundColor Green
        }
    }
}

exit 1
