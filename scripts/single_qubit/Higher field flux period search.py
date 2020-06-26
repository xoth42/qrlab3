# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 20:55:46 2019

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
#ef_info = mclient.get_qubit_info('qubit1ef')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')

start_freq = 840e6
start_current = 0.14e-3  #This is the flux point in question for the frequency above
stop_current = 0.14e-3
current_step=0.00e-3
qbrick.set_frequency(start_freq)

from single_qubit import ssbspec


current = start_current
Yoko.do_set_current(current)
time.sleep(.2)

seq = sequencer.Trigger(600)
spec = ssbspec.SSBSpec(qubit_info, np.linspace(-30e6, 30e6, 81), seq=None, plot_seqs=False, proj_func='phase')
spec.measure_keysight()

current = current + current_step

Yoko.do_set_current(current)
time.sleep(.2)

while current < stop_current:
        seq = sequencer.Trigger(600)
        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-30e6, 30e6, 81), seq=None, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
        current = current + current_step
        Yoko.do_set_current(current)
        plt.close('all')



#start_freq = 4e9
#current=0.146e-3
##start_current = 1.99e-3  #This is the flux point in question for the frequency above
#stop_freq=4.5e9
#freq_step=50e6
#Yoko.do_set_current(current)
#qbrick.set_frequency(start_freq)
#freq = start_freq
#from single_qubit import ssbspec
#
#
#time.sleep(.2)
#
#seq = sequencer.Trigger(600)
#spec = ssbspec.SSBSpec(qubit_info, np.linspace(-50e6, 50e6, 151), seq=None, plot_seqs=False, proj_func='phase')
#spec.measure_keysight()
#
#freq = freq + freq_step
#qbrick.set_frequency(freq)
#time.sleep(.2)
#
#while freq < stop_freq:
#        seq = sequencer.Trigger(600)
#        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-50e6, 50e6, 151), seq=None, plot_seqs=False, proj_func='phase')
#        spec.measure_keysight()
#        freq = freq + freq_step
#        qbrick.set_frequency(freq)
#        plt.close('all')



