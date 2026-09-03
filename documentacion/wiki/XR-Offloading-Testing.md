The goal of this page is to describe an example setup of a real application transmitting the data over FikoRE, mimicking a realistic scenario in which the application is connected to an actual 5G setup. 

In this case, we have decided to use an eXtended Reality (XR) offloading implementation as the reference application. In this setup we have we have an XR 
Head Mounted Display (HMD) which is offloading a particular task to an edge server placed nearby to a 5G gNB to which the HMD is connected. The offloaded task is a latency-critical one, such as split rendering, with high-throughput requirements above 40 Mbps in, at least, the uplink direction. This scenario demands a strong network, in many cases not accessible to application developers. FikoRE can fulfill this gap allowing XR application developers to rapidly test their solutions on realistic 5G setups. 

## XR Offloading Scenario: Real-time Egocentric Human Segmentation

The scenario we are using as an example is the one described in [this paper](https://arxiv.org/abs/2208.12639). In this scenario, the XR HMD is transmitting a video feed from its frontal stereo camera to the edge running the segmentation algorithm. The segmentation algorithm determines which of the pixels corresponds to the XR user's body, creating a segmentation mask which is transmitted back to the device. This mask is used, along with the captured video feed, to render the user's body inside the VR scene. This offloading solution allows the users to see themselves, in real-time, inside the VR scene. The schematic representation of the proposed scenario is the following: 

![SimArchitecture.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/XROffloadingExample.png)

In the real scenario, the XR HMD is connected to a 5G network in charge of transmitting the high throughput and low latency XR traffic. To mimic the scenario, the 5G link between the HMD and the edge server is replaced by FikoRE. In this scenario, we want all the network variability to come from FikoRE. Therefore, the HMD should be connected via wire to the device running FikoRE. In general, most of XR devices allow to run in tethered mode connected to a workstation. In the scenario we are proposing, the HMD is wired to a workstation running the XR application. This workstation is connected using an ethernet cable to the device running FikoRE. FikoRE can run i) in the same server in charge of running the segmentation algorithm or ii) in a different machine connected to the segmentation server via an ethernet cable. In the first option,  the workstation running FikoRE must run a traffic rerouter to forward the traffic coming from and to the HMD to the segmentation server. Both setups ensure the data exchange between the devices has a minimum overhead and FikoRE can generate all the delays and overhead according to the simulated 5G configuration.

For simplification, we focus on the ii) option, the preferred one when the server workstation specifications can fulfill simultaneously FikoRE's and the segmentation algorithm's requirements. The final setup can be then represented as: 

![SimArchitectureSetup.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/XROffloadingSetup.png)

In this scenario, and according to the IPs and ports shown in the figure above, we need to configure two different Netfilter queues (uplink and downlink), as described in [Compilation and Usage](Compilation-and-Usage): 

```
# [UL] RGB Frames
sudo iptables -I INPUT -p udp --dport %ul_port% -j NFQUEUE --queue-num 0

# [DL] Segmentation Mask
sudo iptables -I INPUT -p udp --sport %dl_port% -j NFQUEUE --queue-num 1
```

Before running the testing setup, make sure that the virtual UE representing the XR traffic is configured in the config file as: 

```
[UE]
ue_id: idReal # Arbitrarily chosen by the user
ue_type: 0
ul_queue_n: 0 # as determined in the --queue-num parameters
dl_queue_n: 1 # as determined in the --queue-num parameters
```

