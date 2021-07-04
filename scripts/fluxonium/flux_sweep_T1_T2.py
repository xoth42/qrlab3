# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""

#This spectroscopy is intended to follow one specific transition over the full flux period and not to get the full spectrum of the device. It makes use of SSB spec rather than the regular spectroscopy
#with the hope that we can avoid the current crashing problem. -Ebru



import mclient
import importlib
importlib.reload(mclient)
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
yoko = mclient.instruments['yoko']
qbrick = mclient.instruments['gaius01']
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']
os.chdir(r'C:/qrlab/scripts')

start_freq =1090e6
#start_freq = 1245.31e6 #This should not be a guess but some frequency previously confirmed to be the correct qubit freq at the given flux point.
stop_freq = 1190e6
#
start_current = -1.96e-3
#start_current = 1.99e-3  #This is the flux point in question for the frequency above
stop_current = -1.93e-3
#stop_current = -1.876e-3
current_step=0.01e-3
yoko.do_ramp_current(start_current)
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
#t2_result =[]
#t2_err=[]
#t2_amp = []
#t2_ofs=[]
#t2Echo_result=[]
#t2Echo_err=[]
#t2Echo_amp=[]
#t2Echo_ofs=[]
T1_Ypoints = []
#T1_Xpoints = np.concatenate(np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36))

pi_amp=[]



from single_qubit import ssbspec_lorentzianfit
from single_qubit import contrast_check
from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
#from scripts.single_qubit import T2measurement

#def run_measurement():
##    if freqrange = None:
##        freqrange= 50e6
#    seq = sequencer.Trigger(600)
#    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-50e6, 50e6, 201), seq=seq, plot_seqs=False, proj_func='phase')
#    spec.measure()
#    
#    XS = spec.xs
#    YS = spec.get_ys()
#    width = spec.width()
#    height = spec.height
#    center = spec.center

dig.do_set_naverages(2000)
QK_freq = start_freq
current = start_current
ROpower_initial = 5 
sweep_pow = [5] #bunu linspace tarzi bir seye donusturmek gerekebilir

seq = sequencer.Trigger(600)
spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-10e6, 10e6, 81), seq=None, plot_seqs=False, proj_func='phase')
spec.measure()
#plt.close()
    
XS = spec.xs
YS = spec.get_ys()
width = spec.width()
height = spec.height
center = spec.center

QK_freq = QK_freq + spec.center * 1e6
qbrick.set_frequency(QK_freq)

tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                   update=False, proj_func='phase')

data=tr.measure()      
ge.set('pi_amp', tr.pi_amp)
pi_amp.append(tr.pi_amp)

qubit_info = mclient.get_qubit_info('qubit1ge')

dig.do_set_naverages(2500)

t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                     np.concatenate((np.linspace(0.1e3, 0.9e3, 15), np.linspace(1e3, 10e3, 31), np.linspace(11e3, 45e3, 40))), 
                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
t1.measure()

t1_result.append(t1.fit_params['tau'].value)
t1_err.append(t1.fit_params['tau'].stderr)
t1_ofs.append(t1.fit_params['ofs'].value)
t1_ofs_err.append(t1.fit_params['ofs'].stderr)
t1_amp.append(t1.fit_params['amplitude'].value)
t1_amp_err.append(t1.fit_params['amplitude'].stderr)
t1_amp2.append(t1.fit_params['amplitude2'].value)
t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
t1_result2.append(t1.fit_params['tau2'].value)
t1_err2.append(t1.fit_params['tau2'].stderr)
T1_Ypoints.append(t1.get_ys())



#t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=None,  postseq=None, proj_func='phase')
#t2.measure()
#t2_result.append(t2.fit_params['tau'].value)
#t2_err.append(t2.fit_params['tau'].stderr)
#t2_ofs.append(t2.fit_params['ofs'].value)


#t2_amp.append(t2.fit_params['amplitude'].value)


