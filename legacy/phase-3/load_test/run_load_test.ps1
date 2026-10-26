# TriNetra Phase 3 Load Test Runner
# ===================================
# Runs the Locust load test and validates SLA targets
# Usage: .\phase-3\load_test\run_load_test.ps1
#
# Prerequisites:
#   pip install locust
#   All 5 Spring Boot services must be running (ports 8080-8085)
#
# Arguments (all optional):
#   -Users 50         Number of concurrent users (default: 50)
#   -SpawnRate 10     Users added per second (default: 10)
#   -Duration "5m"    Test duration (default: 5m)
#   -Host "http://localhost:8080"   Target host

param(
    [int]$Users = 50,
    [int]$SpawnRate = 10,
    [string]$Duration = "5m",
    [string]$Host = "http://localhost:8080"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$ResultsDir = "$ScriptDir\results"

# ─── Setup ────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=" * 70
Write-Host "  TriNetra Phase 3 — Load Test"
Write-Host "  Users: $Users | Spawn Rate: $SpawnRate/s | Duration: $Duration"
Write-Host "  Target: $Host"
Write-Host "=" * 70
Write-Host ""

# Create results directory
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$HtmlReport = "$ResultsDir\report_$Timestamp.html"
$CsvPrefix = "$ResultsDir\metrics_$Timestamp"

# ─── Verify Services Health ───────────────────────────────────────────────────

Write-Host "[Step 1/3] Verifying services are up..."

$services = @(
    @{ name = "claim-service";         port = 8080 },
    @{ name = "evidence-service";      port = 8081 },
    @{ name = "fraud-detection-engine"; port = 8083 },
    @{ name = "verdict-generator";     port = 8084 },
    @{ name = "integration-service";   port = 8085 }
)

$allUp = $true
foreach ($svc in $services) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$($svc.port)/api/v2/$($svc.name -replace '-service','s')/health" `
                                  -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($resp.StatusCode -eq 200) {
            Write-Host "  ✅ $($svc.name) (port $($svc.port)) UP"
        } else {
            Write-Host "  ⚠️  $($svc.name) (port $($svc.port)) responded $($resp.StatusCode)"
        }
    } catch {
        Write-Host "  ❌ $($svc.name) (port $($svc.port)) UNREACHABLE - $_"
        $allUp = $false
    }
}

if (-not $allUp) {
    Write-Host ""
    Write-Host "WARNING: Some services are unreachable. Continuing with available services."
    Write-Host "         Run 'docker-compose up' to start all services."
    Write-Host ""
}

# ─── Phase 1 Regression ───────────────────────────────────────────────────────

Write-Host ""
Write-Host "[Step 2/3] Running Phase 1 regression check..."
$phase1Script = "$ProjectRoot\phase-1\reconcile_packet.py"
if (Test-Path $phase1Script) {
    python $phase1Script 2>&1 | Select-String -Pattern "(PASS|FAIL|FN Reduction|p-value)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Phase 1 regression FAILED. Aborting load test." -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Phase 1 regression: PASS"
} else {
    Write-Host "  ⚠️  Phase 1 script not found at $phase1Script — skipping"
}

# ─── Run Load Test ────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[Step 3/3] Running Locust load test ($Users users, $Duration)..."
Write-Host "  Results will be saved to: $ResultsDir"
Write-Host ""

$LocustFile = "$ScriptDir\locustfile.py"

$locustArgs = @(
    "-f", $LocustFile,
    "--host", $Host,
    "--headless",
    "--users", $Users,
    "--spawn-rate", $SpawnRate,
    "--run-time", $Duration,
    "--html", $HtmlReport,
    "--csv", $CsvPrefix,
    "--exit-code-on-error", "1"
)

$startTime = Get-Date
locust @locustArgs
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$elapsed = ($endTime - $startTime).TotalSeconds

# ─── Results Summary ──────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=" * 70
Write-Host "  LOAD TEST COMPLETE"
Write-Host "  Elapsed: $([math]::Round($elapsed, 0))s"
Write-Host "=" * 70

# Parse CSV stats if available
$statsFile = "$CsvPrefix_stats.csv"
if (Test-Path $statsFile) {
    Write-Host ""
    Write-Host "  SLA Validation:"
    $stats = Import-Csv $statsFile

    $slaResults = @()
    foreach ($row in $stats) {
        if ($row.Name -eq "Aggregated") { continue }
        $p95 = [float]($row."95%")
        $name = $row.Name

        $target = switch -Wildcard ($name) {
            "*CREATE*"   { 2000 }
            "*SEARCH*"   { 1000 }
            "*DETAIL*"   { 1500 }
            "*OVERRIDE*" { 3000 }
            "*HEALTH*"   { 500  }
            default      { 5000 }
        }

        $status = if ($p95 -le $target) { "✅ PASS" } else { "❌ FAIL" }
        $slaResults += [PSCustomObject]@{
            Endpoint = $name
            "p95 (ms)" = [math]::Round($p95, 0)
            "Target (ms)" = $target
            Status = $status
        }
    }
    $slaResults | Format-Table -AutoSize
} else {
    Write-Host "  (CSV results not found — check locust output above)"
}

Write-Host ""
Write-Host "  HTML Report: $HtmlReport"
Write-Host "  CSV Metrics: $CsvPrefix_stats.csv"
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "  RESULT: ✅ LOAD TEST PASSED (failure rate < 1%)" -ForegroundColor Green
} else {
    Write-Host "  RESULT: ❌ LOAD TEST FAILED (failure rate >= 1%)" -ForegroundColor Red
}
Write-Host ""
exit $exitCode
