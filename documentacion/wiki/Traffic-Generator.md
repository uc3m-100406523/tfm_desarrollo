The traffic generator is in charge of periodically creating simulated IP packets for both uplink and downlink transmission directions. It’s up to the emulator’s users to decide and implement their own traffic generators. We built a base class for the traffic generator instance from which other custom traffic model can override the base methods. There is a higher level class which can select the model from all the implemented traffic generator class inheriting from the base class. There is one traffic generator instance per user and it can be different for each of them. The traffic generation models can be different for each transmission direction, UL/DL. This functionality, however, has not been implemented as a selectable option in the configuration file and is left as a future step. Within the current version emulator there is two different traffic generators: 

## Simple Continuous Traffic Generator

Simple traffic generator model in which the only parameters to be determined are:  

- Target UL Throughput.
- Target DL Throughput.
- IP packets size.

With this information, the traffic generator creates, in each time step, as many packets (each of the specified size) as necessary according to the selected target throughput. We included random variability around the target throughput following a normal distribution. In each time step of 1 ms, we add this variability around the necessary bits that must be generated to achieve that target throughput. In every time step, we generate as many UL or DL bits as required to fulfill the target data rate configured by the user. We add some white noise around the target throughput in each time step.

## Traffic Generation from File

In this implementation, the generator reads the packets to be generated from a simple .txt file. Each line in the file contains a timestamp and the payload size. The lines are ordered according to the timestamps. The emulator reads line by line in accurate synchronization with the internal clock and according to the timestamps. Once a line is read (in sync with the timestamps) the corresponding payload is added to the IP buffers. A file is necessary for each transmission direction. 

## Configuration Parameters

8 configuration parameters can be defined by the user, for each group of UE types:
```
[UE]
# ...
traffic_type: 1
ul_traffic_file: /home/diego/Git/VRMeasurements/results/VRTest/FinalFigures/Validation/simplevideo.txt
dl_traffic_file: /home/diego/Git/VRMeasurements/results/VRTest/FinalFigures/Validation/simplevideo.txt
delay: 0.002
ul_target: 5.0
dl_target: 5.0
var_perc: 0.0
pkt_size: 12000
```
Which define:

- traffic_type: selected traffic generator models for this type of UEs. [0 for the simple model, 1 for the file-based generator]
- ul_traffic_file: file from which read the packets if traffic_type is 1. For UL transmission direction. 
- dl_traffic_file: file from which read the packets if traffic_type is 1. For DL transmission direction. 
- ul_target/_dl_target: target throughput for UL and DL respectively.
- var_perc: size of the variance of the generated noise.
- pkt_size: virtual IP packet size in bits.
