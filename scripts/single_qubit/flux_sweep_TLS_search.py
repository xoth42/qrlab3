# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:16:46 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""


import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
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

ef_info = mclient.get_qubit_info('qubit1ef')
os.chdir(r'C:/qrlab/scripts')


cool_time=30e3
cool = sequencer.Combined([sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[0]),
                           sequencer.Constant(int(cool_time), 0.04, chan=ef_info.sideband_channels[1]),
                           sequencer.Constant(int(cool_time), 1, chan='3m1')])
seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])


start_freq = 945000000.0
stop_freq = 5000e6

#start_current = 21.928e-3
#stop_current = 21.958-3

start_current = 61.65e-3
stop_current = 61.67-3
current_step=0.001e-3

Yoko.do_set_current(start_current)
qbrick.set_frequency(start_freq)

fxn_freq1D=[]
fxn_current=[]
fxn_ROpowers =[]
t1_result = []
t1_result2=[]
t1_err = []
t1_err2 =[]
t1_ofs = []
t1_ofs_err = []
t1_amp = []
t1_amp_err = []
t1_amp2 = []
t1_amp2_err = []
T1_Ypoints = []
pi_amp=[]

t2_result =[]
t2_err=[]
t2_amp = []
t2_ofs=[]
t2Echo_result=[]
t2Echo_err=[]
t2Echo_amp=[]
t2Echo_ofs=[]



from single_qubit import ssbspec_lorentzianfit
from single_qubit import contrast_check
from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
from scripts.single_qubit import T2measurement




dig.do_set_naverages(800)
QK_freq = start_freq
current = start_current
ROpower_initial = 10 
sweep_pow = [-2, 2, -4, 4, -6, 6] 

seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
spec.measure_keysight()

    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center

QK_freq = QK_freq + spec.center * 1e6
qbrick.set_frequency(QK_freq)

tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                   update=False, proj_func='phase')

data=tr.measure_keysight()      
ge.set('pi_amp', tr.pi_amp)
pi_amp.append(tr.pi_amp)

qubit_info = mclient.get_qubit_info('qubit1ge')

dig.do_set_naverages(3000)
#
##t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
##                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(20.1e3, 450e3, 60))), 
##                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
##t1.measure_keysight()
##
##t1_result.append(t1.fit_params['tau'].value)
##t1_err.append(t1.fit_params['tau'].stderr)
##t1_ofs.append(t1.fit_params['ofs'].value)
##t1_ofs_err.append(t1.fit_params['ofs'].stderr)
##t1_amp.append(t1.fit_params['amplitude'].value)
##t1_amp_err.append(t1.fit_params['amplitude'].stderr)
##t1_amp2.append(t1.fit_params['amplitude2'].value)
##t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
##t1_result2.append(t1.fit_params['tau2'].value)
##t1_err2.append(t1.fit_params['tau2'].stderr)
##T1_Ypoints.append(t1.get_ys())
#
seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=2e6, double_freq=False, generate=True, 
                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
t2.measure_keysight()
t2_result.append(t2.fit_params['tau'].value)
t2_err.append(t2.fit_params['tau'].stderr)
t2_ofs.append(t2.fit_params['ofs'].value)

seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    postseq = sequencer.Delay(500)
#    for i in range (5):
t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 20e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                     plot_seqs = False, generate=True, proj_func='phase', seq=seq, extra_info=ef_info)
t2.measure_keysight()

t2Echo_result.append(t2.fit_params['tau'].value)
t2Echo_err.append(t2.fit_params['tau'].stderr)
t2Echo_ofs.append(t2.fit_params['ofs'].value)



#dig.do_set_naverages(500)
#
#
fxn_freq1D.append(QK_freq)
fxn_current.append(current)
fxn_ROpowers.append(ROpower_initial)


#time.sleep(.01)   

while QK_freq < stop_freq and current < stop_current:

    current = current + current_step
    Yoko.do_set_current(current)

    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
    spec.measure_keysight()

    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    
#   
    i=0
    
    while contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False and i<(len(sweep_pow)): 
    #Here it should be trying to optimize the RO power and frequency to get the optimal contrast
    #Normally this will be done with histogramming, I will modify this once it is implemented to Keysight Dig
    
    #setting RO power to some other
        RObrick.do_set_power(ROpower_initial + sweep_pow[i])
        print(ROpower_initial + sweep_pow[i])
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
#        plt.close()
    
        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
        
        contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
        i = i+1

    if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
        raise Exception('Could not get good contrast') 

    if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
        ROpower_initial = RObrick.do_get_power()
        
        QK_freq = QK_freq + spec.center * 1e6
        qbrick.set_frequency(QK_freq)
        
        tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                   update=False, seq=None, proj_func='phase')
        data=tr.measure_keysight()

        ge.set('pi_amp', tr.pi_amp)
        pi_amp.append(tr.pi_amp)
        qubit_info = mclient.get_qubit_info('qubit1ge')
        dig.do_set_naverages(3000)
