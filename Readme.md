This Python script implements a simple PID controller for the emission current of TITAN EBIT. Use the controller at your own risk and only after careful testing (at minimal beam currents!) that the tuning parameters are well adjusted and the controller behaves as expected. 

Steps for setting up the PID controller on a TRIUMF DAQ machine (assumes PyEpics is pre-installed): 
0. Navigate into the directory holding this Readme and current_stabilization.py.

1. Open the configuration file (stabilizer_config.json) in a text editor and ensure that the specified parameters are reasonable starting points for the PID controller. 

2. Start up the PID controller by running: 
python -m current_stabilization

3. Optimize PID parameters: You can update the PID parameters in stabilizer_config on the fly while the controller is running and monitor for changes (near-)instantaneously. Note that these configuration changes will not be logged as a config file is only being written at the beginning of a stabilization run. 

4. Stop the current stabilization using CTRL + C.  
