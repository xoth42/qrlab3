# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 14:55:43 2018

@author: wanglab
"""

import mclient
import importlib
importlib.reload(mclient)
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
SC_Qubit = mclient.instruments['SC_Qubit']
#RObrick = mclient.instruments['RObrick']
#refbrick = mclient.instruments['refFG']



currents = np.linspace(-4.9352, -4.7352, 5)
yoko.set_output_state(1) 
ssbspec_freqs = np.linspace(-20e6, 20e6, 201) #range of points to check each ssbspec
qubit_drive_freq = 5445.725e6

#RObrick_freq = 7348.8e6
#w = 30
#w_selective = 300
#pi_amp_initial = .1678
default_sideband = 100e6


w_q = np.zeros_like(currents)

SC_Qubit.set_frequency(qubit_drive_freq)
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
    spec.measure_keysight()
    drive_freq = SC_Qubit.get_frequency()
    w_q[i] = ssbspec_freqs[np.argmin(spec.get_ys())] + drive_freq - default_sideband
    
    time.sleep(1)

plt.figure()


plt.plot(currents, w_q/1e6)
plt.ylabel('w_q (MHz)')
plt.xlabel('current [mA]')


plt.plot()

#yoko.set_output_state(0)    