#
##        t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
##                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(20.1e3, 450e3, 60))), 
##                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
##        t1.measure_keysight()
##        
##        t1_result.append(t1.fit_params['tau'].value)
##        t1_err.append(t1.fit_params['tau'].stderr)
##        t1_ofs.append(t1.fit_params['ofs'].value)
##        t1_ofs_err.append(t1.fit_params['ofs'].stderr)
##        t1_amp.append(t1.fit_params['amplitude'].value)
##        t1_amp_err.append(t1.fit_params['amplitude'].stderr)
##        t1_amp2.append(t1.fit_params['amplitude2'].value)
##        t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
##        t1_result2.append(t1.fit_params['tau2'].value)
##        t1_err2.append(t1.fit_params['tau2'].stderr)
##        T1_Ypoints.append(t1.get_ys())
#
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=2e6, double_freq=False, generate=True, 
                                                 seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
        t2.measure_keysight()
        t2_result.append(t2.fit_params['tau'].value)
        t2_err.append(t2.fit_params['tau'].stderr)
        t2_ofs.append(t2.fit_params['ofs'].value)
        
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        #    postseq = sequencer.Delay(500)
        #    for i in range (5):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 20e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                             plot_seqs = False, generate=True, proj_func='phase', seq=seq, extra_info=ef_info)
        t2.measure_keysight()
        
        t2Echo_result.append(t2.fit_params['tau'].value)
        t2Echo_err.append(t2.fit_params['tau'].stderr)
        t2Echo_ofs.append(t2.fit_params['ofs'].value)


        fxn_freq1D.append(QK_freq) 
        fxn_current.append(current)
        fxn_ROpowers.append(ROpower_initial)
        QK_freq = QK_freq + fxn_freq1D[len(fxn_freq1D)-1] - fxn_freq1D[len(fxn_freq1D) - 2] 
        qbrick.set_frequency(QK_freq)
        plt.close('all')



#
#
#
#    
#plt.figure()
#
#
#
plt.plot(fxn_current, fxn_freq1D)

 
np.savetxt('T1_Ypoints_part1.txt', T1_Ypoints)
np.savetxt('fxn_current_part1.txt', fxn_current)
np.savetxt('fxn_freq1D_part1.txt', fxn_freq1D)
np.savetxt('pi_amp_part1.txt', pi_amp)
np.savetxt('t1_amp_part1.txt', t1_amp)
np.savetxt('t1_amp2_part1.txt', t1_amp2)
np.savetxt('t1_amp2_err_part1.txt', t1_amp2_err)
np.savetxt('t1_amp_err_part1.txt', t1_amp_err)      
np.savetxt('t1_err_part1.txt', t1_err)
np.savetxt('t1_err2_part1.txt', t1_err2)
np.savetxt('t1_ofs_part1.txt', t1_ofs)
np.savetxt('t1_ofs_err_part1.txt', t1_ofs_err)
np.savetxt('t1_result_part1.txt', t1_result)    
np.savetxt('t1_result2_part1.txt', t1_result2)
#    
#    
#    
#    
#    
    
    
    
    
    
#IKINCI KISIM


#start_freq = 9.44430E+08
start_freq= 945000000.0
stop_freq = 5000e6

start_current = 61.65e-3
stop_current = 61.63e-3

current_step=-0.001e-3

Yoko.do_set_current(start_current)
qbrick.set_frequency(start_freq)



dig.do_set_naverages(800)
QK_freq = start_freq
current = start_current
ROpower_initial = 10 
sweep_pow = [-2, 2, -4, 4, -6, 6] 

seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
spec.measure_keysight()

    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center

QK_freq = QK_freq + spec.center * 1e6
qbrick.set_frequency(QK_freq)

tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                   update=False, proj_func='phase')

data=tr.measure_keysight()      
ge.set('pi_amp', tr.pi_amp)
pi_amp.append(tr.pi_amp)

qubit_info = mclient.get_qubit_info('qubit1ge')

dig.do_set_naverages(3000)


#t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
#                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(20.1e3, 450e3, 60))), 
#                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
#t1.measure_keysight()
#
#t1_result.append(t1.fit_params['tau'].value)
#t1_err.append(t1.fit_params['tau'].stderr)
#t1_ofs.append(t1.fit_params['ofs'].value)
#t1_ofs_err.append(t1.fit_params['ofs'].stderr)
#t1_amp.append(t1.fit_params['amplitude'].value)
#t1_amp_err.append(t1.fit_params['amplitude'].stderr)
#t1_amp2.append(t1.fit_params['amplitude2'].value)
#t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
#t1_result2.append(t1.fit_params['tau2'].value)
#t1_err2.append(t1.fit_params['tau2'].stderr)
#T1_Ypoints.append(t1.get_ys())
seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=2e6, double_freq=False, generate=True, 
                                         seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
