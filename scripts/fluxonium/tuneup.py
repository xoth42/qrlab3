
import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib.pyplot as plt
import os
os.chdir(r'c:\qrlab-3')

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

cool = sequencer.Constant(int(8e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

#change the qubit_info namings to target and control
#double gaussian fitting for the ssb spec at the beginning, it should be functional at a different flux point frequency
#zz tune up needs double fitting again, make 

from scripts.single_qubit import ssbspec_gaussianfit

# Qubit SSBspec  #ZZ is on
def ssb_check(qubitge):

    spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-6e6, 6e6, 81), proj_func='phase', seq=seq_cool, extra_info=qubit2_info)
    spec.measure()
    qubitfreq = qubitge.get_deltaf()
    qubitfreq_new = qubitfreq + spec.fit_params['freq'].value
    qubitge.set_deltaf(qubitfreq_new)  #I remember some sort of hierarchy between qubit1ge info and the instrument, double check this 

#    spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-6e6, 6e6, 81), proj_func='phase', seq=seq_cool, extra_info=qubit2_info)
#    spec2.measure()
#    qubit2freq = qubit2ge.get_deltaf()
#    qubit2freq_new = qubit2freq + spec.fit_params['freq'].value    
#    qubit2ge.set_deltaf(qubit2freq_new) 
    
    return qubitfreq_new


if 0: #Rabi checking pi amps from 5/6 for both qubits
    tr1 = rabi.Rabi(qubit_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr1.measure()
    qubit1ge.set_pi_amp_selective(qubit1ge.get_pi_amp()*qubit1ge.get_w()/400)  #assuming the selective w=400
    
    tr2 = rabi.Rabi(qubit2_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr2.measure()    
    qubit2ge.set_pi_amp_selective(qubit2ge.get_pi_amp()*qubit2ge.get_w()/400)  #assuming the selective w=400



if 0: #Cooling spec
    
    #Import the script
    cool_freq = 3.420e9
    freq_range = 15e6

    cool = cooling_tune_brickonoff.Cooling_tune_brickonoff(mclient.instruments['cool'], mclient.instruments['gaius01'], 
                                                           qubit2_info, np.linspace(cool_freq-freq_range, cool_freq+freq_range, 31),
                                     [7,8,9], '3m1', seq=None, plot_seqs=False) #1=1ns for plen
    cool.measure()
    
if  0:  #Trying the cooling for a new frequency power combination 
    coolgen.set_frequency(3425700000.0)
    coolgen.set_power(9)     
    ZZ.set_rf_on(False)
    spec2 = ssbspec.SSBSpec(qubit_info, np.linspace(-3e6, 3e6, 81), proj_func='phase', seq=seq_cool)
    spec2.measure()
    spec2 = ssbspec.SSBSpec(qubit2_info, np.linspace(-3e6, 3e6, 81), proj_func='phase', seq=seq_cool)
    spec2.measure()   
    ZZ.set_rf_on(True)

#A proper ZZ tune up script here

if 0: #Check ZZ -- SSB for upper qubit with ZZ for lower qubit in g vs e
    spec1 = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq_cool)
    spec1.measure()
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), qubit2_info.rotate(np.pi,0)])
    spec1 = ssbspec.SSBSpec(qubit_info, np.linspace(-4e6, 4e6, 81), proj_func='phase', seq=seq, extra_info=qubit2_info)
    spec1.measure()    
    

if 0: # Qubit SSBspec
    from scripts.single_qubit import ssbspec_gaussianfit
    spec = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit_info, np.linspace(-6e6, 6e6, 81), proj_func='phase', seq=seq_cool, extra_info=qubit2_info)
    spec.measure()
    qubitfreq = qubit1ge.get_deltaf()
    qubit1ge.set_deltaf(qubitfreq + spec.fit_params['freq'].value)  #I remember some sort of hierarchy between qubit1ge info and the instrument, double check this 

    spec2 = ssbspec_gaussianfit.SSBSpec_Gaussianfit(qubit2_info, np.linspace(-6e6, 6e6, 81), proj_func='phase', seq=seq_cool, extra_info=qubit2_info)
    spec2.measure()
    qubit2freq = qubit2ge.get_deltaf()
    qubit2ge.set_deltaf(qubit2freq + spec2.fit_params['freq'].value) 


# One more cooling optimization here


    
if 0: #Rabi checking pi amps for upper qubit from both input lines
    tr1 = rabi.Rabi(qubit_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr1.measure()
    tr1 = rabi.Rabi(qubit_info2, np.linspace(-0.4, 0.4, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr1.measure()
    
if 0: #Rabi checking pi amps for lower qubit from both input lines
    tr2 = rabi.Rabi(qubit2_info, np.linspace(-0.2, 0.2, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr2.measure()    
    tr2 = rabi.Rabi(qubit2_info2, np.linspace(-0.4, 0.4, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1,
                                   update=True, seq=seq_cool, postseq=None, proj_func='phase')
    data=tr2.measure()  

if 0: #Check coherence  T2Echo
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    
if 0: #Check coherence  T2
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, plot_seqs = False, generate=True, proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, plot_seqs = False, generate=True, proj_func='phase', seq=seq_cool)
    t2.measure()
    

if 0: #Check coherence  T1
    from scripts.single_qubit import T1measurement

    t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 25e3, 81), double_exp=False, generate=True, plot_seqs=False,
                                         proj_func='phase', seq=seq_cool)
    t1.measure()
    t1 = T1measurement.T1Measurement(qubit2_info, np.linspace(0, 25e3, 81), double_exp=False, generate=True, plot_seqs=False,
                                         proj_func='phase', seq=seq_cool)
    t1.measure()


if 0: #Check coherence  T2Echo with no ZZ
    
    from scripts.single_qubit import T2measurement
    ZZ.set_rf_on(False)

    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()

    ZZ.set_rf_on(True)


if 0: #Check coherence  T2Echo with no ZZ
    
    from scripts.single_qubit import T2measurement
    ZZ.set_rf_on(False)

    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()

    ZZ.set_rf_on(True)


if 0: #Check coherence  T2Echo with no ZZ and no cooling
    
    from scripts.single_qubit import T2measurement
    ZZ.set_rf_on(False)
    coolgen.set_rf_on(False)
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(qubit2_info, np.linspace(10, 4e3, 81), detune=2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()

    ZZ.set_rf_on(True)
    coolgen.set_rf_on(True)


if 0: # Drag test
    #UPdate the value at the end of the measurement
    from scripts.single_qubit import drag_test
    dtest = drag_test.drag_test(qubit_info, np.linspace(-2,2, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()

    dtest = drag_test.drag_test(qubit2_info, np.linspace(-2,2, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
    

