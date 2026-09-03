The MAC layer module is the key component of our implementation, as it allows to test different scheduling schemes or approaches suitable for the specific applications or use cases tested. The MAC layer represents a more detailed implementation of the resource allocation procedures. Such procedures were obtained from 3GPP 38.214 and 3GPP 38.211 specifications. According to such specification, a resource allocation grid is created using the info selected by the user in the config file, such as: 
- Bandwidth.
- FDD/TDD Multiplexing Modes/Configuration.
- Resource Allocation type (0 or 1 as in the specifications).  
- Resource Allocation configuration (0,1 or 2 as in the specifications).  

The resource allocation grid is divided in:

* **Frequency**: The enB/gNB has a fixed bandwidth assigned for transmission/reception. The total bandwidth is divided into subcarriers of fixed size. ​Terminology:
    - **Frame**: Is the largest division unit. It extends along the entire bandwidth.​
    - **Resource Block**: is defined as 12 consecutive subcarriers in the frequency domain.​ Size in frequency depends on numerology or subcarrier spacing.​
    - **Subcarrier**: the smallest frequency division​. The frequency length depends on the numerology.
* **Time**: To bound the resource allocation steps in time, the scheduling time is limited and also subdivided in smaller units. ​Terminology:
    - **Frame**: Is the largest division unit. ​ It has a time duration of 10 ms.
    - **Subframe**: next level of granularity. Duration of 1 ms​
    - **Slot**: it contains the OFDM symbols.​ The time length of the slot depends on the​ numerology​. The number of OFDM symbols is 6-7 in LTE and 12-14 in NR/5G​

![Numerology.png](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/Numerology.png)

The result is a time-frequency resource grid with small units which are arbitrarily assigned to different UE by the scheduler.  These small time-frequency units are the Resource Elements (REs) symbols. ​The Resource Elements (REs) are organized in Pysical Resource Blocks (PRBs) of 14 symbols in the time domain and 12 subcarriers in the frequency domain. The PRBs can by grouped in Resource Block Groups (RBGs) according to the resource allocation configuration (0, 1 or 2).  

![Grid.png](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/Grid.png)

The PRBs/RBGs are assigned to the most optimal UEs according to a selected metric. In each time step, a metric value is calculated for each UE and each PRB/RBG. Such metric type is arbitrarily selected by the emulator user and can be easily custom-implemented. We have only included publicly available metrics in the current version of the simulator, such as: 

- **Round Robin**
- **Max. throughput**
- **Proportional Fai**r 

We have implemented the resource allocation model in a very modular manner so the potential users can implement their own specific resource allocation techniques or configuration such as network slicing. Once the metrics for all the UEs and PRBs/RBGs are obtained, each PRB/RBG is assigned to the UE with the highest obtained metric for such PRB/RBG.  The resource allocation steps is not very constraint in the standards: the implementation details are up to the vendors/operators. The resource allocation can be distributed along the time axis in two manners: ​

- **Localized**: allocates all the contiguous slots along the time axis to the same UE, within a subframe. ​
- **Distributed**:​ free allocation allong the time axis. Gives more allocation freedom, but greater overhead​

Along the frequency axis, it can be organized in RBGs of size: 

![TypeAllocation.png](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/TypeAllocation.png)

Once the Resource Allocation Grid is built for each transmission direction, it presents the following distribution: 

![MACSimplified.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/MACSimplified.svg)

The MAC layer module is also in charge of determining which modulation to be used for each UE and PRB/RBG according to the simulated Channel Quality Measurements in the PHY Layer. Adaptive Modulation and Coding (AMC) technology dynamically adjusts the OFDM modulation order, coding method and coding rate of symbols to maximize throughput of the entire link transmission system.​ In order to conduct AMC operation, Channel Quality Indicators (CQIs) need to be fed back by User Equipments (UEs) or eNB/gNB:

![AMC.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/AMC.svg)

​This SNR-CQI calculation can be done in two different modes, selected by the emulator's user using the config file: ​

* **Wideband**: the SNR, and therefore, the CQI is estimated for the entire bandwidth. One single CQI value is given by each UE. It is less precise and allows less flexible scheduling but reduces the scheduling and signaling overhead. ​
* **Sub-band**: the bandwidth is divided in subbands. Different SNR/CQI values are estimated by the UE for each sub-band.  It allows to achieve more optimal scheduling solutions using a higher signaling overhead. ​

The selected modulation determines how many bits can be sent in each PRB/RBG for each UE, which is also used to estimate some of the metrics. Each modulation scheme provide a different bit order, which can be defined as the capacity in bits of each OFDM symbol:​

- QPSK: 2 bits​
- 16QAM: 4 bits​
- 64QAM: 6 bits​
- 256QAM: 8 bits​

Once the assignation is done, a Transport Block Size (in bits) is obtained for each assigned pair of UE-PRB/RBG, which is the length of the block that has tobe provided by the RLC/PDCP layer. The TBS for each PRB/RBG is estimated according to 3GPP 38.306-v16.6.0, section 4.1.2 equation with the following shape (parameters explained in the mentioned specifications): 

![Bitrate.png](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/Bitrate.PNG)

Finally, the implemented MAC layer considers both FDD and TDD full-duplex communication.

* **FDD**: The total bandwidth is divided in two, uplink and downlink. Consequently, the total available bandwidth for each transmission direction resource allocation grid is divided by two.
* **TDD**: In this case, both grid are built with the total available bandwidth, but the time slots are alternatively assigned to one transmission direction at a time. 

