# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 11:28:59 2020

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
readout = 'readout_IQ'
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')

#fwm_gen = mclient.instruments['SS_drive']
#fwm_gen2 = mclient.instruments['SC_qubit2FWM']
os.chdir(r'C:/qrlab/scripts')


ro_freq_qubit2 = 10.815e9
ro_freq_qubit1 = 10.811e9


power = 10
readout_info.rfsource1.set_frequency(ro_freq_qubit2 - mixer_info1.deltaf)
readout_info.rfsource1.set_power(power)
deltaf = 10.811e9 - ro_freq_qubit2 + mixer_info1.deltaf
SS_mixer_info1_set.set_deltaf(deltaf)
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')

mixer_info1_set.set_pi_amp(.01)
mixer_info2_set.set_pi_amp(.12)
mixer_info1 = mclient.get_qubit_info('mixer_info1')
mixer_info2 = mclient.get_qubit_info('mixer_info2')


from single_qubit import ssbspec_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
for i in range(1):        
#        RObrick.do_set_power(i)
    seq = sequencer.Trigger(600)
#        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
    spec = ssbspec_mixer.SSBSpec_mixer(qubit2_info, mixer_info1,mixer_info2, np.linspace(-10e6, 10e6, 101), seq=seq, 
                                       plot_seqs=True, proj_func='phase')
    spec.measure_keysight()
    
    
    
    
    
from single_qubit import rabi_mixer
import time
update_proj =False
seq = sequencer.Sequence([sequencer.Trigger(400),sequencer.Delay(10)])

for i in range(1):

    tr = rabi_mixer.Rabi_mixer(qubit2_info, mixer_info1, mixer_info2,
#                               np.linspace(-0.9, 0.9, 81), selective=False,
                               np.linspace(-0.8, 0.8, 101), selective=False,
#                               np.linspace(-0.14, 0.14, 81), selective=True,
#                               np.linspace(-0.1, 0.1, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,# fix_period = 0.88,#postseq = postseq,
                               update=True, #extra_info=[qubit_info],
                               proj_func='phase')
    tr.measure_keysight()



    
from single_qubit import T1measurement_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

t1 = T1measurement_mixer.T1Measurement_mixer(qubit2_info, mixer_info1,mixer_info2, #np.linspace(0, 500e3, 101),
                                     np.linspace(0.1e3, 3e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                     double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
t1.measure_keysight()    



from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
for i in range(1):
    t2 = T2measurement_mixer.T2Measurement_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(0, 5e3, 101), 
                                                 detune=2e6, double_freq=False, generate=True,# echotype = 'HANN',
                                                 seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

    
    t2.measure_keysight()
    
    
from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
for i in range(1):
    t2 = T2measurement_mixer.T2Measurement_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(0, 5e3, 101), 
                                                 detune=2e6, double_freq=False, generate=True, echotype = 'HANN',
                                                 seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

    
    t2.measure_keysight()
    

power = 10
readout_info.rfsource1.set_frequency(ro_freq_qubit1 - mixer_info1.deltaf)
readout_info.rfsource1.set_power(power)
deltaf = 10.811e9 - ro_freq_qubit1 + mixer_info1.deltaf
SS_mixer_info1_set.set_deltaf(deltaf)
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
 

mixer_info1_set.set_pi_amp(.12)
mixer_info2_set.set_pi_amp(.12)
mixer_info1 = mclient.get_qubit_info('mixer_info1')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
   
from single_qubit import ssbspec_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
for i in range(1):        
#        RObrick.do_set_power(i)
    seq = sequencer.Trigger(600)
#        seq = Join([seq, qubit2_info.rotate(np.pi/2, X_AXIS)])
    spec = ssbspec_mixer.SSBSpec_mixer(qubit_info, mixer_info1,mixer_info2, np.linspace(-50e6, 50e6, 101), seq=seq, 
                                       plot_seqs=True, proj_func='phase')
    spec.measure_keysight()
    
    
    
    
    
from single_qubit import rabi_mixer
import time
update_proj =False
seq = sequencer.Sequence([sequencer.Trigger(400),sequencer.Delay(10)])

for i in range(1):

    tr = rabi_mixer.Rabi_mixer(qubit_info, mixer_info1, mixer_info2,
#                               np.linspace(-0.9, 0.9, 81), selective=False,
                               np.linspace(-0.7, 0.7, 101), selective=False,
#                               np.linspace(-0.14, 0.14, 81), selective=True,
#                               np.linspace(-0.1, 0.1, 81), selective=True,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=seq,# fix_period = 0.88,#postseq = postseq,
                               update=True, #extra_info=[qubit_info],
                               proj_func='phase')
    tr.measure_keysight()



    
from single_qubit import T1measurement_mixer

#    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 250e3, 121), 
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(2000, 1, chan='3m1'), sequencer.Delay(250),
#                          ef_info.rotate(np.pi, 0), sequencer.Constant(4000, 1, chan='3m1'), sequencer.Delay(250)])
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])

t1 = T1measurement_mixer.T1Measurement_mixer(qubit_info, mixer_info1,mixer_info2, #np.linspace(0, 500e3, 101),
                                     np.linspace(0.1e3, 3e3, 101),
#                                         np.concatenate((np.linspace(5e3, 5e3, 50), np.linspace(6e3, 6e3, 51))),
                                     double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)    
t1.measure_keysight()    



from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
for i in range(1):
    t2 = T2measurement_mixer.T2Measurement_mixer(qubit_info, mixer_info1, mixer_info2, np.linspace(0, 0.5e3, 101), 
                                                 detune=20e6, double_freq=False, generate=True,# echotype = 'HANN',
                                                 seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

    
    t2.measure_keysight()
    
    
from single_qubit import T2measurement_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
for i in range(1):
    t2 = T2measurement_mixer.T2Measurement_mixer(qubit_info, mixer_info1, mixer_info2, np.linspace(0, 0.5e3, 101), 
                                                 detune=20e6, double_freq=False, generate=True, echotype = 'HANN',
                                                 seq=None, postseq=None, proj_func='phase') #extra_info=[qubit2_info])
#        t2 = T2measurement.T2Measurement(qubit_info, np.concatenate((np.linspace(0.1e3, 2.6e3, 81), np.linspace(2.61e3, 10e3, 81))), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')

    
    t2.measure_keysight()