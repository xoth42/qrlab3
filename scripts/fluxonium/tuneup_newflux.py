# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 11:49:11 2020

@author: wanglab
"""


import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib.pyplot as plt
import os
os.chdir(r'c:\qrlab')

alz = mclient.instruments['alazar']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
qubit2_info = mclient.get_qubit_info('qubit2ge')
qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')

   
from scripts.single_qubit import ssbspec
from scripts.single_qubit import rabi
from scripts.single_qubit import ssbspec_gaussianfit
from scripts.fluxonium import cooling_tune_brickonoff
from scripts.single_qubit import T2measurement
from scripts.single_qubit import T1measurement
from scripts.single_qubit import drag_test
gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
#zx90_info = mclient.get_gate_info('zx90_gate')
cx_info = mclient.get_gate_info('cx_gate')
cancel_info = mclient.get_gate_info('cancel_gate')



cool = sequencer.Constant(int(4e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

cavity= RObrick.do_get_frequency()
RO_power=5
gaius_freq = gaius01.do_get_frequency()

def ssb_check(qubitge, qubitge_2, qubit_info, range):  #single gaussian fit
    spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info,range, proj_func='phase', seq=seq_cool, extra_info=qubit2_info)
    spec.measure()
    qubitfreq = qubitge.get_deltaf()
    qubitfreq_new = qubitfreq + spec.fit_params['freq'].value
    qubitge.set_deltaf(qubitfreq_new)  #I remember some sort of hierarchy between qubit1ge info and the instrument, double check this 
    qubitge_2.set_deltaf(qubitfreq_new)  #I remember some sort of hierarchy between qubit1ge info and the instrument, double check this 

    return qubitfreq_new



def cooling_spec(cool_freq, freq_range, qubit_info, power_list):
    cool = cooling_tune_brickonoff.Cooling_tune_brickonoff(mclient.instruments['cool'], mclient.instruments['gaius01'], 
                                                           qubit2_info, np.linspace(cool_freq-freq_range, cool_freq+freq_range,31),
                                     power_list, '3m1', seq=None, plot_seqs=False) #1=1ns for plen
    cool.measure()


def ssb(qubit_info, seq, extra_info): #can do single or double fits depending on selection 
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-3e6, 8e6, 61), proj_func='phase', seq=seq, extra_info=extra_info)
    spec.measure()
    center=spec.fit_params['center1'].value
    return center

def ssb_ZZ(qubit_info, ZZ_info, plen, seq, extra_info): #can do single or double fits depending on selection 
    spec = ssb_ZZenhance.SSBSpec(qubit_info, ZZ_info, np.linspace(-15e6, 15e6, 61), plen, sigma=6, proj_func='phase', seq=seq, extra_info=extra_info)
    spec.measure()
    center=spec.fit_params['center1'].value
    return center

#
def ZZ_tune(qubit_info, power_range, freq_range, extra_info = qubit2_info):
    
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
    ZZ.set_rf_on(True)
    for power in power_range:
       ZZ.do_set_power(power)
       L_nopi = []
       L_pi = []     

       for freq in freq_range:
           ZZ.do_set_frequency(freq)           
           L_nopi.append(ssb(qubit_info, seq_cool, extra_info=None))
           L_pi.append(ssb(qubit_info, seq, extra_info = qubit2_info))



       plt.figure()
       plt.plot(freq_range,L_nopi)
       plt.plot(freq_range,L_pi)
#

def rabi_test(qubitge, qubit_info, seq, range):
    tr = rabi.Rabi(qubit_info, range, selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq, postseq=None, proj_func='phase')
    data=tr.measure()
    qubitge.set_pi_amp_selective(qubitge.get_pi_amp()*qubitge.get_w()/qubitge.get_w_selective())  



def T2R(qubit_info,seq=None): 
    postseq =  gate_info2.rotate(np.pi,0)
    
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 1e3, 81), detune=2e6, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq, postseq=None, extra_info = gate_info2)
    t2.measure()

def T2E(qubit_info,seq=None): 
    
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    
def T1(qubit_info, seq):
    postseq =  gate_info2.rotate(np.pi,0)

    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 50e3, 81), double_exp=False, generate=True, plot_seqs=False,
                                         proj_func='phase', seq=seq, postseq=postseq, extra_info=gate_info2)  #Note the rep time is 50us
    t1.measure()



def Drag_test(qubit_info):   
    dtest = drag_test.drag_test(qubit_info, np.linspace(-0.5,1, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
#    
#We start with a different flux point. 
#Based on the spectroscopy, we assume that we have an idea about where the qubit frequencies should be 
#We also assume that we have a good guess of what the selective pi amp should be  (w_selective suggestion = 200)
#


if 0:
    ZZ.set_rf_on(False)
    coolgen.set_rf_on(False)
    alz.set_naverages(2500)
    qubitnew1 = ssb_check(qubit1ge, qubit1ge_2, qubit_info,  np.linspace(-10e6, 10e6, 61))
#    alz.set_naverages(100000)
##
#    qubitnew2 = ssb_check(qubit2ge, qubit2ge_2, qubit2_info,  np.linspace(-10e6, 10e6, 61))
    qubits = mclient.get_qubits()
    qubit_info = mclient.get_qubit_info('qubit1ge')
    qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
    qubit2_info = mclient.get_qubit_info('qubit2ge')
    qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')
    #This should confirm that we are in the good region.
    
#    Getting some cooling prediction
#    alz.set_naverages(2500)
#    cool_freq = (cavity - gaius_freq - qubitnew2)/2
#    coolgen.set_rf_on(True)
#    freq_range = 15e6        
#    cooling_spec(3420e6, 15e6, qubit2_info, [11,12,13])
##    
    bla

#    
#coolgen.set_frequency(3425.7e6)
#coolgen.set_power(9)


if 0:
   ##Optimizing ZZ 

#    rabi_test(qubit1ge, qubit_info, seq_cool,np.linspace(-0.15, 0.3, 61) )   
#    rabi_test(qubit2ge, qubit2_info, seq_cool,np.linspace(-0.3, 0.3, 61))   

    ZZ.set_rf_on(True)
    alz.set_naverages(2000)
    power_range = np.linspace(10,10, 1)
    freq_range = np.linspace(3528.5e6, 3529.5e6, 7)
    ZZ_tune(qubit_info, power_range, freq_range, extra_info = qubit2_info)
    bla    

#ZZ.set_frequency()
#ZZ.set_power()


if 0:
#    Rabi checking pi amps from 5/6 for both qubits
    rabi_test(qubit1ge, qubit_info, seq_cool,np.linspace(-0.15, 0.15, 61))   
    rabi_test(qubit2ge, qubit2_info, seq_cool,np.linspace(-0.2, 0.2, 61))   
            
    
    #SSB to update sidenband frequencies (measures through 5/6, updates both qubit_info delta's)

    qubitnew1 = ssb_check(qubit1ge, qubit1ge_2, qubit_info, np.linspace(-6e6, 6e6, 81))
    qubitnew2 = ssb_check(qubit2ge, qubit2ge_2, qubit2_info, np.linspace(-6e6, 6e6, 81))
    qubits = mclient.get_qubits()
    qubit_info = mclient.get_qubit_info('qubit1ge')
    qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
    qubit2_info = mclient.get_qubit_info('qubit2ge')
    qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')
#    
#    #Running cooling spec one more time
    cool_freq = (cavity - gaius_freq - qubitnew2)/2
    freq_range = 35e6        
    cooling_spec(3420e6, 15e6, qubit2_info, [12,13])
    bla
    #manually set the frequency and power
#coolgen.set_power()
#coolgen.set_frequency()
#coolgen.set_rf_on(True)
#    
    

if 1:
    #Update all 4 pi amp's
#    rabi_test(qubit1ge, qubit_info, seq_cool, np.linspace(-0.15, 0.15, 61))   
#    rabi_test(qubit2ge, qubit2_info, seq_cool, np.linspace(-0.2, 0.2, 61))   
#    rabi_test(qubit1ge_2, qubit_info2, seq_cool, np.linspace(-0.5, 0.5, 61))   
#    rabi_test(qubit2ge_2, qubit2_info2, seq_cool, np.linspace(-0.5, 0.5, 61))   
#    
    T2R(gate_info1, seq=seq_cool)
    T2R(gate_info2, seq=seq_cool)
        
#    T2E(qubit_info, seq=seq_cool)
#    T2E(qubit2_info, seq=seq_cool)
#    #        
##    #Measure T1     
#    T1(gate_info1, seq=seq_cool)
#    T1(qubit2_info, seq=seq_cool)
##    
##    #T2E with ZZ off    
#    ZZ.set_rf_on(False)
#    T2E(qubit_info,seq=seq_cool)
#    T2E(qubit2_info,seq=seq_cool)
#    ZZ.set_rf_on(True)
##    
#    #T2E with ZZ off and cooling off    
#    ZZ.set_rf_on(False)
#    coolgen.set_rf_on(False)
#    T2E(qubit_info, seq=None)
#    T2E(qubit2_info, seq=None)
#    ZZ.set_rf_on(True)
#    coolgen.set_rf_on(True)
##        
#    #Drag test - NEEDS TO BE UPDATED MANUALLY
#    Drag_test(qubit_info)
#    Drag_test(qubit2_info)  
#
    
if 0: # Tune up for time vs detuning   
    
    from scripts.fluxonium import CRtuning_timevsdet
    
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])     
    cr_tune = CRtuning_timevsdet.CRtuning_timevsdet(qubit_info2, qubit_info, qubit2_info, 
                                                    np.linspace(0,100,21), np.linspace(-10e6, 30e6, 21), 
                amp=0.36, phase=0, rel_amp=0.0000, rel_phase=0.0, sigma=4, update=False, 
                seq=seq_cool, fix_phase=True, fix_period=None, control_pi=False, proj_func='phase')    
    
    data = cr_tune.measure()
    bla
