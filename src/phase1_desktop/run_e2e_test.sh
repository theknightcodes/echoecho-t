#!/usr/bin/env bash
set -euo pipefail

# EchoEcho-T Phase 1 — Real-Speech E2E Test Runner
# Usage: ./run_e2e_test.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs

LOG_FILE="logs/e2e_test_$(date +%Y%m%d_%H%M%S).log"
CONDA_ENV="${ECHOECHO_CONDA_ENV:-echoecho-t}"

echo "========================================"
echo "EchoEcho-T — Real-Speech E2E Test"
echo "========================================"
echo "Conda env : ${CONDA_ENV}"
echo "Log file  : ${LOG_FILE}"
echo "========================================"

# Activate environment (conda preferred, venv fallback)
if command -v conda &>/dev/null; then
    # shellcheck source=/dev/null
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if conda env list | grep -q "^${CONDA_ENV} "; then
        conda activate "$CONDA_ENV"
        echo "Activated conda environment: ${CONDA_ENV}"
    else
        echo "Warning: conda env '${CONDA_ENV}' not found. Trying project venv..."
        if [ -f "venv/bin/activate" ]; then
            # shellcheck source=/dev/null
            source venv/bin/activate
            echo "Activated project venv."
        else
            echo "Warning: No venv found. Using system Python."
        fi
    fi
elif [ -f "venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source venv/bin/activate
    echo "Activated project venv."
else
    echo "Warning: No conda or venv found. Using system Python."
fi

# Run the real-speech test: 60 seconds, default Tamil, log to timestamped file
python tests/test_real_speech.py 60 ta "$LOG_FILE"
