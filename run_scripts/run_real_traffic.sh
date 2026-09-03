#! /bin/bash

# Relative base directories
FIKORE_PATH="$HOME/Repositories/5g-network-emulator"
CONFIG_FILE="$FIKORE_PATH/config/config_car_soft_real_ue.ini"
RULES_PATH="$FIKORE_PATH/run_scripts/iptables_rules.sh"

# Set new iptables rules
sudo "$RULES_PATH"

# Run emulator
sudo "$FIKORE_PATH/bin/main" "$CONFIG_FILE"

# Flush previous iptables rules
sudo iptables -F
sudo iptables -X
