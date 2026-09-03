The User Equipment (UE) module models the individual UEs connected to emulated gNB/antenna. In each timestep, the UE is designed to:

1. Generate Traffic: using a traffic generator model or from the incoming actual IP traffic.
2. Update Position: using a custom mobility model, the UE updates its own position every timestep.
3. Estimate the Channel State Indicators: using the PHY Layer models from the 3GPP specifications.
4. Release/Drops Packets: which have been successfully transmitted or were dropped according to the emulator models. 

The simplified UE structure is the following: 

![UEOverall.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/UEOverall.svg)

The UE module is implemented in the ue() class, which is in charge of modeling and updating the simulated UE's position, generating/handling packets, estimating the Channel State Indicator and Releasing or Dropping the already processed packets. The method step() is in charge of performing these steps: 

![UEDataflow.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/UEDataflow.svg)

We can observe that the emulator's instances of mobility_model(), traffic_model(), netfilter_queues()/pkt_capture(), phy_handler() and pdcp_handler() are all part of the UE module. We have created a helper class, ue_handler, which gets the UE-related configuration parameters and create all the emulated UEs. 

The configuration file is designed to allow the user simulate multiple users grouped according to their specifications. A new group of UEs is initialized as:

```[UE]
ue_id: idReal
# . . .
```
The configuration file parser creates a new set of UEs every time it parses the "[UE]" identification. While the ue_id is not important for the correct functioning of the emulator, is better to use a unique id for debugging/logging purposes. The other configuration parameters are:
```
[UE]
ue_id: idReal
ue_type: 0
ul_queue_n: 0
dl_queue_n: 1
n_ues: 1
n_antennas: 2
tx_power: 20
cqi_period: 5
ri_period: 5
scaling_factor: 1
log_freq: 10
log_ue: false
log_quality: false
log_traffic: false
log_mobility: false
traffic_type: 0
ul_target: 5.0
dl_target: 10.0
var_perc: 0.10
pkt_size: 12000
mobility_type: 1
pos_x: 50
pos_y: 50
random_init: false
speed: 0.0
speed_var: 0.0
max_distance: 1000
time_target: 5
time_target_var: 0
priority: 1
delta_metric: 1.0
delay_t_metric: 0.1
beta_metric: 0.5
ue_height: 1.5
```
Which define:

- ue_type: if 0, real IP traffic is assigned to the user, and the Netfilter Queues defined below are handled.
- ul_queue_n/dl_queue_n: unique Netfilter Queue ID configured for the UL and DL streams.
- n_ues: number of UEs of these tyPHY-Layerpe.
- n_antennas: number of physical antennas in the UE.
- tx_power: transmission power for the UE.
- cqi_period: period in ms for the PHY layer to re-estimate the CSI.
- ri_period: period in ms for the PHY layer to estimate the Rank Indicator.
- scaling_factor: used for carrier aggregation throughput calculation. Is signaled by the eNB/gNB in a real deployment. It can take the values: 1, 0.8, 0.75, 0.4
- log_freq: data is logged according to this period in ms.
- log_ue: enable/disable UE logging
- log_quality: enable/disable PHY logging
- log_traffic: enable/disable traffic generation logging
- log_mobility: enable/disable mobility model logging
- traffic_type: selected traffic generator models for this type of UEs.
- ul_target/_dl_target: target throughput for UL and DL respectively.
- var_perc: size of the variance of the generated noise.
- pkt_size: virtual IP packet size in bits.
- mobility_type: id of the desired mobility model for current UE.
- pos_x: initial x position.
- pos_y: initial y position.
- random_init: wether to randomly initialized or not.
- speed: target speed of the UEs.
- speed_var: size of the white noise to be applied in each timestep to the target speed.
- max_distance: max. distance of the UE to the gNB. 
- time_target: target time used in some of the implemented models, such as random walk model.
- time_target_var: size of the white noise to be applied in each timestep to the target time.
- priority: used by the user priotitization algorithm implemented in the MAC Layer.
- delta_metric: metric-specific parameter.
- delay_t_metric: metric-specific parameter.
- beta_metric: metric-specific parameters.
- ue_height: height of the UE.

Main Modules:
* [Traffic Generator](Traffic-Generator)
* [Netfilter Module ](Netfilter-Module)
* [Mobility Models](Mobility-Models)
* [Metric Estimation](Metric-Estimation)
* [RLC/PDCP Layer](RLC-and-PDCP-Layer)
* [PHY Layer](PHY-Layer)