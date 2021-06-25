# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 16:04:17 2021

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
import os
import time
import math
import lmfit
import time
import datetime


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
ef2_info = mclient.get_qubit_info('qubit2ef')
ef2_info_set = mclient.instruments['qubit2ef']
#ef2_V2_info = mclient.get_qubit_info('qubit2ef_V2')
#fwm_info = mclient.get_qubit_info('fwm_info1')
#fwm_info2 = mclient.get_qubit_info('fwm_info2')
mixer_info1 = mclient.get_qubit_info('mixer_info1')
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
SS_mixer_info2 = mclient.get_qubit_info('SS_mixer_info2')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
mixer_info1_set = mclient.instruments['mixer_info1']
mixer_info2_set = mclient.instruments['mixer_info2']
SS_mixer_info1_set = mclient.instruments['SS_mixer_info1']
SS_mixer_info2_set = mclient.instruments['SS_mixer_info2']
#fwm2_info = mclient.get_qubit_info('fwm_info2')
#qubit03_info = mclient.get_qubit_info('qubit1_03')
#qubit14_info = mclient.get_qubit_info('qubit1_14')
readout_info = mclient.get_readout_info('readout')
#readout = 'readout_IQ'
readout = mclient.instruments['readout']
readout_IQ = mclient.instruments['readout_IQ']
alz = mclient.instruments['alazar']
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')

#fwm_gen = mclient.instruments['SS_drive']
#fwm_gen2 = mclient.instruments['SC_qubit2FWM']
os.chdir(r'C:/qrlab/scripts')


def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )

    est = est + params['roff'] + 1j*params['ioff']
    
    return np.abs(est) - y

def gaussian(params, x, data):
    return data - params['amp'] * np.exp(-.5 * ((x - params['mean']) / params['std'])**2)

#cool_time=10e3
#cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[0]),
#                           sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[1]),
#                           sequencer.Constant(int(cool_time), 1, chan='3m1')])


alz.set_naverages(20000)
repeat = 1

if 1: #T2 mixer
    from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(repeat):
        t2 = T2measurement_mixer.T2Measurement_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(0, 30e3, 101), 
                                                     detune=.3e6, double_freq=False, generate=True, echotype = 'HANN',
                                                     seq=None, postseq=None,plot_seqs = False, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure()
    
if 1: #T2 mixer
    from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(repeat):
        t2 = T2measurement_mixer.T2Measurement_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(0, 8e3, 101), 
                                                     detune=1e6, double_freq=False, generate=True, echotype = 'NONE',
                                                     seq=None, postseq=None,plot_seqs = False, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

        
        t2.measure()
    
if 1: # T1 mixer

    from single_qubit import T1measurement_mixer
    for i in range(repeat):
#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    postseq = sequencer.Combined([
#                sequencer.Join([mixer_info1.rotate(np.pi, 0),sequencer.Delay(5)]),
#                sequencer.Join([mixer_info2.rotate(np.pi, 0),sequencer.Delay(5)])
#            ])
        t1 = T1measurement_mixer.T1Measurement_mixer(qubit2_info, mixer_info1,mixer_info2, #np.linspace(0, 500e3, 101),
                                             np.linspace(0e3, 30e3, 101),
    #                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                             double_exp=False,postseq = None, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
        t1.measure()

bla