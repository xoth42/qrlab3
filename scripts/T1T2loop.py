# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 23:42:09 2019

@author: Wang_Lab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib.pyplot as plt

fxa01 = mclient.get_qubit_info('fxa01')
fxb01 = mclient.get_qubit_info('fxb01')

from single_qubit import T1measurement
from single_qubit import T2measurement

for i in range(5):
    t1a = T1measurement.T1Measurement(fxa01, np.concatenate((np.linspace(0, 96e3, 25), np.linspace(100e3, 450e3, 36))), 
                                     double_exp=False, generate=True, plot_seqs=False, seq=None, proj_func='phase')
    t1a.measure_keysight()

    t1b = T1measurement.T1Measurement(fxb01, np.concatenate((np.linspace(0, 48e3, 25), np.linspace(50e3, 450e3, 41))), 
                                     double_exp=False, generate=True, plot_seqs=False, seq=None, proj_func='phase')
    t1b.measure_keysight()
    
    t2a = T2measurement.T2Measurement(fxa01, np.linspace(4e3, 34e3, 91), detune=0.2e6, 
                                     double_freq=False, generate=True, seq=None, proj_func='phase')
    t2a.measure_keysight()

    t2b = T2measurement.T2Measurement(fxb01, np.linspace(4e3, 34e3, 91), detune=0.2e6,
                                     double_freq=False, generate=True, seq=None, proj_func='phase')
    t2b.measure_keysight()

    t2ea = T2measurement.T2Measurement(fxa01, np.linspace(8e3, 58e3, 101), detune=0.2e6, 
                                     echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase')
    t2ea.measure_keysight()

    t2eb = T2measurement.T2Measurement(fxa01, np.linspace(8e3, 58e3, 101), detune=0.2e6, 
                                     echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase')
    t2eb.measure_keysight()
