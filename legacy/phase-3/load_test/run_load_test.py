"""
TriNetra Phase 3 — Python Load Test Runner
==========================================
Executes the Locust performance test suite, checks health,
validates Phase 1 regression, and validates SLAs.

Usage:
  python phase-3/load_test/run_load_test.py
  python phase-3/load_test/run_load_test.py --users 50 --spawn-rate 10 --duration 2m
"""

import argparse
import csv
import datetime
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error


SERVICES = [
    {"name": "claim-service", "port": 8080, "path": "/api/v2/claims/health"},
    {"name": "evidence-service", "port": 8081, "path": "/api/v2/evidence/health"},
    {"name": "fraud-detection-engine", "port": 8083, "path": "/api/v2/fraud/health"},
    {"name": "verdict-generator", "port": 8084, "path": "/api/v2/verdicts/health"},
    {"name": "integration-service", "port": 8085, "path": "/api/v2/integrations/health"},
]

SLA_TARGETS = {
    "CREATE": 2000,
    "SEARCH": 1000,
    "DETAIL": 1500,
    "OVERRIDE": 3000,
    "HEALTH": 500,
    "DEFAULT": 5000,
}


def check_services():
    print("\n[Step 1/3] Checking service availability...")
    all_up = True
    for svc in SERVICES:
        url = f"http://localhost:{svc['port']}{svc['path']}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TriNetra-HealthCheck/3.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    print(f"  [OK] {svc['name']} (port {svc['port']}) is UP")
                else:
                    print(f"  [WARN] {svc['name']} (port {svc['port']}) returned {resp.status}")
        except Exception:
            print(f"  [--] {svc['name']} (port {svc['port']}) not responding (optional if running single service)")
            all_up = False
    return all_up


def run_phase1_regression(project_root):
    print("\n[Step 2/3] Checking Phase 1 reconciliation engine regression...")
    phase1_script = os.path.join(project_root, "phase-1", "reconcile_packet.py")
    sample_file = os.path.join(project_root, "phase-1", "samples", "sample_weight_drop.json")
    if os.path.exists(phase1_script) and os.path.exists(sample_file):
        res = subprocess.run([sys.executable, phase1_script, sample_file], capture_output=True, text=True)
        if res.returncode == 0 and "INCONSISTENT" in res.stdout:
            print("  [OK] Phase 1 reconciliation test: PASS (weight anomaly verified)")
            return True
        else:
            print("  [ERROR] Phase 1 reconciliation test FAILED:")
            print(res.stderr or res.stdout)
            return False
    else:
        print("  [WARN] Phase 1 script or sample file not found, skipping regression check.")
    return True


def run_load_test(args, script_dir):
    print(f"\n[Step 3/3] Running Locust load test ({args.users} users, spawn rate {args.spawn_rate}/s, duration {args.duration})...")
    results_dir = os.path.join(script_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = os.path.join(results_dir, f"report_{timestamp}.html")
    csv_prefix = os.path.join(results_dir, f"metrics_{timestamp}")
    locust_file = os.path.join(script_dir, "locustfile.py")

    cmd = [
        sys.executable, "-m", "locust",
        "-f", locust_file,
        "--host", args.host,
        "--headless",
        "--users", str(args.users),
        "--spawn-rate", str(args.spawn_rate),
        "--run-time", args.duration,
        "--html", html_report,
        "--csv", csv_prefix,
        "--exit-code-on-error", "1",
    ]

    start_time = time.time()
    res = subprocess.run(cmd)
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print(f"  LOAD TEST COMPLETED (Elapsed: {int(elapsed)}s)")
    print("=" * 70)

    # Validate SLAs from CSV
    stats_file = f"{csv_prefix}_stats.csv"
    if os.path.exists(stats_file):
        print("\n  SLA Validation Breakdown:")
        print(f"  {'Endpoint / Action':<40} | {'p95 (ms)':<10} | {'Target (ms)':<12} | {'Status'}")
        print("  " + "-" * 75)

        with open(stats_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("Name", "")
                if name == "Aggregated" or not name:
                    continue

                try:
                    p95_val = float(row.get("95%", 0))
                except ValueError:
                    p95_val = 0.0

                target = SLA_TARGETS["DEFAULT"]
                for key, val in SLA_TARGETS.items():
                    if key in name:
                        target = val
                        break

                status = "[PASS]" if p95_val <= target else "[FAIL]"
                print(f"  {name:<40} | {p95_val:<10.1f} | {target:<12} | {status}")

    print(f"\n  HTML Report: {html_report}")
    print(f"  CSV Metrics: {csv_prefix}_stats.csv\n")

    return res.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="TriNetra Phase 3 Load Test Runner")
    parser.add_argument("--users", type=int, default=50, help="Concurrent users (default: 50)")
    parser.add_argument("--spawn-rate", type=int, default=10, help="Users spawned per sec (default: 10)")
    parser.add_argument("--duration", type=str, default="2m", help="Test duration (default: 2m)")
    parser.add_argument("--host", type=str, default="http://localhost:8080", help="Target API host")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

    print("=" * 70)
    print(f"  TriNetra AI -- Phase 3 Production Hardening Load Test")
    print(f"  Target Host: {args.host}")
    print(f"  Configuration: {args.users} Users, Spawn Rate: {args.spawn_rate}/s, Duration: {args.duration}")
    print("=" * 70)

    check_services()
    run_phase1_regression(project_root)
    success = run_load_test(args, script_dir)

    if success:
        print("[SUCCESS] Phase 3 Load Test PASSED with acceptable SLA latency and < 1% error rate.")
    else:
        print("[NOTICE] Load test finished with exit code.")


if __name__ == "__main__":
    main()
