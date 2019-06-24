# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 14:55:43 2018

@author: wanglab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
matplotlib.rcParams['backend'] = 'Qt4Agg'
matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
import math as math
import time


import os
os.chdir(r'c:\qrlab')

#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']


qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')

ge = mclient.instruments['qubit1ge']

yoko = mclient.instruments['yoko']
qbrick = mclient.instruments['qbrick']
#RObrick = mclient.instruments['RObrick']
#refbrick = mclient.instruments['refFG']


currents = np.linspace(0, 0.1, 11)
yoko.set_output_state(1) 
ssbspec_freqs = np.linspace(-1.5e6, 1.5e6, 101) #range of points to check each ssbspec
qbrick_freq = 6305.75e6
#RObrick_freq = 7348.8e6
#w = 30
#w_selective = 300
#pi_amp_initial = .1678
default_sideband = 100e6


w_q = np.zeros_like(currents)

qbrick.set_frequency(qbrick_freq)
#RObrick.set_frequency(RObrick_freq)
#refbrick.set_frequency(RObrick_freq+50e6)
#time.sleep(1)


for i in range(len(currents)):
    
    yoko.do_set_current(currents[i])
    time.sleep(.5)
    
             
    '''Here we do an SSB spec'''
    from scripts.single_qubit import ssbspec
    seq = sequencer.Trigger(250)        
    spec = ssbspec.SSBSpec(qubit_info, ssbspec_freqs, seq=seq, plot_seqs=False)
    spec.measure()
    drive_freq = qbrick.get_frequency()
    w_q[i] = ssbspec_freqs[np.argmin(spec.get_ys())] + drive_freq - default_sideband
    
    time.sleep(1)

plt.figure()


plt.plot(currents, w_q/1e6)
plt.ylabel('w_q (MHz)')
plt.xlabel('current [mA]')


plt.plot()

yoko.set_output_state(0)    

