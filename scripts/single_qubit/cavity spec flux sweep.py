# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 19:15:43 2018

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 13:37:44 2018

@author: Wang_Lab
"""

import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as plt
from pulseseq import sequencer, pulselib
import matplotlib as mpl
import math as math
import time
import datetime

#alz = mclient.instruments['alazar']
#yoko1 = mclient.instruments['yoko1']
dig = instruments.create('dig', 'Keysight_DIG', chassis = 0, slot = 3, trigger_period=500)
#yoko2 = mclient.instruments['yoko2']
Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
readout_info = mclient.get_readout_info()

from scripts.single_cavity import rocavspectroscopy_keysight

#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen

rofreq = 7596.1e6
freq_range = 20e6
freq_points =51

ramp_currents = np.linspace(-0.34e-3, -0.32e-3, 22) #units are in A

current = ramp_currents[0]
Yoko.do_set_current(current)

ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-40, -40, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 51),
                                             qubit_pulse=False)
ro.measure()



for current in ramp_currents[1:]:
    #yoko1.do_set_current(current)
    Yoko.do_set_current(current)
    rofreq = 7596.1e6
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-40, -40, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 51),
                                             qubit_pulse=False)
    ro.measure()

plt.figure()
