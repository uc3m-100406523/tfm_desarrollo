The emulator's usability would be extremely reducing without proper data logging which allows users to analyze the performance for a given network configuration. As the emulator is designed to run in real-time, the logging overhead should be reduced to the minimum. We used [spdlog](https://github.com/gabime/spdlog), a fast C++ implementation for data logging to text files. The logging format is up to the developers. We used our own custom format which we plan to change to CSV or similar in future versions.

We implemented a log handling class, log_handler(), which instantiates a spdlog logger agent. In total, we instantiate log_handler() class twice, for UE and MAC logging. To avoid increasing the overhead, we recommend to use high (>100ms) logging periods. We implemented a simple class which estimates the mean of the desired data between the logging periods. Consequently, we are logging the mean values between the logging periods rather than the quantized values.

The associated configuration parameters are:
```
[UE]
#. . .
log_freq: 10
log_ue: false
log_quality: false
log_traffic: false
log_mobility: false

[MACLayer]
#. . .
log_freq: 10
log_mac: false
```
Which define:

 - log_freq: data is logged according to this period in ms.
 - log_ue: enable/disable UE logging
 - log_quality: enable/disable PHY logging
 - log_traffic: enable/disable traffic generation logging
 - log_mobility: enable/disable mobility model logging
 - log_freq: period between logs in ms
 - log_mac: enable/disable MAC layer's logging