The PDCP/RLC layer represents a very simple abstraction of all the high layer levels within the full stack of 5G networks and beyond. It is in charge of queuing all the IP packets (real and simulated) from all the UEs. One queue is created for each UE. The PDCP/RLC layer communicates the MAC layer, in a Scheduling Request (SR), how many bits are ready for transmission for each UE.  When ever a slot is allocated to an UE by the MAC layer, the IP packets of such UE are split into smaller blocks (if necessary) and moved to the MAC layer queues.  We added the RLC packet re-ordering and re-transmission capabilities. The simplified flow follows:

![PDCPRLC.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/PDCPRLC.svg)

RLC Packet Ordering Capabilities: IP packets are generally larger than the Transport Block Size (TBS) or packet size used for transmission. As the transmitted packets can be retrnasmitted in an HARQ process, they might arrived unordered. The RLC is in charge of reordering and reconstructing the received packets into their corresponding IP packets. If one packet from the IP packet is lost, the entire IP packet is dropped. We emulate this behaviour by checking the correct integrity of the IP packet. The IP packet is not released until all the packets have been received. Besides, RLC also tries to ensure IP packet order (up to an arbitrary timeout). We achieve this attending to the current packet ID and the previous packet ID which is also stored in its header.

Note: No specific 3GPP models/implementations were followed: this module just represents a high level abstraction of the described layers. None of the protocols and interfaces described in the different 3GPP specifications describing these layers are implemented. We just understood this layer as a packet queuer, divider and provider.  

This module is a complex, built using multiple pieces or classes. We built the following block diagram to give a high level overview of the PDCP/RLC layer:

![PDCPRLCImplementation.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/PDCPRLCImplementation.svg)

We can observe how the high level PDCPHandler() class is the one interfacing the different PDCP/RLC processes with other emulator's modules. Within this class there are two instances of the PDCPLayer() class, one for each TX direction. This last class is the one orchestrating the pkt flow between the different queues, according to the instructions coming from other modules. While most of the implemented methods are just interfaces between other modules and the main methods from the different buffers, there is key method which is actually handling the flow between the IP, Release and HARQ buffers. This method, called handle_pkt(), takes the size to be transmitted in bits, along with some arbitrary Channel State Indicators. The logic can be depicted as:

![HandlePkts.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/HandlePkts.svg)

The pdcp_layer() class handles 3 main buffers:

- IPBuffer: Stores the simulated (virtual or from actual IP traffic) IP packets.
- HARQBuffer: Stores the packets that must be retransmitted according to the HARQ model.
- ReleaseBuffer: Releases the simulated IP packets (remove from memory, or release actual IP packets using Netfilter Queues interface)

The HARQ and Release Buffers have ready packets when the buffer's front packet target delay has been met. By doing this we make sure all the modeled delay, both on the  HARQ side and release side (backhauling delay) are considered. The buffers are handled by the ip_buffer(), harq_handler() and release_handler() classes. The harq_handler() also includes the retransmissions estimation model described in section C.6.

**Actual IP Traffic Handling** 

The main difference between the real/virtual traffic handling is that in the virtual case, we dont move the packets around to reduce the processing overhead. We only store statistics of consumed and drop packets and latencies, but we ignore the packet indexes or RLC re-ordering. Consequently, the PDCP Layer behaves slightly different when actual IP traffic is assigned to a virtual UE. The main differences are in the classes pdcp_layer() and release_handler() classes. We created to inheriting class from each of them, pdcp_layer_ip() and release_handler_ip() respectively. In pdcp_layer_ip() the main callback receiving the IP packets queued by Netfilter is set. This callback, creates and queue the virtual IP packets using the meta-info received by the callback.

There is a PDCP Handler instance for each UE handling its own UL/DL packet flow. However, the configuration parameters are identical for all the UEs:
```
[PDCP_RLC]
backhaul_d: 0.003
backhaul_d_var: 0.0
order_pkts: true

[MACLayer]
# ...
max_rtx_ul: 4
max_rtx_dl: 4

[PHYLayer]
# ...
air_delay_var_ul: 0.0
rtx_period_ul: 0.004
rtx_period_var_ul: 0
rtx_proc_delay_ul: 0.002
rtx_proc_delay_var_ul: 0.0
air_delay_var_dl: 0.0
rtx_period_dl: 0.005
rtx_period_var_dl: 0
rtx_proc_delay_dl: 0.002
rtx_proc_delay_var_dl: 0.0
```
Which define:

- max_rtx_ul/dl: max number of retransmissions for UL/DL HARQ packets.
- air_delay_var: added variance to the delay comming from the air propagation.
- rtx_period_ul/dl: ack/nack delay in seconds for UL/DL HARQ packets.
- rtx_period_ul/dl_var: white noise spread around the ack/nack delay in seconds for UL/DL HARQ packets.
- rtx_proc_delay_ul/dl: ack/nack processing delay in seconds for UL/DL HARQ packets.
- rtx_proc_delay_ul/dl_var: white noise spread around the ack/nack processing delay in seconds for UL/DL HARQ packets.
- backhaul_d: backhauling delay, use for Release buffer.
- backhaul_d_var: white noise spread around the backhauling delay.
- order_pkts: enable/disable RLC reordering. 