#! /bin/bash



# General settings

# Relative base directories
UL_DATA_PATH="$HOME/cap/video_ul.txt"
DL_DATA_PATH="$HOME/cap/video_dl.txt"

# Network variables
LOCAL_IP=192.168.1.139
FOREIGN_IP=192.168.1.56
COUNT_DL=40000 # Approximately, 100 packets are 30 s
COUNT_UL=40000 # Approximately, 100 packets are 30 s

# Filters
FILTER_ALL="(port 443 or port 5228 or port 80) and (tcp or udp)" # All packets
CHROME_DST="(port 443 or port 5228 or port 80) and (tcp or udp) and dst $LOCAL_IP" # Uplink
CHROME_SRC="(port 443 or port 5228 or port 80) and (tcp or udp) and src $LOCAL_IP" # Downlink
SSH_DST="(port 22) and (tcp or udp) and dst $LOCAL_IP" # Uplink
SSH_SRC="(port 22) and (tcp or udp) and src $LOCAL_IP" # Downlink
MUMBLE_DST="(tcp or udp) and dst $FOREIGN_IP" # Uplink
MUMBLE_SRC="(tcp or udp) and src $FOREIGN_IP" # Downlink

FILTER_DST=$CHROME_DST
FILTER_SRC=$CHROME_SRC



# Show important information

echo "-----------------------"
echo "| Network information |"
echo "-----------------------"
echo
echo "  1. IP address"
echo
ip -f inet address show
echo
echo "  2. MAC address"
echo
ip -f inet link show
echo
echo "  3. Neighbouring devices"
echo
ip -f inet neighbour show
echo



# Test filters

# echo "Capturing packets for: $FILTER_DST"
# echo
# sudo tcpdump -n -i wlp0s20f3 "$FILTER_DST"
# echo



# Print on standard output

# echo "Capturing and processing $COUNT packets for:"
# echo "    - Filter 1: $FILTER_DST"
# echo "    - Filter 2: $FILTER_SRC"
# echo
# echo "--------------"
# echo "| UL packets |"
# echo "--------------"
# echo
# tcpdump -n -i wlp0s20f3 -ttttt -l -c $COUNT $FILTER_SRC | gawk '{
#     split($1, time_parts, ":");
#
#     hours = time_parts[1];
#     minutes = time_parts[2];
#     seconds = time_parts[3];
#
#     current_delta = (hours * 3600) + (minutes * 60) + seconds;
#
#     p_len=0
#     for(i=0;i>-1;i++) {
#         if($i=="length") {
#             p_len=$(i+1)
#             break
#         }
#     }
#
#     print current_delta, p_len
# }'
# echo
# echo "--------------"
# echo "| DL packets |"
# echo "--------------"
# echo
# tcpdump -n -i wlp0s20f3 -ttttt -l -c $COUNT $FILTER_DST | gawk '{
#     split($1, time_parts, ":");
#
#     hours = time_parts[1];
#     minutes = time_parts[2];
#     seconds = time_parts[3];
#
#     current_delta = (hours * 3600) + (minutes * 60) + seconds;
#
#     p_len=0
#     for(i=0;i>-1;i++) {
#         if($i=="length") {
#             p_len=$(i+1)
#             break
#         }
#     }
#
#     print current_delta, p_len
# }'
# echo



# Capture a given number of packets

echo "Capturing and processing $COUNT_DL (DL) and $COUNT_UL (UL) packets for:"
echo "    - Filter 1: $FILTER_DST"
echo "    - Filter 2: $FILTER_SRC"
echo
echo "Captured packets will be stored in $DL_DATA_PATH, $UL_DATA_PATH"
echo
echo "--------------"
echo "| UL packets |"
echo "--------------"
echo
tcpdump -n -i wlp0s20f3 -ttttt -l -c $COUNT_UL $FILTER_SRC | gawk '{
    split($1, time_parts, ":");

    hours = time_parts[1];
    minutes = time_parts[2];
    seconds = time_parts[3];

    current_delta = (hours * 3600) + (minutes * 60) + seconds;

    p_len=0
    for(i=0;i>-1;i++) {
        if($i=="length") {
            p_len=$(i+1)
            break
        }
    }

    print current_delta, p_len >> "'"$UL_DATA_PATH"'"
}' &
echo
echo "--------------"
echo "| DL packets |"
echo "--------------"
echo
tcpdump -n -i wlp0s20f3 -ttttt -l -c $COUNT_DL $FILTER_DST | gawk '{
    split($1, time_parts, ":");

    hours = time_parts[1];
    minutes = time_parts[2];
    seconds = time_parts[3];

    current_delta = (hours * 3600) + (minutes * 60) + seconds;

    p_len=0
    for(i=0;i>-1;i++) {
        if($i=="length") {
            p_len=$(i+1)
            break
        }
    }

    print current_delta, p_len >> "'"$DL_DATA_PATH"'"
}' &
echo



# Capture until Ctrl-C
#
# tcpdump -n -i wlp0s20f3 -ttttt -l '(port 443 or port 5228 or port 80) and (tcp or udp)' | gawk '{
#     split($1, time_parts, ":");
#
#     hours = time_parts[1];
#     minutes = time_parts[2];
#     seconds = time_parts[3];
#
#     current_delta = (hours * 3600) + (minutes * 60) + seconds;
#
#     p_len=0
#     for(i=0;i>-1;i++) {
#         if($i=="length") {
#             p_len=$(i+1)
#             break
#         }
#     }
#
#     print current_delta, p_len >> "'"$UL_DATA_PATH"'"
#     fflush()
# }'