#t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 15e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, seq=None, plot_seqs = False, generate=True, proj_func='phase')
#t2.measure()
#t2Echo_result.append(t2.fit_params['tau'].value)
#t2Echo_err.append(t2.fit_params['tau'].stderr)
#t2Echo_ofs.append(t2.fit_params['ofs'].value)
#t2Echo_amp.append(t2.fit_params['amplitude'].value)
##This code strictly assumes that the first run is an accurate guess.
dig.do_set_naverages(2000)

#phase=np.asarray(YS[:])
#phase=phase[:,None].T
fxn_freq1D.append(QK_freq)
#fxn_freq = np.asarray(XS + QK_freq)
#fxn_freq=fxn_freq[:,None].T
fxn_current.append(current)
fxn_ROpowers.append(ROpower_initial)


#time.sleep(.01)   

while QK_freq < stop_freq and current < stop_current:
#    if current == 2e-3:
#        dig.do_set_naverages = 2000
    current = current + current_step
    yoko.do_set_current(current)
#    time.sleep(.01)

    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-10e6, 10e6, 81), seq=None, plot_seqs=False, proj_func='phase')
    spec.measure()
#    plt.close()
    
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    
#    QK_freq = QK_freq + spec.center * 1e6
#    qbrick.set_frequency(QK_freq)
    
#    tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                   update=False,seq=None, proj_func='phase')
#    data=tr.measure()
#    pi_amp[i] = tr.pi_amp         
#    ge.set('pi_amp', tr.pi_amp)
#    qubit_info = mclient.get_qubit_info('qubit1ge')
#
#    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
#                                         np.concatenate((np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36), np.linspace(22e3, 550e3, 60))), 
#                                         double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
#    t1.measure()
#    
#    t1_result.append(t1.fit_params['tau'].value)
#    t1_err.append(t1.fit_params['tau'].stderr)
#    t1_ofs.append(t1.fit_params['ofs'].value)
#    t1_ofs_err.append(t1.fit_params['ofs'].stderr)
#    t1_amp.append(t1.fit_params['amplitude'].value)
#    t1_amp_err.append(t1.fit_params['amplitude'].stderr)
#    t1_amp2.append(t1.fit_params['amplitude2'].value)
#    t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
#    t1_result2.append(t1.fit_params['tau2'].value)
#    t1_err2.append(t1.fit_params['tau2'].stderr)
#    
#    T1_Ypoints.append(t1.get_ys())
#
#    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=None, postseq=None, proj_func='phase')
#    t2.measure()
#    t2_result.append(t2.fit_params['tau'].value)
#    t2_ofs.append(t2.fit_params['ofs'].value)
#    t2_err.append(t2.fit_params['tau'].stderr)
##    t2_amp.append(t2.fit_params['amplitude'].value)
#
#    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 15e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase', seq=None)
#    t2Echo_result.append(t2.fit_params['tau'].value)
#    t2Echo_err.append(t2.fit_params['tau'].stderr)
#    t2Echo_ofs.append(t2.fit_params['ofs'].value)

#   
    i=0
    
    while contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False and i<(len(sweep_pow)): 
    #Here it should be trying to optimize the RO power and frequency to get the optimal contrast
    #Normally this will be done with histogramming, I will modify this once it is implemented to Keysight Dig
    
    #setting RO power to some other
        RObrick.do_set_power(ROpower_initial + sweep_pow[i])
        print((ROpower_initial + sweep_pow[i]))
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=None, plot_seqs=False, proj_func='phase')
        spec.measure()
#        plt.close()
    
        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
        
        contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
        i = i+1

    if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
        raise Exception('Could not get good contrast')  #BUNUN SONUNDA ILK RO POWERA DONMESINI ISTEMEM MANTIKLI OLABILIR

    if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
        ROpower_initial = RObrick.do_get_power()
        
        QK_freq = QK_freq + spec.center * 1e6
        qbrick.set_frequency(QK_freq)
        
        tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                   update=False, seq=None, proj_func='phase')
        data=tr.measure()
#        pi_amps[i] = tr.pi_amp         
        ge.set('pi_amp', tr.pi_amp)
        pi_amp.append(tr.pi_amp)
        qubit_info = mclient.get_qubit_info('qubit1ge')
        dig.do_set_naverages(2500)