t2.measure_keysight()
t2_result.append(t2.fit_params['tau'].value)
t2_err.append(t2.fit_params['tau'].stderr)
t2_ofs.append(t2.fit_params['ofs'].value)

seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
#    postseq = sequencer.Delay(500)
#    for i in range (5):
t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 20e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                     plot_seqs = False, generate=True, proj_func='phase', seq=seq, extra_info=ef_info)
t2.measure_keysight()

t2Echo_result.append(t2.fit_params['tau'].value)
t2Echo_err.append(t2.fit_params['tau'].stderr)
t2Echo_ofs.append(t2.fit_params['ofs'].value)

dig.do_set_naverages(800)


fxn_freq1D.append(QK_freq)
fxn_current.append(current)
fxn_ROpowers.append(ROpower_initial)


#time.sleep(.01)   



while QK_freq < stop_freq and current > stop_current:

    current = current + current_step
    Yoko.do_set_current(current)

    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
    spec.measure_keysight()

    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    
#   
    i=0
    
    while contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False and i<(len(sweep_pow)): 
    #Here it should be trying to optimize the RO power and frequency to get the optimal contrast
    #Normally this will be done with histogramming, I will modify this once it is implemented to Keysight Dig
    
    #setting RO power to some other
        RObrick.do_set_power(ROpower_initial + sweep_pow[i])
        print(ROpower_initial + sweep_pow[i])
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
        spec.measure_keysight()
#        plt.close()
    
        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
        
        contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
        i = i+1

    if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
        raise Exception('Could not get good contrast') 

    if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
        ROpower_initial = RObrick.do_get_power()
        
        QK_freq = QK_freq + spec.center * 1e6
        qbrick.set_frequency(QK_freq)
        
        tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                   update=False, seq=None, proj_func='phase')
        data=tr.measure_keysight()

        ge.set('pi_amp', tr.pi_amp)
        pi_amp.append(tr.pi_amp)
        qubit_info = mclient.get_qubit_info('qubit1ge')
        dig.do_set_naverages(3000)
        
#        t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
#                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(20.1e3, 450e3, 60))), 
#                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
#        t1.measure_keysight()
#        
#        t1_result.append(t1.fit_params['tau'].value)
#        t1_err.append(t1.fit_params['tau'].stderr)
#        t1_ofs.append(t1.fit_params['ofs'].value)
#        t1_ofs_err.append(t1.fit_params['ofs'].stderr)
#        t1_amp.append(t1.fit_params['amplitude'].value)
#        t1_amp_err.append(t1.fit_params['amplitude'].stderr)
#        t1_amp2.append(t1.fit_params['amplitude2'].value)
#        t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
#        t1_result2.append(t1.fit_params['tau2'].value)
#        t1_err2.append(t1.fit_params['tau2'].stderr)
#        T1_Ypoints.append(t1.get_ys())
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 5e3, 101), detune=2e6, double_freq=False, generate=True, 
                                                 seq=seq, extra_info=ef_info, postseq=None, proj_func='phase')
        t2.measure_keysight()
        t2_result.append(t2.fit_params['tau'].value)
        t2_err.append(t2.fit_params['tau'].stderr)
        t2_ofs.append(t2.fit_params['ofs'].value)
        
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        #    postseq = sequencer.Delay(500)
        #    for i in range (5):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 20e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, 
                                             plot_seqs = False, generate=True, proj_func='phase', seq=seq, extra_info=ef_info)
        t2.measure_keysight()
        
        t2Echo_result.append(t2.fit_params['tau'].value)
        t2Echo_err.append(t2.fit_params['tau'].stderr)
        t2Echo_ofs.append(t2.fit_params['ofs'].value)

        dig.do_set_naverages(800)


        fxn_freq1D.append(QK_freq) 
        fxn_current.append(current)
        fxn_ROpowers.append(ROpower_initial)
        QK_freq = QK_freq + fxn_freq1D[len(fxn_freq1D)-1] - fxn_freq1D[len(fxn_freq1D) - 2] 
        qbrick.set_frequency(QK_freq)
        plt.close('all')






    
plt.figure()



plt.plot(fxn_current, fxn_freq1D, linestyle='None', marker='.', markersize=7)       

    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#    
#        
#    
#    
#    
#
#
#
#
#
#
#
#
#
#
#
#    
#        
#    
    
    
    
    
    
        
    
    
    











    
    