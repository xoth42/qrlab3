# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 20:24:09 2019

@author: Wang_Lab
"""
import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
import time
import objectsharer as objsh
from pulseseq import sequencer, pulselib
import os

qubit_info = mclient.get_qubit_info('qubit1ge')
qubit2_info = mclient.get_qubit_info('qubit2ge')
Magnet = mclient.instruments['Magnet']
readout_info = mclient.get_readout_info('readout')

fieldlist = np.linspace(-0.07,-0.07,5)

freadout = []

rabiamp1 = []
rabiamp2 = []
rabiamp3 = []
freq1 = []
freq2 = []

rabiamp1_err = []
rabiamp2_err = []
rabiamp3_err = []
freq1_err = []
freq2_err = []

for field in fieldlist:
    
    if float(Magnet.do_get_PSwitch()) == 1:
    
        Magnet.do_set_field(field)
    #    time.sleep(10)
        try:
            while not abs(float(Magnet.do_get_field()) - field) < 0.0005:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in ramping field'
        
        Magnet.do_set_PSwitch(0)    
        time.sleep(300)
        try:
            while not float(Magnet.do_get_PSwitch()) == 0:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in setting persistent mode'
        
    elif abs(float(Magnet.do_get_field()) - field) > 0.00005:
        print 'heat PSwitch first'
        exit
        
    
        
    field0 = Magnet.do_get_field()
    print 'field at %sT'%(float(field0))    
    from single_cavity import rocavspectroscopy_keysight
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    rofreq = 10.935e9
    freq_range = 2.5e6
    dig.set_naverages(10000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
    ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-5, 10, 1),
                                             np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                             qubit_pulse=False, seq=None)
    ro.measure()
    pl.close()
    max_freq = ro.fit_params[2]
    print max_freq
    readout_info.rfsource1.set_frequency(ro.fit_params[2])
    readout_info.rfsource2.set_frequency(ro.fit_params[2]+50e6)   

    freadout.append(max_freq)
    

    

    from single_qubit import rabi
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    dig.set_naverages(30000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
    tr = rabi.Rabi(qubit_info, 
        #                       np.linspace(-0.2, -0.20, 81), selective=False,
                               np.linspace(-0.6, 0.6, 81), selective=False,
        #                       np.linspace(-0.26, -0.18, 101), selective=False,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                               update=True, #extra_info=ef_info,
                               proj_func='phase')
    tr.measure_keysight()
    pl.title('S31 with qubit1 field = %s'%(float(field0)))
    rabiamp1.append(tr.fit_params['amp'].value)
    rabiamp1_err.append(tr.fit_params['amp'].stderr)
    pl.close()
    
    dig.set_naverages(80000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
    tr = rabi.Rabi(qubit2_info, 
        #                       np.linspace(-0.2, -0.20, 81), selective=False,
                               np.linspace(-0.7, 0.7, 81), selective=False,
        #                       np.linspace(-0.26, -0.18, 101), selective=False,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                               update=True, fix_period = qubit2ge.get_pi_amp()*2, #extra_info=ef_info,
                               proj_func='phase')
    tr.measure_keysight()
    pl.title('S31 with qubit2 field = %s'%(float(field0)))    
    rabiamp2.append(tr.fit_params['amp'].value)
    rabiamp2_err.append(tr.fit_params['amp'].stderr)
    pl.close()
    
    
    dig.set_naverages(30000)
#    SC_qubit.set_rf_on(False)
#    qubitbrick.set_rf_on(True)
    tr = rabi.Rabi(qubit_info, 
        #                       np.linspace(-0.2, -0.20, 81), selective=False,
                               np.linspace(-0.6, 0.6, 81), selective=False,
        #                       np.linspace(-0.26, -0.18, 101), selective=False,
        #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                               plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                               update=True, #extra_info=ef_info,
                               proj_func='phase')
    tr.measure_keysight()
    pl.title('S31 with qubit1 field = %s'%(float(field0)))
    rabiamp3.append(tr.fit_params['amp'].value)
    rabiamp3_err.append(tr.fit_params['amp'].stderr)
    pl.close()
    
    
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
#    
    from single_qubit import T2measurement
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 2e3, 101), detune=4e6, double_freq=False, generate=True, 
                                         seq=None, postseq=None, proj_func='phase', extra_info=[qubit2_info])
        t2.measure_keysight()
    freq1.append(t2.fit_params['freq'].value*10**6) 
    freq1_err.append(t2.fit_params['freq'].stderr*10**6) 
    pl.close()
    
    
    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 2e3, 101), detune=4e6, double_freq=False, generate=True, 
                                         seq=seq, postseq=None, proj_func='phase', extra_info=[qubit2_info])
        t2.measure_keysight()
    freq2.append(t2.fit_params['freq'].value*10**6) 
    freq2_err.append(t2.fit_params['freq'].stderr*10**6) 
    pl.close()
    
    if not field == fieldlist[-1]:
        Magnet.do_set_PSwitch(1)
        time.sleep(30)
        
        try:
            while not float(Magnet.do_get_PSwitch()) == 1:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in getting out of persistent mode'

pl.figure()
pl.plot(fieldlist, np.asarray(freadout)/1e6, label = 'readout freq(MHz)')
pl.legend()
pl.show()

pl.figure()
pl.errorbar(fieldlist, - np.asarray(rabiamp1), yerr = rabiamp1_err, label = 'qubit 1')
pl.errorbar(fieldlist, - np.asarray(rabiamp3), yerr = rabiamp3_err, label = 'qubit 1')
pl.errorbar(fieldlist, - np.asarray(rabiamp2), yerr = rabiamp2_err, label = 'qubit 2')
pl.legend()
pl.show()

pl.figure()
pl.plot(fieldlist, np.asarray(rabiamp2)/(np.asarray(rabiamp1) + np.asarray(rabiamp3)), label = 'qubit 2 / qubit 1')
pl.legend()
pl.show()

pl.figure()
pl.errorbar(fieldlist, freq1, yerr = freq1_err, label = 'without qubit 2 pi pulse')
pl.errorbar(fieldlist, freq2, yerr = freq2_err, label = 'with qubit 2 pi pulse')
pl.legend()
pl.show()

save_filepath = 'C:/Users/Wang_Lab/Documents/yingying/08272019cooldown/20190921/'



if not os.path.exists(save_filepath):
    os.makedirs(save_filepath)
    
np.savetxt(save_filepath + 'results0928_-40mT.txt',
           np.column_stack((fieldlist,freadout,rabiamp1,rabiamp2,rabiamp3,freq1,freq2,rabiamp1_err,rabiamp2_err,rabiamp3_err,freq1_err,freq2_err,)),
           header ='field,freadout,rabiamp1,rabiamp2,rabiamp3,freq1,freq2,rabiamp1_err,rabiamp2_err,rabiamp3_err,freq1_err,freq2_err')