#        t1 = T1measurement.T1Measurement(qubit_info, np.concatenate(np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36), np.linspace(22e3, 550e3, 60)), double_exp=True, generate=True, plot_seqs=False, proj_func='phase')

        
        t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                             np.concatenate((np.linspace(0.1e3, 0.9e3, 15), np.linspace(1e3, 10e3, 31), np.linspace(11e3, 45e3, 40))), 
                                             double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
        t1.measure()
        
        t1_result.append(t1.fit_params['tau'].value)
        t1_err.append(t1.fit_params['tau'].stderr)
        t1_ofs.append(t1.fit_params['ofs'].value)
        t1_ofs_err.append(t1.fit_params['ofs'].stderr)
        t1_amp.append(t1.fit_params['amplitude'].value)
        t1_amp_err.append(t1.fit_params['amplitude'].stderr)
        t1_amp2.append(t1.fit_params['amplitude2'].value)
        t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
        t1_result2.append(t1.fit_params['tau2'].value)
        t1_err2.append(t1.fit_params['tau2'].stderr)
        T1_Ypoints.append(t1.get_ys())
        
        
#        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, generate=True, 
#                                         seq=None, extra_info=ef_info, postseq=None, proj_func='phase')
#        t2.measure()
#        t2_result.append(t2.fit_params['tau'].value)
#        t2_err.append(t2.fit_params['tau'].stderr)
#        t2_ofs.append(t2.fit_params['ofs'].value)
##        t2_amp.append(t2.fit_params['amplitude'].value)
#
#
##        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 15e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase', seq=None, extra_info=ef_info)
##        t2Echo_result.append(t2.fit_params['tau'].value)
##        t2Echo_err.append(t2.fit_params['tau'].stderr)
##        t2Echo_ofs.append(t2.fit_params['ofs'].value)
##        t2Echo_amp.append(t2.fit_params['amplitude'].value)        
        dig.do_set_naverages(2000)


        fxn_freq1D.append(QK_freq) #yoksa eksi mi?
        fxn_current.append(current)
        fxn_ROpowers.append(ROpower_initial)
        QK_freq = QK_freq + fxn_freq1D[len(fxn_freq1D)-1] - fxn_freq1D[len(fxn_freq1D) - 2] 
        qbrick.set_frequency(QK_freq)
        plt.close('all')

#        time.sleep(.01)
    
    

    #BURADAN ITIBAREN
    
    
