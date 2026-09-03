We are using [Netfilter Queues](https://www.netfilter.org/projects/libnetfilter_queue/), a user-space library providing an API to packets that have been queued by Linux kernel packet filter. It requires the necessary filtering rule to be set by the user: filter and queue the packets coming in/out a specific port or IP. The filtered packets are added to the configured queue. The emulator already assigns callbacks to each of the queues associated to each of the real-traffic users. The callbacks get the newest packet's info, such as unique ID and size. Virtual packets, identical to the ones created by the simulated traffic generator, are added to the emulator's PDCP/RLC queues. Such packets have the same unique ID as their associated real IP packets. Once a virtual packets has been released or dropped by the emulator, the actual associated IP packet is also released or dropped according to the unique ID.

We implemented a simple class which interfaces with the C API provided by Netfilter Queues to assign callbacks to the configured Netfilter Queues.As we are using Netfilter Queues, a Linux specific library, the emulator must be compiled and run in Linux if the users aims to attach actual IP traffic to it.  This class is instanced for each transmission direction (DL/UL) for each UE attached to actual IP traffic. It configures a callback associated to the specific Netfilter Queue. This callback is added by the PDCP/RLC layer class, which is described later. When ever a pkt is determined to be released or dropped by the emulator, the PDCP/RLC layer can call one of the methods defined by this class to send the appropriate command to Netfilter Queues.

The Netfilter Queue configured ID is given to the specific UE using the configuration file:

```
[UE]
# ...
ue_type: 0
ul_queue_n: 0
dl_queue_n: 1
```
Which define:

- ue_type: if 0, real IP traffic is assigned to the user, and the Netfilter Queues defined below are handled.
- ul_queue_n/dl_queue_n: unique Netfilter Queue ID configured for the UL and DL streams.

We specify how to configure the Netfilter Queues in the Usage section.