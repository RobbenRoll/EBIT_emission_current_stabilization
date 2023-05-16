This Python script implements a simple PID controller for the emission current of TITAN EBIT. Use the controller at your own risk and only after careful testing (at minimal beam currents!) that the tuning parameters are well adjusted and the controller behaves as expected. 

Steps for setting up the PID controller on a TRIUMF DAQ machine (assumes PyEpics is pre-installed): 
0. Navigate into the directory holding this Readme and EBIT_current_PID_controller.py.

1. Download ivPID Python module:
wget https://raw.githubusercontent.com/ivmech/ivPID/master/PID.py

2a. If the directory does not already hold a pid.conf configuration file: Open EBIT_current_PID_controller.py in a text editor and set the I_target, Kp, Ki, Kd parameters to reasonable starting values. Upon starting PID controller script, a pid.conf file will be automatically created with these parameters.   

2b. If the directory already holds a pid.conf configuration file: Open the configuration file in a text editor and ensure that the specified parameters are reasonable starting points for the PID controller. 

3. Start up the PID controller by running: 
python EBIT_current_PID_controller.py

4. Optimize PID parameters: You can update the PID parameters in pid.conf on the fly while the controller is running and monitor for changes (near-)instantaneously. 