if 0:    
    start_freq = 944500000.0
    #start_freq = 1245.31e6 #This should not be a guess but some frequency previously confirmed to be the correct qubit freq at the given flux point.
    #stop_freq = 5000e6
    #
    start_current = 2.0831e-3
    #start_current = 1.99e-3  #This is the flux point in question for the frequency above
    stop_current = 1.95e-3
    current_step= -0.01e-3
    yoko.do_set_current(start_current)
    qbrick.set_frequency(start_freq)
    
    
    
    QK_freq = start_freq
    current = start_current
    ROpower_initial = 10
    sweep_pow = [-2, 2, -4, 4, -6, 6] #bunu linspace tarzi bir seye donusturmek gerekebilir
    
    seq = sequencer.Trigger(600)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-5e6, 50e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
    spec.measure()
    plt.close()
        
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    
    QK_freq = QK_freq + spec.center * 1e6
    qbrick.set_frequency(QK_freq)
    
    tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=False, proj_func='phase', seq=None)
    data=tr.measure()      
    ge.set('pi_amp', tr.pi_amp)
    pi_amp.append(tr.pi_amp)
    qubit_info = mclient.get_qubit_info('qubit1ge')
    
    dig.do_set_naverages(2500)
    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                         np.concatenate((np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36), np.linspace(22e3, 550e3, 60))), 
                                         double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
    t1.measure()        
    t1_result.append(t1.fit_params['tau'].value)
    t1_err.append(t1.fit_params['tau'].stderr)
    t1_ofs.append(t1.fit_params['ofs'].value)
    t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    t1_amp.append(t1.fit_params['amplitude'].value)
    t1_amp_err.append(t1.fit_params['amplitude'].stderr)
    t1_amp2.append(t1.fit_params['amplitude2'].value)
    t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
    t1_result2.append(t1.fit_params['tau2'].value)
    t1_err2.append(t1.fit_params['tau2'].stderr)
            
    T1_Ypoints.append(t1.get_ys())
    
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, generate=True, 
                                             seq=None, postseq=None, proj_func='phase')
    t2.measure()
    t2_result.append(t2.fit_params['tau'].value)
    t2_err.append(t2.fit_params['tau'].stderr)
    t2_ofs.append(t2.fit_params['ofs'].value)
    #t2_amp.append(t2.fit_params['amplitude'].value)
    
    
    #t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 30e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase', seq=None, extra_info=ef_info)
    #t2.measure()
    #t2Echo_result.append(t2.fit_params['tau'].value)
    #t2Echo_err.append(t2.fit_params['tau'].stderr)
    #t2Echo_ofs.append(t2.fit_params['ofs'].value)
    #t2Echo_amp.append(t2.fit_params['amplitude'].value) 
    #This code strictly assumes that the first run is an accurate guess.
    dig.do_set_naverages(800)
    #phase=np.asarray(YS[:])
    #phase=phase[:,None].T
    fxn_freq1D.append(QK_freq)
    #fxn_freq = np.asarray(XS + QK_freq)
    #fxn_freq=fxn_freq[:,None].T
    fxn_current.append(current)
    fxn_ROpowers.append(ROpower_initial)
    
    #QK_freq = QK_freq + spec.center * 1e6
    #qbrick.set_frequency(QK_freq)
    #time.sleep(.01)   
    
    while QK_freq < stop_freq and current > stop_current:
    #    if current == 2e-3:
    #        dig.do_set_naverages = 2000
        current = current + current_step
        yoko.do_set_current(current)
    #    time.sleep(.01)
    
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-5e6, 50e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
        spec.measure()
    #    plt.close()
        
        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
    ##    
    ##    tr = rabi.Rabi(qubit_info, np.linspace(-0.5, 0.5, 100), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
    ##                   update=False, proj_func='phase')
    ##    data=tr.measure()
    ##    pi_amps[i] = tr.pi_amp         
    ##    ge.set('pi_amp', tr.pi_amp)
    ##    qubit_info = mclient.get_qubit_info('qubit1ge')
    ##
    ##    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 120e3, 101), double_exp=False, generate=True, plot_seqs=False, proj_func='phase')
    ##    t1.measure()
    ##    t1_result.append(t1.fit_params['tau'].value)
    ##    t1_err.append(t1.fit_params['tau'].stderr)
    ##    t1_ofs.append(t1.fit_params['ofs'].value)
    ##    t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    ##    t1_amp.append(t1.fit_params['amplitude'].value)
    ##    t1_amp_err.append(t1.fit_params['amplitude'].stderr)
    ##
    ##
    ##    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 4e3, 251), detune=5e6, double_freq=False, generate=True, proj_func='phase')
    ##    t2.measure()
    ##    t2_result.append(t2.fit_params['tau'].value)
    ##    t2_ofs.append(t2.fit_params['ofs'].value)
    ##    t2_amp.append(t2.fit_params['amplitude'].value)
    ##   
    ##    i=0
    #    
        while contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False and i<(len(sweep_pow)): 
        #Here it should be trying to optimize the RO power and frequency to get the optimal contrast
        #Normally this will be done with histogramming, I will modify this once it is implemented to Keysight Dig
        
        #setting RO power to some other
            RObrick.do_set_power(ROpower_initial + sweep_pow[i])
            print((ROpower_initial + sweep_pow[i]))
            seq = sequencer.Trigger(600)
            spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, np.linspace(-15e6, 15e6, 141), seq=seq, plot_seqs=False, proj_func='phase')
            spec.measure()
    #        plt.close()
        
            XS = spec.xs
            YS = spec.get_ys()
            width = spec.width()
            height = spec.height
            center = spec.center
            
            contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None)
            i = i+1
    
        if contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == False:
            raise Exception('Could not get good contrast')  #BUNUN SONUNDA ILK RO POWERA DONMESINI ISTEMEM MANTIKLI OLABILIR
    
        if  contrast_check.Contrast_check(XS, YS, height, width, flat_portion = None) == True:
            QK_freq = QK_freq + spec.center * 1e6
            qbrick.set_frequency(QK_freq)
            ROpower_initial = RObrick.do_get_power()
            
            tr = rabi.Rabi(qubit_info, np.linspace(-0.6, 0.6, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=False, proj_func='phase')
            data=tr.measure()
    #        pi_amps[i] = tr.pi_amp         
            ge.set('pi_amp', tr.pi_amp)
            pi_amp.append(tr.pi_amp)
            qubit_info = mclient.get_qubit_info('qubit1ge')
            dig.do_set_naverages(2500)
            t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                                 np.concatenate((np.linspace(0.1e3, 1.9e3, 19), np.linspace(2e3, 20e3, 36), np.linspace(22e3, 550e3, 60))), 
                                                 double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None)
            t1.measure()        
            t1_result.append(t1.fit_params['tau'].value)
            t1_err.append(t1.fit_params['tau'].stderr)
            t1_ofs.append(t1.fit_params['ofs'].value)
            t1_ofs_err.append(t1.fit_params['ofs'].stderr)
            t1_amp.append(t1.fit_params['amplitude'].value)
            t1_amp_err.append(t1.fit_params['amplitude'].stderr)
            t1_amp2.append(t1.fit_params['amplitude2'].value)
            t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
            t1_result2.append(t1.fit_params['tau2'].value)
            t1_err2.append(t1.fit_params['tau2'].stderr)
    
    
            t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, generate=True, proj_func='phase')
            t2.measure()
            t2_result.append(t2.fit_params['tau'].value)
            t2_err.append(t2.fit_params['tau'].stderr)
            t2_ofs.append(t2.fit_params['ofs'].value)
    #        t2_amp.append(t2.fit_params['amplitude'].value)
            
            
    #        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 15e3, 101), detune=0.3e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True, proj_func='phase')
    #        t2.measure()
    #        t2Echo_result.append(t2.fit_params['tau'].value)
    #        t2Echo_err.append(t2.fit_params['tau'].stderr)
    #        t2Echo_ofs.append(t2.fit_params['ofs'].value)
    #        t2Echo_amp.append(t2.fit_params['amplitude'].value) 
            dig.do_set_naverages(800)
    #        
    ##        phasenew=np.asarray(YS[:])
    ##        phasenew=phasenew[:,None].T
    ##        phase= np.concatenate([phase,phasenew])
    ##        fxn_freqnew = np.asarray(XS + QK_freq)
    ##        fxn_freqnew=fxn_freqnew[:,None].T
    ##        fxn_freq= np.concatenate([fxn_freq,fxn_freqnew])
    #
    #        fxn_freq1D.append(QK_freq) #yoksa eksi mi?
    #        fxn_current.append(current)
    #        fxn_ROpowers.append(ROpower_initial)
    #        QK_freq = QK_freq + fxn_freq1D[len(fxn_freq1D)-1] - fxn_freq1D[len(fxn_freq1D) - 2]
    #        qbrick.set_frequency(QK_freq)
    #        plt.close('all')
    ##        time.sleep(.01)
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
    
    
    
    
    
        
    plt.figure()

#plt.plot(ramp_currents, fxn_freq)
#    results.append(spec.ampdata[0,:])
##    results.append(spec.get_ys())
#    min_result.append(np.min(spec.ampdata[0,:]))
#    plt.close()


#X, Y = np.meshgrid(fxn_current, XS)
#Y =np.transpose(fxn_freq)
#X=X*1000
#Y=Y/float(1E9)
#Z = np.transpose(phase)





plt.plot(fxn_current, fxn_freq1D)           #I don't know why I insisted on having a color plot, it's not really necessary if I am just following one transition. I can add height as a 3rd parameter later. 
##plt.pcolormesh(X, Y, Z)
#plt.colorbar()
#plt.xlabel('Coil Current (mA)')
#plt.ylabel('Frequency (GHZ)')
#plt.show()
#to_save = [X, Y, Z]
#
#    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    
    
    











    
    