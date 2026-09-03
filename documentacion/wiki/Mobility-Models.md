We implemented 3 simple well-known mobility models for the UE

1. Manhattan Model: the name comes from the squared shapes of the followed path, similar to Manhattan streets. The model randomly selects a new direction from the main four cardinal directions every time the elapsed time is greater than an arbitrary target time.
2. Random Walk Model: randomly selects a new completely random direction every time the elapsed time is greater than an arbitrary target time.
3. Random Waypoint Model: randomly selects a new target position every time the previous target position has been reached.

The three mobility models outputs from the emulator's implementation:

![MobilityModels.png](https://github.com/nokia/5g-network-emulator/blob/main/docs/figures/MobilityModels.png)

The Mobility Models are organized identically to the Traffic Generators models: we created a base class that the custom implemented Mobility Model classes override. Every time update_pos() method from the base or inheriting classes is called, a new position for the UE is estimated. There is one instance for each UE, and each UE can be assigned with a different Mobility Model. The base class simply does not update the position: is a static user model. The initial position can be randomized or manually selected by the user using the configuration file.

For each UE, in the configuration file the user can determine the following parameters' values:
```
[UE]
# ...
mobility_type: 1
pos_x: 50
pos_y: 50
random_init: false
speed: 0.0
speed_var: 0.0
max_distance: 1000
time_target: 5
time_target_var: 0
```
Which define:

- mobility_type: id of the desired mobility model for current UE.
- pos_x: initial x position.
- pos_y: initial y position.
- random_init: whether to randomly initialized or not.
- speed: target speed of the UEs.
- speed_var: size of the white noise to be applied in each timestep to the target speed.
- max_distance: max. distance of the UE to the gNB. 
- time_target: target time used in some of the implemented models, such as random walk model.
- time_target_var: size of the white noise to be applied in each timestep to the target time
