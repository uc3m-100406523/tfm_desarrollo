#!/bin/bash

# Relative base directories
FIKORE_PATH="$HOME/Repositories/5g-network-emulator"
CONFIG_FILE="$FIKORE_PATH/config/config_template2.ini"

# Python analizers
PY_ANALYZERS="$FIKORE_PATH/py_analizers"
DRAW_SIM="${PY_ANALYZERS}/draw_sim.py"

# Function to generate plots
generatePlots() {
    echo "[INFO] Searching and running analysis scripts..."

    echo "[PLOT] Running draw_sim.py"
    python3 "$DRAW_SIM" || { echo "[ERROR] draw_sim.py failed."; exit 1; }

    echo "[DONE] Plots generated successfully."
}

# If called with argument 'graficas', only plot
if [ "$1" == "graficas" ]; then
    generatePlots
    exit 0
fi

# Run emulator
pushd "$FIKORE_PATH" > /dev/null
echo "[RUN] Running bin/main with ${CONFIG_FILE}"
sudo ./bin/main "$CONFIG_FILE"
RESULT_CODE=$?
popd > /dev/null

# Check emulator result
if [ $RESULT_CODE -ne 0 ]; then
    echo "[ERROR] Emulator execution failed. Aborting."
    exit 1
fi
echo "[INFO] Emulator finished successfully."

# Generate plots
generatePlots
