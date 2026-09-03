#! /bin/bash

# Relative base directories
FIKORE_PATH="$HOME/Repositories/5g-network-emulator"

# Function execute simulation
runSim() {
    # Run emulator
    sudo "$FIKORE_PATH/bin/main" "$CONFIG_FILE"
}

# Iterate along config files
FILES=$(ls $1)
for FILE in $FILES
do
    CONFIG_FILE="$(realpath $1)/$FILE"
    echo $CONFIG_FILE
    runSim
done
