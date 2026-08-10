#!/bin/bash
cd ~/murk-runners
git add tasks_data.json MURK_STATE_SUMMARY.md
if ! git diff-index --quiet HEAD --; then
    echo "[Git Engine] Telemetry log changes detected. Initiating isolated branch push..."
    git commit -m "Hourly operational sync: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin telemetry-logs
else
    echo "[Git Engine] No log changes detected. Skipping sync."
fi
