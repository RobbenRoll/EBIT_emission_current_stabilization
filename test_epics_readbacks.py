import epics

pvname_cath_curr = "EBIT:CATHCUR:RDCUR"
pvname_V_focus_mon = "EBIT:GUNFOCUS:RDVOL"

I_mon = epics.caget(pvname_cath_curr)
V_focus_mon = epics.caget(pvname_V_focus_mon)
print("CATHCUR:RDCUR: {:.3f} mA, GUNFOCUS:RDVOL: {:.3f} V".format(I_mon, V_focus_mon))
