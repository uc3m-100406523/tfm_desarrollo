The PHY layer models the Channel Quality Measurements: SINR, RSRP, MCS, CQI, HARQ ACK/NACK. These metrics, besides of being logged for later analysis, are used by the MAC layer for resource allocation decisions, and to determine what happens with each data block. This info is used to also determine the probability of a packet to be retransmitted, according to the HARQ model. The SINR is obtained by simulating the Received Signal Power (RSP) and noise and interference:
```
SINR = RSP/(Noise + Interference)
```
The signal power is modeled according to 3GPP 38.901 specification:  
```
RSP(dB) = transmissionPower(dBm) – pathLoss(dB) + shadowing(dB) + fading(dB) + txGain(dB) + rxGain(dB)
```
The path loss, attenuation and fading models can be found in the 3GPP specification above for 6 different outdoor/indoor scenarios. These are the only models implemented in the current version of the emulator. txGain, rxGain and transmissionPower are left as configuration parameters manually selected by the user using the configuration file.

The noise and interference are modelled using the same models as above but for other eNBs/gNBs and UEs sufficiently close to the simulated eNBs/gNBs and UEs:

- Noise (N) estimation: The noise is a constant value: Thermal_noise + Noise_figure, which are chosen as simulation parameters by the user.
- Interference (I) estimation: is modelled using the Received Signal Power models as in the previous slide but for other Base Stations (BS) and UEs sufficiently close to the simulated BS and UEs.

The noise and interference are left as fixed in the current version of the emulator and are calculated before the emulation begins. The number and distance of the interfering eNBs/ gNBs and UEs, and their base frequencies and other basic configuration are left as simulation parameters.  

The SINR is used to estimate the optimal MCS index for each UE and PRB/RBG. To get the SINR-MCS relations, we performed a set of link level simulations using Matlab, obtaining a set of  SINR-BLER curves for each MCS. These are obtained for different configurations according to the maximum number of MIMO layers and RBGs sizes.

The HARQ model determines whether a packet has to be re-transmitted or not following a simple stochastic approach:

![HARQ.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/HARQ.svg)

Where n is the current number of retrnasmissions for the evaluated packet and R is the HARQ reduction parameter given as a configuration parameters. From the specifications we assumed:

- Maximum 4 retransmission before droping the packet.
- No fixed ACK/NACK delay, asynchronous.
- Modulation kept from original transmission regardless the update CQIs.
- HARQ packets with higher priority than first transmission packets.

Finally, we have the Rank Indicator Model which determines if the signals received in each antenna of the UE are uncorrelated, and MIMO can be used. Available models in the State of the Art are based on correlation matrices which we do not and will not estimate. Current implemented model is based in the idea that the transmitted power is constant for the same UE and is divided by each non-correlated antenna. Consequently, we can estimate the limit SINR values for each added layer from which is more efficient to use the extra layer. We built a simple look-up table with this information.

All the channel quality estimations are done depending on the correlation time (estimated from the doppler effect from the frequency band and the UE's velocity). Besides, the shadowing estimation and pathloss also depends on the correlation distance (traveled by the UE), parameter given by the 6 models described in the specifications. We have then the following simple chart flow:

![PHYFlow.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/PHYFlow.svg)

The steps shown in the figure implement the models described in 3GPP 38.901 specifications. Some details:

![ModelsPHY.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/ModelsPHY.svg)

All the functionality is implemented within the phy_layer() class. This class is instanced once for each transmission direction (DL/UL). We implemented a helper class, phy_handler, which includes these instances and interfaces them with other modules of the emulator.