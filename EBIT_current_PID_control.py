#!/usr/bin/python
# Software PID controller for EBIT beam current stabilitzation
# Regulates the focus bias in order to stabilize the cathode emission current
# Adopted fom https://onion.io/2bt-pid-control-python/
##import epics
from ivPID import PID
import time
from datetime import datetime
import numpy as np
import os.path

I_target_mA = 50 # nominal electron emission current [mA]
I_mon_res_mA = 0.24 # current monitor resolution [mA]
V_focus_min = 400 # minimal allowable focus voltage [V]
V_focus_max = 600 # maximal allowable focus voltage [V]
max_dV_focus = 1. # maximal allowable focus voltage step [V]
min_dV_focus = 0.1 # smallest allowable focus voltage step [V]
##pvname_I_cath_mon = 'EBIT:CATHCUR:RDCUR' #  pv name of EPICS cathode current readback
##pvname_V_focus_set = 'EBIT:GUNFOCUS:VOL' # pv name of EPICS focus voltage setpoint
run_PID_control = True

sample_interval = 10 # [s]
Kp = 10.
Ki = 1.
Kd = 0.1

pid = PID.PID(Kp, Ki, Kd)
pid.SetPoint = I_target_mA

def createConfig ():
	if not os.path.isfile("./pid.conf"):
		print("{}, {}, {}, {}, {}, {}, {}".format(
		      I_target_mA, Kp, Ki, Kd, V_focus_min, V_focus_max, min_dV_focus))
		with open ("./pid.conf", "w") as f:
			f.write("{}, {}, {}, {}, {}, {}, {}".format(
			        I_target_mA, Kp, Ki, Kd, V_focus_min, V_focus_max, min_dV_focus))

def readConfig ():
	global I_target_mA
	with open ("./pid.conf", "r") as f:
		config = f.readline().split(",")
		pid.SetPoint = float(config[0])
		I_target_mA = pid.SetPoint
		pid.setKp (float(config[1]))
		pid.setKi (float(config[2]))
		pid.setKd (float(config[3]))

createConfig()
i = 1
timestamps = []
I_mon_history = []
V_focus_set_history = []
while run_PID_control:
	readConfig()
	# TODO:  Get emission current readback and focus voltage setpoint
	##I_mon_mA = epics.caget(pvname_I_cath_mon)
	##V_focus_set = epics.caget(pvname_V_focus_set)
	I_mon_mA = I_target_mA*(1+1.0/i)
	V_focus_set = 500.1
	i += 1

	now = datetime.now()
	date_time = now.strftime("%Y-%m-%d_%H:%M:%S")
	pid.update(I_mon_mA)
	dV_focus_set = max_dV_focus*pid.output
	print("{}  I_mon_mA: {:>5.1f} mA,   V_focus_set: {:>5.3f} V,   dV_focus_set: {:>5.3f} V".format(
	      date_time, I_mon_mA, V_focus_set, dV_focus_set))
	if np.abs(I_mon_mA - I_target_mA) < I_mon_res_mA:
		print("Focus voltage kept constant - I_mon and I_target agree within "
		      "the current readback resolution." )
		pass
	elif np.abs(dV_focus_set) < min_dV_focus:
		print("Focus voltage kept constant - "
              "dV_focus_set = {:.3f} < min_dV_focus = {:.3f}".format(
			  dV_focus_set, min_dV_focus))
		pass
	elif V_focus_set + dV_focus_set < V_focus_min:
		print("Focus voltage kept constant - demanded set point "
		      "lies below the allowed focus voltage range.")
		pass
	elif V_focus_set + dV_focus_set > V_focus_max:
		print("Focus voltage kept constant - demanded set point "
		      "lies above the allowed focus voltage range.")
		pass
	else:
		V_focus_set += dV_focus_set
		##epics.caput(pvname_V_focus_set, V_focus_set) # TODO: Update focus voltage setpoint in EPICS
		print("Set focus voltage to: {:.3f}".format(V_focus_set))

	I_mon_history.append(I_mon_mA)
	timestamps.append(date_time)
	V_focus_set_history.append(V_focus_set)
	time.sleep(sample_interval)
