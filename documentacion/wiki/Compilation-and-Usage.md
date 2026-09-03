The emulator has been designed to be easily compiled and used. We have created a simple Makefile to simplify the compilation process. The code has been developed in C++11 and prepared to be compiled using g++. We also ensured that the dependencies list is short. The emulators has been designed to work only with Ubuntu. It could be compiled for Windows if NO ACTUAL IP TRAFFIC is USED. As it is not our goal, we let potential users to modify the compilation instructions to achieve their goals (Netfilter MUST be removed from the compilation pipeline). Ubuntu instructions:

1. Install the dependencies:

- Install Netfiler Queues:
```
sudo apt update
​​​​​​​sudo apt install libnetfilter-queue-dev
```
- Install Minimalistic Netlink communication library:
```
sudo apt update
sudo apt install libmnl-dev
```
2. Download/Clone the source code from this repository.
3. Open a terminal and navigate to the folder to which the source code was cloned. Make sure make is insntalled. Otherwise install it (sudo apt install make) as explained here. In the main folder, where the MakeFile is, run:
```
make
```
4. If no error was raised, the emulator was compiled on the ./bin folder. It can be run from the source code folder as:
```
./bin/main
```
5. The configuration file must be stored in source code folder, with the name "config.ini". A tamplate full-funtional configuration is provided and ready to be used.

## Real IP Traffic

To run the emulator with actual IP traffic we need to follow the next steps:

1. Prepare Netfilter Queues using iptables. For instance, for TCP Uplink and Downlink traffic, we would run the following commands on a Linux terminal or bash script:
```
# [UL] Main Data
sudo iptables -I INPUT -p tcp --dport %destination_port% -j NFQUEUE --queue-num 0

# [DL] ACK back
sudo iptables -I INPUT -p tcp --sport %destination_port% -j NFQUEUE --queue-num 1

# [DL] Main Data
sudo iptables -I INPUT -p tcp --sport %incoming_port% -j NFQUEUE --queue-num 0

# [UL] ACK back
sudo iptables -I INPUT -p tcp --sport %incoming_port% -j NFQUEUE --queue-num 1
```
With %destination_port% and %incoming_port% being substituted by the user-selected destination and incoming ports.

2. Prepare a single UE which will process this actual IP traffic by preparing the configuration file as:
```
[UE]
ue_id: idReal # Arbitrarily chosen by the user
ue_type: 0
ul_queue_n: 0 # as determined in the --queue-num parameters
dl_queue_n: 1 # as determined in the --queue-num parameters
```
Example setup for an XR offloading scenario testing using the emulator: 

* [XR Offloading Testing: Example Setup](XR-Offloading-Testing)

## Tests

While this section doesn't describe proper testing, as they were not developed (at least yet), it provides some hints of the expected behaviour. If the MakeFile was not changed, the -O3 optimization flag was used and the following parameters were set:

- Base Frequency: 27.5 GHz
- Bandwidth: 800MHz
- TDD: 1UL:4DL
- Modulation: 256QAM
- Target UL per user: 5 Mbps
- Target DL per user: 10 Mbps
- Metric Type: Proportional Fair
- Scheduling Mode: 0 (Individual Slots)
- Scheduling Type: 0 (Grouped in RBGs)
- Prioritization: Disabled

And the emulator running on a Intel i7-10870H CPU @ 2.20GHz with 8 physical (16 virtual) cores, we got the following performance:

| Number of UEs | ​Mean DL Throughput | ​Mean UL Throughput | ​Mean DL Latency | ​Mean UL Latency | Step Processing Time|
| ------ | ------ | ------ | ------ | ------ | ------ |
| 1 | 10 Mbps | 5 Mbps | 3.5 ms | 3.5 ms | <0.01 ms |
| 10 | 10 Mbps | 5 Mbps | 3.5 ms | 3.5 ms | <0.3 ms |
| 50 | 10 Mbps | 5 Mbps | >7 ms | >7 ms | <0.5 ms |
| 100 | 10 Mbps | 5 Mbps | >10 ms | >10 ms | <0.8 ms |
| 200 | 10 Mbps | 5 Mbps | >15 ms | >15 ms | >1 ms |