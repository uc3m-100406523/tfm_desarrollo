#! /bin/bash

# Relative base directories
FIKORE_PATH="$HOME/Repositories/5g-network-emulator"

# Iterate along log directories
LOG_DIRS=$(ls $1)
for LOG_DIR in $LOG_DIRS
do
    REAL_LOG_DIR=$(realpath $1)/$LOG_DIR/
    echo "[INFO]: Running draw_sim.py in $REAL_LOG_DIR"
    python3 "$FIKORE_PATH/py_analizers/draw_sim.py" $REAL_LOG_DIR $REAL_LOG_DIR
done
