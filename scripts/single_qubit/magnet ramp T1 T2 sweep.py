# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 17:30:24 2019

@author: Wang_Lab
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
from pulseseq import sequencer, pulselib
import os
import time
import math
import datetime



qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
Yoko = mclient.instruments['Yoko']
qbrick = mclient.instruments['QK']
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']



freq = 946.465e6
#start_freq = 1245.31e6 #This should not be a guess but some frequency previously confirmed to be the correct qubit freq at the given flux point.

#
start_current = 1.879e-3
#start_current = 1.99e-3  #This is the flux point in question for the frequency above

current_step=0
Yoko.do_set_current(1.879e-3)

qbrick.set_frequency(freq)
fxn_freq1D=[]
fxn_current=[]
fxn_ROpowers =[]
t1_result = []
t1_err = []
t1_ofs = []
t1_ofs_err = []
t1_amp = []
t1_amp_err = []
t2_result =[]
t2_err=[]
t2_amp = []
t2_ofs=[]
t2Echo_result=[]
t2Echo_err=[]
t2Echo_amp=[]
t2Echo_ofs=[]

pi_amp=[]





from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
from scripts.single_qubit import T2measurement







for i in range(40): 
    
    dig.do_set_naverages(5000)
    tr = rabi.Rabi(qubit_info, np.linspace(-0.5, 0.5, 101), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                   update=False, proj_func='phase')

    data=tr.measure_keysight()      
    ge.set('pi_amp', tr.pi_amp)
    pi_amp.append(tr.pi_amp)


    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 120e3, 121), double_exp=False, generate=True, plot_seqs=False, proj_func='phase')
    t1.measure_keysight()
    t1_result.append(t1.fit_params['tau'].value)
    t1_err.append(t1.fit_params['tau'].stderr)
    t1_ofs.append(t1.fit_params['ofs'].value)
    t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    t1_amp.append(t1.fit_params['amplitude'].value)
    t1_amp_err.append(t1.fit_params['amplitude'].stderr)


    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 8e3, 101), detune=1e6, double_freq=False, generate=True, proj_func='phase')
    t2.measure_keysight()
    t2_result.append(t2.fit_params['tau'].value)
    t2_err.append(t2.fit_params['tau'].stderr)
    t2_ofs.append(t2.fit_params['ofs'].value)



    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 20e3, 101), detune=0.2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase')
    t2.measure_keysight()
    t2Echo_result.append(t2.fit_params['tau'].value)
    t2Echo_err.append(t2.fit_params['tau'].stderr)
    t2Echo_ofs.append(t2.fit_params['ofs'].value)
    plt.close('all')



