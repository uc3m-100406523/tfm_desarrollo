Our goal was to develop and emulator which fully follows the 3GPP specifications and models for both the Physical and MAC layer simulations, allowing the possible users to add their own algorithms, models or modifications. We haven’t added any proprietary algorithms or models, our contribution is a tool which is easy to use and modify, and gathers the main models and procedures described on 3GPP specifications.  

The general architecture is designed as follows:  

![SimArchitecture.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/SimArchitecture.svg)

While the specifics and details of each  implemented module and functionality is described later, we give a brief overview of the overall data flow and logic. The time granularity of the emulator is the duration of a subframe (1 ms). In each time step (1 ms) the next overall flow is followed:  

1. A.For simulated traffic: 

    - Simulated IP packets are generated in each timestep according to a user-selected traffic generation model. Potential users can add their own traffic models in a simple manner. 

1. B.For real IP Traffic:

    - Real IP Packets coming into a specific port are filtered and queued using Netfilter. Netfilter is a Linux firewall  which provides an API to access and determine the future of the queued packets. This API, written in C allows to filter the packets coming in/out a selected port. In each timestep, the queued packets information (ID and size) are sent to the PDCP/RLC layer which queues simulated IP packets with the same size and ID as the queued ones.  

2. The IP packets are queued in the PDCP/RLC Layer.
3. The PDCP/RLC layer indicates the MAC layer how many bits are waiting to be sent for each connected User Equipent (UE). 
4. The MAC layer uses this information and the channel quality metrics measured by the physical layer to perform the resource allocation step.
5. The MAC layer indicates the PDCP/RLC layer how many bits are allocated for each UE.  
6. The PDCP/RLC layer segments the IP packets into smaller blocks as determined by the MAC Layer.  
7. The allocated blocks are moved to the PHY Layer.  
8. The PHY Layer emulates what happens to each packet in terms of:  

    - Latency 
    - HARQ Retransmissions 

9. According to the emulated latencies and HARQ retransmissions for each packet, the packet:  

    - If it has to be retransmitted it is sent back to the PDCP/RLC queues to be sent again. A simulated HARQ latency is added to the packet and will not be sent until such latency has passed.  
    - If it has been retransmitted more times than the 3GPP specified maximum, the message is discarded. If the message is an actual IP packet, it is discarded by Netfilter after the assigned latency. If it is emulated it is just erased. In both cases, logging data is captured.  
    - If the packet has been successfully transmitted and it’s a real IP packet, it is released by Netfilter for transmission after the specified latency. If it is a simulated packet, it is also erased, and the correspondent data is logged. 
    - If a packet has to be retransmitted, is sent back to the PDCP queues to be sent again. If not, is sent to be released. If the number of retransmissions for the specific packets is greater than the maximum, is discarded.  

10. A logging module is used to log al the relevant data such as:  
    - Throughput 
    - Latencies 
    - Channel Quality Metrics: SINR, RSRP, MCS index, modulation, etc. 
    - Error rate 
    - Resource allocation metrics. 

Note: The steps described below are followed concurrently for both Uplink and Downlink and for each simulated or emulated UE.

The implemented organization overview is reflected in the following figure, and depicted modules will be thoroughly described in the next sections: 

![EmuImplementation.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/EmuImplementation.svg)

* [Configuration File](Configuration-File)
* [Real-Time Emulation](Real-Time-Emulation)
* [MAC Layer](MAC-Layer)
* [User Equipment (UE)](User-Equipment)
* [Data Logging](Data-Logging)
* [Overall Flow](Overall-Flow)