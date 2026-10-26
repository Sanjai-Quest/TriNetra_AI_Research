#!/usr/bin/env python3
"""
Test: Validation script must fail explicitly when the backend is offline.

Ensures that real_world_validation.py never produces simulated metrics,
fabricated latency percentiles, or SLA verdicts when the backend is
unreachable (audit Finding F-07, remediation item C-14).
"""

import os
import subprocess
import sys

TESTING_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "testing",
)
VALIDATION_SCRIPT = os.path.join(TESTING_DIR, "real_world_validation.py")


def test_validation_exits_nonzero_when_backend_offline():
    """
    Run real_world_validation.py without a backend running.
    Assert:
      - Exit code >= 2
      - stdout contains 'BLOCKED'
      - stdout does NOT contain 'SIMULATED'
      - stdout does NOT contain 'SLA: PASS'
      - stdout does NOT contain hardcoded latency '142' in 'p50' context
    """
    # Ensure no backend is running on 8080 for this test.
    # The test assumes port 8080 is not serving the TriNetra API.
    env = os.environ.copy()
    # Override any proxy that might interfere
    env.pop("HTTP_PROXY", None)
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, VALIDATION_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        env=env,
        cwd=TESTING_DIR,
    )

    output = result.stdout + result.stderr

    # 1. Must exit with non-zero code (specifically >= 2)
    assert result.returncode >= 2, (
        f"Expected exit code >= 2 when backend is offline, "
        f"got {result.returncode}.\nOutput:\n{output[:500]}"
    )

    # 2. Must contain BLOCKED message
    assert "BLOCKED" in output, (
        f"Expected 'BLOCKED' in output when backend is offline.\n"
        f"Output:\n{output[:500]}"
    )

    # 3. Must NOT contain 'SIMULATED' verdict
    assert "SIMULATED" not in output, (
        f"Output must not contain 'SIMULATED' when backend is offline — "
        f"fabricated metrics are prohibited.\nOutput:\n{output[:500]}"
    )

    # 4. Must NOT contain 'SLA: PASS'
    assert "SLA: PASS" not in output, (
        f"Output must not contain 'SLA: PASS' when backend is offline.\n"
        f"Output:\n{output[:500]}"
    )

    print("[PASS] test_validation_exits_nonzero_when_backend_offline")


def test_no_hardcoded_simulation_values_in_source():
    """
    Static analysis: verify that real_world_validation.py no longer contains
    the hardcoded simulation fallback values.
    """
    with open(VALIDATION_SCRIPT, "r", encoding="utf-8") as f:
        source = f.read()

    # The original fabrication block contained these exact patterns:
    forbidden_patterns = [
        'p50, p95, p99, avg   = 142, 267, 398, 178',
        'backend_correct      = 18',
        '"18/20 (Simulated',
        'r["verdict"]  = "SIMULATED"',
        'r["correct"]  = True',
    ]
    for pattern in forbidden_patterns:
        assert pattern not in source, (
            f"Source still contains fabrication pattern: {pattern!r}\n"
            f"The offline simulation fallback has not been fully removed."
        )

    print("[PASS] test_no_hardcoded_simulation_values_in_source")


if __name__ == "__main__":
    test_no_hardcoded_simulation_values_in_source()
    # Only run the subprocess test if explicitly requested (it requires
    # no backend on port 8080, which is the expected CI state).
    if "--run-offline" in sys.argv:
        test_validation_exits_nonzero_when_backend_offline()
    else:
        print("[INFO] Skipping subprocess test (pass --run-offline to enable)")
    print("\nAll executed tests passed.")
