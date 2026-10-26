#!/usr/bin/env bash
# ==============================================================================
# TriNetra-Link One-Command End-to-End Reproduction Script
# Protocol Version: 2.6.0 (Amended)
#
# Usage:
#   bash reproduce.sh
# ==============================================================================

set -euo pipefail

echo "======================================================================"
echo "TRINETRA-LINK: END-TO-END REPRODUCIBILITY PIPELINE"
echo "Protocol Amendment v2.6.0 (Algorithm + Dataset Study)"
echo "======================================================================"

# 1. Environment & Python check
echo -e "\n[STEP 1/7] Checking Python Environment..."
python -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'"
echo "Python version: $(python --version)"

# 2. Run Data Linters and Pre-commit Remediation Guards
echo -e "\n[STEP 2/7] Running Remediation Guards & Data Linters..."
python testing/run_remediation_guards.py
python scripts/data_lint.py
echo "[PASS] All repository hygiene and anti-leakage guards verified."

# 3. Execute Complete Test Suite
echo -e "\n[STEP 3/7] Running Test Suite with Coverage..."
pytest tests/ --cov=trinetra_link --cov-report=term-missing
echo "[PASS] All unit and integration tests passed."

# 4. Gate Verification (G-4 Scale Fitting & G-3 Pilot Check)
echo -e "\n[STEP 4/7] Verifying Research Study Gates G-3 and G-4..."
python -m trinetra_link.cli pilot check
echo "[PASS] Gate G-3 pilot check completed and quality floors frozen."

# 5. Staging Cohort Assignment and Stratified Split
echo -e "\n[STEP 5/7] Verifying Staging Cell Assignment and Stratified Split (24 cal / 96 test)..."
python -m trinetra_link.cli staging assign --n 120 --seed 42
python -m trinetra_link.cli split --seed 42
echo "[PASS] Stratified 24 calibration / 96 test split manifest confirmed."

# 6. Fit Hyperparameters on Calibration Split
echo -e "\n[STEP 6/7] Fitting Hyperparameters on Calibration Split..."
python -m trinetra_link.cli fit --split calibration
echo "[PASS] Calibration thresholds fitted without test split leakage."

# 7. Execute All Empirical Experiments (E1, E2, E3)
echo -e "\n[STEP 7/7] Executing Empirical Experiments on 96 Test Journeys..."
RUN_DIR="results/reproduce_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${RUN_DIR}"

echo "--> Running Experiment E1: Primary Comparison vs 5 Baselines..."
python -m trinetra_link.cli eval e1 --split test --output "${RUN_DIR}/e1" --bootstrap 2000

echo "--> Running Experiment E2: Controlled Perturbations..."
python -m trinetra_link.cli eval e2 --split test --output "${RUN_DIR}/e2"

echo "--> Running Experiment E3: Architectural Component Ablations..."
python -m trinetra_link.cli eval ablations --split test --output "${RUN_DIR}/e3"

echo "======================================================================"
echo "[SUCCESS] TRINETRA-LINK REPRODUCTION PIPELINE FINISHED"
echo "Outputs generated:"
echo "  Table III (CSV):   ${RUN_DIR}/e1/table3_primary_comparison.csv"
echo "  Table III (LaTeX): ${RUN_DIR}/e1/table3_primary_comparison.tex"
echo "  Risk-Coverage Fig: ${RUN_DIR}/e1/figure_risk_coverage.png"
echo "  Perturbations Fig: ${RUN_DIR}/e2/figure_robustness.png"
echo "  Ablations Fig:     ${RUN_DIR}/e3/figure_ablations.png"
echo "======================================================================"
