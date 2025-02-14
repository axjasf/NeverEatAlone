# GitHub Actions Local Testing Script
# Requires: act-cli (https://github.com/nektos/act)

# Configuration
$artifactPath = "./artifacts"
$secretFile = "./.secrets"
$defaultPlatform = "ubuntu-latest=node:16-buster"

# Create artifacts directory if it doesn't exist
if (-not (Test-Path $artifactPath)) {
    New-Item -ItemType Directory -Path $artifactPath
}

function Test-Environment {
    Write-Host "[CHECK] Checking local environment..." -ForegroundColor Cyan

    # Check Docker
    try {
        docker info > $null 2>&1
        Write-Host "[OK] Docker is running" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Docker is not running! Please start Docker Desktop" -ForegroundColor Red
        return $false
    }

    # Check act
    try {
        act --version > $null 2>&1
        Write-Host "[OK] act is installed" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] act is not installed! Please install act-cli" -ForegroundColor Red
        return $false
    }

    # Check secrets file
    if (Test-Path $secretFile) {
        Write-Host "[OK] Secrets file found" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Secrets file not found! Creating template..." -ForegroundColor Yellow
        @"
PYTHON_VERSION=3.11
NODE_VERSION=18
"@ | Out-File $secretFile
    }

    return $true
}

function Test-Job {
    param (
        [Parameter(Mandatory=$true)]
        [string]$JobName
    )

    Write-Host "[RUN] Testing job: $JobName" -ForegroundColor Cyan
    act -j $JobName --secret-file $secretFile --artifact-server-path $artifactPath -P $defaultPlatform

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Job '$JobName' completed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Job '$JobName' failed" -ForegroundColor Red
    }
}

function Test-Workflow {
    Write-Host "[RUN] Testing entire workflow" -ForegroundColor Cyan
    act --secret-file $secretFile --artifact-server-path $artifactPath -P $defaultPlatform

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Workflow completed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Workflow failed" -ForegroundColor Red
    }
}

function Show-Usage {
    Write-Host @"
Local GitHub Actions Testing Tool

Usage:
    ./test-workflow.ps1 [command] [options]

Commands:
    check       - Check local environment
    test-job    - Test specific job (requires -JobName)
    test-all    - Test entire workflow
    help        - Show this help message

Options:
    -JobName    - Name of the job to test (required for test-job)

Examples:
    ./test-workflow.ps1 check
    ./test-workflow.ps1 test-job -JobName backend-lint
    ./test-workflow.ps1 test-all
"@ -ForegroundColor Yellow
}

# Main execution
$command = $args[0]

switch ($command) {
    "check" {
        Test-Environment
        break
    }
    "test-job" {
        if ($args.Length -lt 2) {
            Write-Host "[ERROR] Please specify a job name" -ForegroundColor Red
            Show-Usage
            return
        }
        if (Test-Environment) {
            Test-Job -JobName $args[1]
        }
        break
    }
    "test-all" {
        if (Test-Environment) {
            Test-Workflow
        }
        break
    }
    default {
        Show-Usage
        break
    }
}
