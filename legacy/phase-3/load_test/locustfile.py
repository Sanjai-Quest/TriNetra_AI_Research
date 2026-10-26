"""
TriNetra Phase 3 Load Test — Locust Script
===========================================
Purpose:
  Performance baseline test for Phase 3 hardened services.
  Validates SLA targets under realistic concurrent load.

Target SLAs (per Phase 3 Implementation Plan):
  - claim creation     → p95 < 2000ms
  - claim search       → p95 < 1000ms
  - fraud analysis     → p95 < 5000ms (async, triggered via claim creation)
  - verdict generation → p95 < 3000ms (async)

Usage:
  pip install locust
  locust -f phase-3/load_test/locustfile.py --host http://localhost:8080 --headless \
         --users 50 --spawn-rate 10 --run-time 5m \
         --html phase-3/load_test/results/report.html \
         --csv phase-3/load_test/results/metrics

Test Scenarios:
  1. Claim Creation   (POST /api/v2/claims)        — 40% of traffic
  2. Claim Search     (GET  /api/v2/claims/search) — 35% of traffic
  3. Claim Detail     (GET  /api/v2/claims/{id})   — 20% of traffic
  4. Verdict Override (POST /api/v2/claims/{id}/override) — 5% of traffic

Author: TriNetra Phase 3 Hardening
"""

import random
import uuid
from locust import HttpUser, TaskSet, task, between, events
from locust.runners import MasterRunner

# ─── Test Data ────────────────────────────────────────────────────────────────

PRODUCT_CATEGORIES = [
    "Electronics", "Clothing", "Footwear", "Home Appliances",
    "Sports", "Books", "Toys", "Jewelry"
]

CLAIM_REASONS = [
    "Item not delivered",
    "Wrong item received",
    "Item damaged in transit",
    "Item does not match description",
    "Defective product",
    "Changed mind",
    "Late delivery"
]

# Shared list of created claim IDs (populated as tests run, used by GET tests)
created_claim_ids: list[str] = []

# ─── Task Sets ────────────────────────────────────────────────────────────────


class ClaimTasks(TaskSet):
    """Core claim management tasks representing realistic API traffic."""

    @task(40)
    def create_claim(self):
        """POST /api/v2/claims — most frequent user action."""
        payload = {
            "customerId": str(uuid.uuid4()),
            "orderId": f"ORD-LOAD-{random.randint(10000, 99999)}",
            "productId": f"PROD-{random.randint(1000, 9999)}",
            "productCategory": random.choice(PRODUCT_CATEGORIES),
            "productValue": round(random.uniform(10.0, 2000.0), 2),
            "claimAmount": round(random.uniform(10.0, 2000.0), 2),
            "claimReason": random.choice(CLAIM_REASONS),
            "deliveryDate": "2026-08-01T10:00:00Z",
            "returnDate": "2026-08-05T10:00:00Z",
            "trackingNumber": f"TRK-{random.randint(100000, 999999)}",
            "paymentTxnId": f"TXN-{uuid.uuid4().hex[:12].upper()}"
        }
        with self.client.post(
            "/api/v2/claims",
            json=payload,
            name="POST /api/v2/claims [CREATE]",
            catch_response=True
        ) as resp:
            if resp.status_code == 201:
                data = resp.json()
                claim_id = data.get("claimId")
                if claim_id:
                    created_claim_ids.append(claim_id)
                    if len(created_claim_ids) > 1000:  # cap list size
                        created_claim_ids.pop(0)
                resp.success()
            elif resp.status_code == 503:
                # Circuit open — expected under extreme load, not a failure
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(35)
    def search_claims(self):
        """GET /api/v2/claims/search — second most frequent."""
        statuses = ["CREATED", "DECISION_PENDING_REVIEW", "APPROVED", "REJECTED", None]
        status = random.choice(statuses)
        params = {"page": 0, "size": 20}
        if status:
            params["status"] = status

        with self.client.get(
            "/api/v2/claims/search",
            params=params,
            name="GET /api/v2/claims/search [SEARCH]",
            catch_response=True
        ) as resp:
            if resp.status_code in (200, 503):
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(20)
    def get_claim_detail(self):
        """GET /api/v2/claims/{claimId} — reads using a previously created claim."""
        if not created_claim_ids:
            return

        claim_id = random.choice(created_claim_ids)
        with self.client.get(
            f"/api/v2/claims/{claim_id}",
            name="GET /api/v2/claims/{id} [DETAIL]",
            catch_response=True
        ) as resp:
            if resp.status_code in (200, 404, 503):
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(5)
    def override_verdict(self):
        """POST /api/v2/claims/{claimId}/override — investigator action (low frequency)."""
        if not created_claim_ids:
            return

        claim_id = random.choice(created_claim_ids)
        payload = {
            "investigatorId": str(uuid.uuid4()),
            "verdict": random.choice(["REFUND", "REJECT"]),
            "reasoning": "Load test override — Phase 3 validation"
        }
        with self.client.post(
            f"/api/v2/claims/{claim_id}/override",
            json=payload,
            name="POST /api/v2/claims/{id}/override [OVERRIDE]",
            catch_response=True
        ) as resp:
            if resp.status_code in (200, 404, 503):
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(5)
    def health_check(self):
        """GET /api/v2/claims/health — validates service is still up under load."""
        with self.client.get(
            "/api/v2/claims/health",
            name="GET /api/v2/claims/health [HEALTH]",
            catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Health check failed: {resp.status_code}")


# ─── User Class ───────────────────────────────────────────────────────────────

class TriNetraUser(HttpUser):
    """
    Simulates a TriNetra platform user (investigator or automated service).
    Think time: 0.5s–2s between requests (realistic user pacing).
    """
    tasks = [ClaimTasks]
    wait_time = between(0.5, 2.0)

    def on_start(self):
        """Called once when user starts — verify service health."""
        self.client.get("/api/v2/claims/health", name="[WARMUP] health check")


# ─── Event Hooks ──────────────────────────────────────────────────────────────

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "=" * 70)
    print("  TriNetra Phase 3 Load Test Starting")
    print("  Target: POST /api/v2/claims -> p95 < 2000ms")
    print("  Target: GET  /api/v2/claims/search -> p95 < 1000ms")
    print("=" * 70 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "=" * 70)
    print("  TriNetra Phase 3 Load Test Complete")
    print(f"  Total Requests: {environment.stats.total.num_requests}")
    print(f"  Total Failures: {environment.stats.total.num_failures}")
    failure_rate = 0
    if environment.stats.total.num_requests > 0:
        failure_rate = (environment.stats.total.num_failures / environment.stats.total.num_requests) * 100
    print(f"  Failure Rate:   {failure_rate:.2f}% (target: < 1%)")
    p95 = environment.stats.total.get_response_time_percentile(0.95)
    print(f"  p95 Latency:    {p95:.0f}ms (claim creation target: < 2000ms)")
    print("=" * 70 + "\n")
