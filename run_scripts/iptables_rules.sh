#! /bin/bash



# Flush previous iptables rules
sudo iptables -F
sudo iptables -X



# Set new iptables rules

# Connections list
# CON_1_UL=0
# CON_1_DL=1
# CON_2_UL=2
# CON_2_DL=3
# CON_3_UL=4
# CON_3_DL=5

# All traffic with running host
# LOCAL_IP=192.168.1.45
# sudo iptables -I INPUT -p tcp --src $LOCAL_IP -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p tcp --dst $LOCAL_IP -j NFQUEUE --queue-num 0 # DL ACK
# sudo iptables -I INPUT -p udp --src $LOCAL_IP -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p udp --dst $LOCAL_IP -j NFQUEUE --queue-num 0 # DL ACK

# Web browser
# BROWSER_PORT1=443
# BROWSER_PORT2=80
# sudo iptables -I OUTPUT -p tcp --dport $BROWSER_PORT1 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
# sudo iptables -I INPUT -p tcp --sport $BROWSER_PORT1 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
# sudo iptables -I OUTPUT -p udp --dport $BROWSER_PORT1 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
# sudo iptables -I INPUT -p udp --sport $BROWSER_PORT1 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
# sudo iptables -I OUTPUT -p tcp --dport BROWSER_PORT2 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
# sudo iptables -I INPUT -p tcp --sport BROWSER_PORT2 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
# sudo iptables -I OUTPUT -p udp --dport BROWSER_PORT2 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
# sudo iptables -I INPUT -p udp --sport BROWSER_PORT2 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA

# Google Chrome
CHROME_PORT1=443
CHROME_PORT2=5228
CHROME_PORT3=80
sudo iptables -I OUTPUT -p tcp --dport $CHROME_PORT1 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
sudo iptables -I INPUT -p tcp --sport $CHROME_PORT1 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
sudo iptables -I OUTPUT -p udp --dport $CHROME_PORT1 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
sudo iptables -I INPUT -p udp --sport $CHROME_PORT1 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
sudo iptables -I OUTPUT -p tcp --dport $CHROME_PORT2 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
sudo iptables -I INPUT -p tcp --sport $CHROME_PORT2 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
sudo iptables -I OUTPUT -p udp --dport $CHROME_PORT2 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
sudo iptables -I INPUT -p udp --sport $CHROME_PORT2 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
sudo iptables -I OUTPUT -p tcp --dport $CHROME_PORT3 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
sudo iptables -I INPUT -p tcp --sport $CHROME_PORT3 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA
sudo iptables -I OUTPUT -p udp --dport $CHROME_PORT3 -j NFQUEUE --queue-num 0 # UL DATA / DL ACK
sudo iptables -I INPUT -p udp --sport $CHROME_PORT3 -j NFQUEUE --queue-num 1 # UL ACK / DL DATA

# SSH connections
# SSH_PORT=22
# sudo iptables -I OUTPUT -p tcp --dport $SSH_PORT -j NFQUEUE --queue-num 2 # UL DATA / DL ACK
# sudo iptables -I INPUT -p tcp --sport $SSH_PORT -j NFQUEUE --queue-num 3 # UL ACK / DL DATA
# sudo iptables -I OUTPUT -p udp --dport $SSH_PORT -j NFQUEUE --queue-num 2 # UL DATA / DL ACK
# sudo iptables -I INPUT -p udp --sport $SSH_PORT -j NFQUEUE --queue-num 3 # UL ACK / DL DATA

# Simple host
# LOCAL_IP=192.168.1.45
# REMOTE_IP=192.168.1.52
# sudo iptables -I INPUT -p tcp --dst $REMOTE_IP --src $LOCAL_IP -j NFQUEUE --queue-num 0 # UL DATA
# sudo iptables -I INPUT -p tcp --src $REMOTE_IP --dst $LOCAL_IP -j NFQUEUE --queue-num 1 # UL ACK
# sudo iptables -I INPUT -p tcp --src $LOCAL_IP --dst $REMOTE_IP -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p tcp --dst $LOCAL_IP --src $REMOTE_IP -j NFQUEUE --queue-num 0 # DL ACK

# Mumble
# REMOTE_PORT=64738
# LOCAL_PORT=45626
# sudo iptables -I INPUT -p tcp --dport $REMOTE_PORT -j NFQUEUE --queue-num 0 # UL DATA
# sudo iptables -I INPUT -p tcp --sport $REMOTE_PORT -j NFQUEUE --queue-num 1 # UL ACK
# sudo iptables -I INPUT -p tcp --sport $LOCAL_PORT -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p tcp --dport $LOCAL_PORT -j NFQUEUE --queue-num 0 # DL ACK

# TCP
# REMOTE_PORT=443
# LOCAL_PORT=45493
# sudo iptables -I INPUT -p tcp --dport $REMOTE_PORT -j NFQUEUE --queue-num 0 # UL DATA
# sudo iptables -I INPUT -p tcp --sport $REMOTE_PORT -j NFQUEUE --queue-num 1 # UL ACK
# sudo iptables -I INPUT -p tcp --sport $LOCAL_PORT -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p tcp --dport $LOCAL_PORT -j NFQUEUE --queue-num 0 # DL ACK

# UDP
# REMOTE_PORT=443
# LOCAL_PORT=45493
# sudo iptables -I INPUT -p udp --dport $REMOTE_PORT -j NFQUEUE --queue-num 0 # UL DATA
# sudo iptables -I INPUT -p udp --sport $REMOTE_PORT -j NFQUEUE --queue-num 1 # UL ACK
# sudo iptables -I INPUT -p udp --sport $LOCAL_PORT -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p udp --dport $LOCAL_PORT -j NFQUEUE --queue-num 0 # DL ACK

# TCP and UDP
# REMOTE_PORT=443
# LOCAL_PORT=45493
# sudo iptables -I INPUT -p tcp --dport $REMOTE_PORT -j NFQUEUE --queue-num 0 # UL DATA
# sudo iptables -I INPUT -p tcp --sport $REMOTE_PORT -j NFQUEUE --queue-num 1 # UL ACK
# sudo iptables -I INPUT -p tcp --sport $LOCAL_PORT -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p tcp --dport $LOCAL_PORT -j NFQUEUE --queue-num 0 # DL ACK
# sudo iptables -I INPUT -p udp --dport $REMOTE_PORT -j NFQUEUE --queue-num 0 # UL DATA
# sudo iptables -I INPUT -p udp --sport $REMOTE_PORT -j NFQUEUE --queue-num 1 # UL ACK
# sudo iptables -I INPUT -p udp --sport $LOCAL_PORT -j NFQUEUE --queue-num 1 # DL DATA
# sudo iptables -I INPUT -p udp --dport $LOCAL_PORT -j NFQUEUE --queue-num 0 # DL ACK



# Show new iptables rules
sudo iptables -L -n -v
