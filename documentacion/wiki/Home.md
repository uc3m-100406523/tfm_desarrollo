## Why a 5G+ Emulator? 

Nokia Extended Reality Lab in Spain is focused on Immersive Media Technologies, with a special focus on what we denominated Distributed Reality (DR). The goal of (DR) is to be able to merge different local realities into a single real-time remote immersive experience. One key feature of DR is to allow the users to see his/her own hands and body within a fully immersive VR experience. However, this goal requires high-end hardware to run in real-time. Consequently, we are currently working on offloading architectures and implementations which allow us to run our demanding algorithms (AI/ML) on light VR/AR devices in real-time. 

5G technologies should be theoretically able to fulfill the network requirements of real-time task offloading. However, 5G technologies still have a long path ahead to reach their full potential. Consequently, we decided to implement our own 5G networks and beyond emulator to test and optimize our own solutions, determining which configuration (not only 5G, but also beyond) satisfy the requirements. 
 
##  Goals

There are several emulators publicly available online, such as NS-3, SimuLTE or Simul5G. However, their complexity is extremely high, especially for non-telecommunications-specialists. Our main goal is to provide with a straightforward emulation tool for both experts and non-experts. Contrarily to the mentioned simulators/emulators, the goal of our tool is not mainly to understand and test the network, but study how the network and its different possible configurations behave for particular applications, use-cases and verticals.  

As we want to test our solutions in with actual networked applications we need a network emulator which:  

* Works in Real-Time.
* Handles actual IP traffic efficiently. 
* Handles multiple emulated users with real or simulated traffic. 
* Models the real behavior of the network with sufficient accuracy. 

Besides, we need the emulator to be simple to use and, more importantly, easy to modify for possible particular needs. Consequently, the emulator must:  

* Have a high level of modularity to allow easy modifications.  
* Follow a straightforward implementation.  
* Be simple to use both as an emulator (real traffic) and simulator (simulated traffic).  

Furthermore, as the goal is to test actual applications on different possible scenarios and understand the most optimal network configurations, we understand is crucial to allow to easily modify the resource allocation algorithms and procedures. We believe it’s a crucial step in which an optimal algorithm design can produce an optimal behavior of the network for very specific applications. For this reason, we have designed the algorithm to allow the users to easily implement and test their own resource allocation algorithms.  

Main sections: 
* [Architecture and Implementation Details](Architecture-and-Implementation)
* [Compilation and Usage](Compilation-and-Usage)