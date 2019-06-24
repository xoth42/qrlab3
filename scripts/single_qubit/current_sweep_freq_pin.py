# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:56:16 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 13:37:44 2018

@author: Wang_Lab
"""


import time
import datetime
#

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
os.chdir(r'C:/qrlab/scripts')

dig = mclient.instruments['dig']
AWG1 = mclient.instruments['AWG1']
Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB0::11::INSTR')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')

cool_time=15e3
cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.12, chan=ef_info.sideband_channels[0]),
                           sequencer.Constant(int(cool_time), 0.12, chan=ef_info.sideband_channels[1]),
                           sequencer.Constant(int(cool_time), 1, chan='3m1')])

from scripts.single_qubit import T2measurement

seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
qubit_freq = 9.44518e+08

results = []
min_result = []
ramp_currents = np.linspace(2.0800e-3, 2.180e-3, 21) #units are in A


for current in ramp_currents:
    Yoko.do_set_current(current)
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 4e3, 101), detune=1e6, double_freq=False, generate=True, 
                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
    t2.measure_keysight()
    results.append(t2.fit_params['freq'].value)



plt.plot(ramp_currents, results)