In the emulator, both FDD and TDD perform identical resource allocation steps. Only the amount of DL/UL allocated bits in each time step change. As the smallest simulation granularity is 1 ms or 1 subframe, the TDD Handler only needs to: ​

- Estimate how many OFDM symbols are assigned to transmission direction, UL and DL, in the current subframe (1ms). ​
- Inform the scheduler of the number of OFDM symbols assigned for each direction.  ​
- The scheduler performs the scheduling normally, but the bits assigned for UL/DL for each user depend on the number of OFDM symbol assigned to each TX direction. ​

The MAC Layer basic class is the rb() (Resource Block) class, which we instance as many times as RBs/RBGs in the Resource Allocation grid, according to the selected configuration parameters. We build two grids of rb() instances, one for each transmission direction UL/DL. The grids are handled by instances of the grid() class. The interface between both grids and other modules is provided by the mac_layer() class. The steps of the UL and DL grids are designed to run concurrently if multi-threading is enabled by the user.

The grid() class is in charge of building the Resource Allocation grid for the assigned transmission direction according to the selected configuration parameters. This is done following the respective 3GPP specifications, described in the following steps:

1. If FDD duplexing is used, the total available bandwidth for the current transmission direction (UL/DL) is divided by 2. 
2. From the selected numerology, we get the subcarriers spacing, in HZ. 
3. The total number of RBs in frequency is estimated using the subcarrier spacing, total available bandwidth and the number of subcarriers per RB (12 according to the specifications:

    *Number of frequency RBs = Bandwidth/(Subcarrier Spacing * Number of Subcarriers per RB)*

4. Two possible scheduling modes:

    4. A.Distributed Mode: in the time axis, the slots are separated in individual RBs: The slots are not grouped, and therefore, in each slot, and according to the specifications we have 14 OFDM symbols in each RB.
    4. B.Grouped Mode: in the time axis, the slots are all grouped in a single Resource Block Group. In this case, with a RBG including all the time slots within a subframe. The total number of OFDM symbols is then 14* (Number of slots).

5. The number of time slots within the subframe of 1 ms depends on the numerology:

    *Number of time slots = 2<sup>numerology</sup>*

6. Two possible scheduling configurations:

    6. A.Configuration 0: the RBs are grouped in RBG in frequency. The number of frequency RBs per RBG is given in the specifications. The number of total subcarriers in a RBG is then:

        *Number of SC per RBG = Number of RB per RBG * 12*

    6. B.Configuration 1: the RBs are not grouped, they are handled individually. 

7. The Resource Element (RE) is the smalles time-frequency unit, composed by a OFDM symbol in time and a subcarrier in frequency. Using the above possible configurations, we estimate the number of REs in each RB/RBG. This number of RE is used, by the rb() class, too estimate how many bits can fit in that RB given the simulated Channel State Indicator. 

In each of the UL and DL grids, the main operations happen in the step() method in which the UEs are allocated to different RGB according to their estimated CSIs and the selected scheduling algorithm, summarized as: 


![GridStep.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/GridStep.svg)

In every allocation step, each RBG evaluates each UE which has estimated the metric according to its measured CSIs. Once an individual RGB has finished iterating over the UEs, it gets the UE with highest metric. The number of bits that can be allocated to that UE is also estimated using the CSIs. The last step is then to notify the UE that the rbg with indexes i,j has been assigned to it, with the estimated number of bits granted. This process is repeated for both the UL and DL transmission directions.

The number of bits than are assigned depend onthe estimated CSI. If TDD duplexing is used, the bits that the assigned UE can transmit for DL/UL depends on the available DL/UL time slots for the current subframe (1ms). This number of available UL/DL time slots is determined by the class tdd_handler(). There is an instance of this class for each transmission direction grid. The tdd_handler simply returns the total number of Resource Elements granted for UL/DL transmission for the current subframe given the current timestamp. The TDD pattern is given as a number of consecutive DL slots, a transition slot and a number of consecutive UL slots. This pattern is continuosly repeated: 

![TDDPattern.png](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/TDDPattern.png)

The configuration parameters used by the MAC layer are:
```
[MACLayer]
metric_type: 6
log_freq: 10
log_mac: false
mimo_layers: 4
ofdm_symbols: 14
numerology: 3
max_rtx_ul: 4
max_rtx_dl: 4
mcs_tables: true
scheduling_mode: 0
scheduling_type: 0
scheduling_config: 1
duplexing_type 0
n_dl_slots: 4
n_ul_slots: 1
transition_c: 54
```
Which define:

- metric_type: selected metric type.
- log_freq: period between logs in ms
- log_mac: enable/disable MAC layer's logging
- mimo_layers: number of available MIMO layers
- numerology: chosen numerology or subcarrier spacing.
- scheduling_mode: scheduling mode - 0 - distributed | 1 - grouped.
- scheduling_type: scheduling type - 0 - group frequency RBs in RBGs | 1 - no frequency RBs grouping.
- scheduling_config: configuration for scheduling type 0.
- duplexing_type: TDD or FDD duplexing.
- n_dl_slots: number of DL slots within a TDD configuration pattern.
- n_ul_slots: number of UL slots within a TDD configuration pattern.
- transition_c: Transition configuration which determines the number of DL/UL Resource Elements available within the transtion (DL <-> UL) slot.