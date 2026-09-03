#! /bin/bash

# Relative base directories
FIKORE_PATH="$HOME/Repositories/5g-network-emulator"
CONFIG_FILE=$1

# Run emulator
sudo "$FIKORE_PATH/bin/main" "$CONFIG_FILE"
