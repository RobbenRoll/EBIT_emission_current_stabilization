#!/usr/bin/python
# Software PID controller for EBIT beam current stabilitzation
# Regulates the focus bias in order to stabilize the cathode emission current
import epics
from ivPID import PID
import time
from datetime import datetime
import numpy as np
import json
import csv

class BeamCurrentStabilizer():
	_pvname_I_target_mA = 'EBIT:CATHCUR:RDCUR' #  pv name of EPICS cathode current readback
	_pvname_V_focus_set = 'EBIT:GUNFOCUS:VOL' # pv name of EPICS focus voltage setpoint
	_max_I_target_mA = 1000
	_default_config = {"I_target_mA" : 50, # target current [mA]
	                   "V_focus_min" : 400, # minimal allowable focus voltage [V]
					   "V_focus_max" : 600, # maximal allowable focus voltage [V]
					   "Kp" : 0.2, "Ki" : 0.0, "Kd" : 0.0,
					   "min_dV_focus" : 0.1, # minimal allowable focus voltage step [V]
					   "max_dV_focus" : 5.0, # maximal allowable focus voltage step [V] #TODO: RENAME
					   "I_resolution_mA" : 0.24, # resolution of current readback
					   "sampling_interval" : 10
		   }
	def __init__(self, use_default_config=False):
		if use_default_config:
			self.I_target_mA = self._default_config["I_target_mA"]
			self.pid = PID.PID()
			self.pid.setKp(self._default_config["Kp"])
			self.pid.setKi(self._default_config["Ki"])
			self.pid.setKd(self._default_config["Kd"])
			self.pid.SetPoint = self.I_target_mA
			self.V_focus_min = self._default_config["V_focus_min"]
			self.V_focus_max = self._default_config["V_focus_max"]
			self.min_dV_focus = self._default_config["min_dV_focus"]
			self.max_dV_focus = self._default_config["max_dV_focus"]
			self.I_resolution_mA = self._default_config["I_resolution_mA"]
			self.sampling_interval = self._default_config["sampling_interval"]
		else:
			self.load_config(reset_pid=True)

	def save_config(self, fname="stabilizer_config.json"):
		"""Write current stabilizer configuration to json file"""
		config = {"I_target_mA" : self.I_target_mA,
				  "V_focus_min" : self.V_focus_min,
				  "V_focus_max" : self.V_focus_max,
		          "Kp" : self.pid.Kp, "Ki" : self.pid.Ki, "Kd" : self.pid.Kd,
				  "min_dV_focus" : self.min_dV_focus,
				  "max_dV_focus" : self.max_dV_focus,
				  "I_resolution_mA" : self.I_resolution_mA,
				   "sampling_interval" : self.sampling_interval}
		with open(fname, "w") as file:
			json.dump(config, file, sort_keys=False, indent=4)

	def load_config(self, fname="stabilizer_config.json", reset_pid=True):
		"""Load config from json file"""
		with open(fname, "r") as file:
			config = json.load(file)
		self.I_target_mA = config["I_target_mA"]
		if reset_pid:
			self.pid = PID.PID()
		self.pid.setKp(config["Kp"])
		self.pid.setKi(config["Ki"])
		self.pid.setKd(config["Kd"])
		self.pid.SetPoint = config["I_target_mA"]
		self.V_focus_min = config["V_focus_min"]
		self.V_focus_max = config["V_focus_max"]
		self.min_dV_focus = config["min_dV_focus"]
		self.max_dV_focus = config["max_dV_focus"]
		self.I_resolution_mA = config["I_resolution_mA"]
		self.sampling_interval = config["sampling_interval"]

	def set_target_current(self, I_target_mA, V_focus_min=None, V_focus_max=None):
		"""Update target current and optionally update focus voltage limits"""
		self.I_target_mA = I_target_mA
		self.pid.SetPoint = I_target_mA
		self.V_focus_min = V_focus_min or self.V_focus_min
		self.V_focus_max = V_focus_max or self.V_focus_max

	def activate(self, write_logs=True):
		print("\n##### Starting beam current stabilization #####")
		if self.I_target_mA > self._max_I_target_mA:
			raise Exception("Set target exceeds maximum allowable target current!")
		self.save_config()
		## i = 0 # for testing only ## TODO: remove after testing
		if write_logs:
			now = datetime.now()
			date_time = now.strftime("%Y-%m-%d_%H%M%S")
			self.save_config(fname="logs/"+date_time+"_config.json")
			fname = date_time+"_stabilization_log.csv"
			f = open("logs/"+fname, "w", newline="")
			log = csv.writer(f)
			log.writerow(["Datetime", " I_mon [mA]", " V_focus_set [V]"])
			print("Saving config and stabilization history to ./logs/")
		try:
			while True:
				self.load_config(reset_pid=False)
				# TODO:  Get emission current readback and focus voltage setpoint
				I_mon_mA = epics.caget(self._pvname_I_target_mA) ## self.I_target_mA*(1+1.0/(i+1)) # for testing
				V_focus_set = epics.caget(self._pvname_V_focus_set) # 500.1 # for testing
				##i += 1 # for testing ## TODO: remove after testing

				now = datetime.now()
				date_time = now.strftime("%Y-%m-%d %H:%M:%S")
				self.pid.update(I_mon_mA)
				dV_focus_set = self.pid.output
				print("{}  I_mon: {:>5.3f} mA,  V_focus_set: {:>5.3f} V,  dV_focus_set: {:>6.3f} V".format(
				      date_time, I_mon_mA, V_focus_set, dV_focus_set))
				if np.abs(I_mon_mA - self.I_target_mA) < self.I_resolution_mA:
					print("Focus voltage kept constant - I_mon and I_target "
					      "agree within the current readback resolution." )
					pass
				elif V_focus_set + dV_focus_set < self.V_focus_min:
					print("Focus voltage kept constant - demanded set point "
					      "lies below the allowed focus voltage range.")
					pass
				elif V_focus_set + dV_focus_set > self.V_focus_max:
					print("Focus voltage kept constant - demanded set point "
					      "lies above the allowed focus voltage range.")
					pass
				elif np.abs(dV_focus_set) < self.min_dV_focus:
					print("Focus voltage kept constant - "
			              "dV_focus_set = {:.3f} < min_dV_focus = {:.3f}".format(
						  dV_focus_set, self.min_dV_focus))
					pass
				else:
					if np.abs(dV_focus_set) > self.max_dV_focus:
						print("Proposed voltage step truncated to maximal "
						      "allowed value ({:.3f}V).".format(self.max_dV_focus))
						dV_focus_set = np.sign(dV_focus_set)*self.max_dV_focus
					V_focus_set += dV_focus_set
					epics.caput(self._pvname_V_focus_set, V_focus_set) ##
					print("Set focus voltage to: {:.3f} V".format(V_focus_set))

				if write_logs:
					log.writerow([date_time," {:.3f}".format(I_mon_mA)," {:.3f}".format(V_focus_set)])
				time.sleep(self.sampling_interval)
		except KeyboardInterrupt:
			if write_logs:
				f.close()
			print("\nStabilization stopped.\n")

if __name__ == "__main__":
	try:
		stabilizer = BeamCurrentStabilizer(use_default_config=False)
		print("Loaded configuration from stabilizer_config.json")
		print("\nSet target beam current: {:.1f} mA".format(stabilizer.I_target_mA))
		print("Set focus voltage limits (min / max): {:.3f} / {:.3f} V".format(
		                        stabilizer.V_focus_min, stabilizer.V_focus_max))
	except FileNotFoundError:
		stabilizer = BeamCurrentStabilizer(use_default_config=True)
		print("Loading configuration from 'stabilizer_config.json' failed. Loading default configuration instead.")
		print("\nSet target beam current: {:.1f} mA".format(stabilizer.I_target_mA))
		print("Set focus voltage limits (min/max): {:.3f} / {:.3f} V".format(
		                        stabilizer.V_focus_min, stabilizer.V_focus_max))
	run_stabilizer = input("\nActivate beam current stabilization with the above parameters? (y/n)")
	if run_stabilizer in ["Y", "y", "Yes", "yes", "YES"]:
		stabilizer.activate(write_logs=True)
	else:
		pass
