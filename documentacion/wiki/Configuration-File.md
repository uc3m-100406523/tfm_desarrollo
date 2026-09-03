All the configurable parameters can be manually selected by the user. The current implementation doesn't allow to reconfigure the emulator dynamically and has to be done before the simulator is run. The configuration file, with *.ini extension, has the following format:
```
# Comments
[VariableSuperclass1]
Variable1: value
```
The comments are preceeded by a #. In "[ ]" we define the superclass to which the following variables are part of. The variables are defined followed by a ":" with NO spaces. The value is written right after, with a space in between the ":" and the value. 