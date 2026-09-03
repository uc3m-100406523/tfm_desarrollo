The current simulator has been designed to run in emulation mode principally. This requires real-time processing which satisfies the chosen time granularity of 1 ms: all the processes happening in a single timestep should meet this 1 ms deadline. Consequently, the emulator has been implemented in C++ specifically designed to effienctly allow concurrent processing. Specifically, each UE() instance runs in a separate thread. Besides, the downlink and uplink Grid() instances also run concurrently. The MACLayer processes run first, with UEs processed inmediatly after. This is done as some results from the MACLayer() step are required by the UEs processes. For debugging purposes, the user can choose to run the emulator in a single thread, however, this is evidently discouraged when the emulator must run in real-time (or faster).

As the emulator is designed to handle real traffic, the emulator should be able to precisely run a timestep every millisecond to ensure consistency between the IP packets and emulator's timing. We implemented a simple ticker module in charge of syncrhonizing the emulator, triggering a signal every millisecond. The process is running in a separate thread: 

![Ticker.svg](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/Ticker.svg)

Two configuration parameters can be defined by the user:
```
[Global]
duration: -1
period: 1
```

Which define:

* period: of the signal triggering, in ms. If set to <0, simulation mode, the emulator runs as fast as possible.
* duration: duration of the simulation in s.