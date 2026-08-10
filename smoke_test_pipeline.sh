#!/bin/bash

# Murk Audio Automation Stack Smoke Test Harness
# Systems Framework: v6.20 Relational Schema

RUNNER_DIR="/Users/jameswilliams/murk-runners"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "================================================================="
echo "INITIALIZING MURK AUDIO PIPELINE SMOKE TEST: $TIMESTAMP"
echo "================================================================="

run_test() {
    local script_name=$1
    echo -n "[TEST] Running $script_name... "
    
    output=$(python3 "$RUNNER_DIR/$script_name" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "\033[0;32mPASSED\033[0m"
        echo "       $output" | grep -E "(Success|Authorized|Captured|Locked)"
    else
        echo -e "\033[0;31mFAILED (Exit Code: $exit_code)\033[0m"
        echo "       Error Context: $output"
    fi
    echo "-----------------------------------------------------------------"
}

# Enforce Execution Order based on System Dependency Rows
run_test "intel_scraper.py"
run_test "marketing_scraper.py"
run_test "social_velocity_scraper.py"
run_test "press_monitor_scraper.py"
run_test "ks_health_monitor.py"
run_test "grants_scraper.py"
run_test "runner_ashley.py"
run_test "runner_hughie.py"

echo "================================================================="
echo "SMOKE TEST INTEGRATION RUN COMPLETE."
echo "================================================================="
