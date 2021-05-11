import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
matplotlib.rcParams['backend'] = 'Qt4Agg'
matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt

import math as math
import time
from matplotlib import gridspec
import lmfit


import os
os.chdir(r'c:\qrlab')

def gaussian(params, x, data):
    return data - params['amp'] * np.exp(-.5 * ((x - params['mean']) / params['std'])**2)

def gaussian_sum(params, x, data):
    g1 = params['amp1'] * np.exp(-.5 * ((x - params['mean1']) / params['std1'])**2)
    g2 = params['amp2'] * np.exp(-.5 * ((x - params['mean2']) / params['std2'])**2)
    return data - (g1 + g2)

def meas_error_model(params, x1, x2, data):
    C_g = params['A_gg'] * np.exp(-.5 * ((x1 - params['mean_g']) / params['std_g'])**2) + params['A_eg'] * np.exp(-.5 * ((x1 - params['mean_e']) / params['std_e'])**2) 
    C_e = params['A_ee'] * np.exp(-.5 * ((x2 - params['mean_e']) / params['std_e'])**2) + params['A_ge'] * np.exp(-.5 * ((x2 - params['mean_g']) / params['std_g'])**2) 
    return data - (C_g + C_e)



qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
qubit2_info = mclient.get_qubit_info('qubit2ge')
ef_info = mclient.get_qubit_info('qubit1ef')
dig = mclient.instruments['dig']



#Find read-out cavity and choose a power

if 1: # RO Cavity spec
    from scripts.single_cavity import rocavspectroscopy_keysight
    rofreq = 6530e6
    freq_range = 15e6
    for pulse in [False, True]:
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-15, -15, 1),
                                             np.linspace(rofreq - freq_range, rofreq + freq_range, 101), qubit_pulse=pulse)
        ro.measure()

    bla
    
if 0: # Qubit spec
    from scripts.single_qubit import spectroscopy_keysight
    qubit_freq = 7500e6
    freq_range = 2500e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['Qbrick'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 151),
                                     [-15],
                                     plen=20000, amp=0.000001, plot_seqs=False,
                                     freq_delay=.1) #1=1ns for plen

    spec.measure()
    bla

"""Qubit SSBspec"""
if 0: # Qubit SSBspec
    from scripts.single_qubit import ssbspec
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-10e6, 10e6, 101), plot_seqs=False, proj_func='amplitude')
    spec.measure_keysight()
    bla

if 0: # Power Rabi
    for i in range(1):
        from scripts.single_qubit import rabi
        tr = rabi.Rabi(qubit_info, np.linspace(-0.5, 0.5, 101), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=True, proj_func='amplitude')

        tr.measure_keysight()     
    bla
    
if 0: # T1
    from scripts.single_qubit import T1measurement
    for i in range(1):
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 10e3, 101), double_exp=False, generate=True, plot_seqs=False, proj_func='amplitude')
        t1.measure_keysight()
    bla
    
if 0: # T2
    from scripts.single_qubit import T2measurement
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 4e3, 101), detune=1e6, double_freq=False, generate=True, proj_func='amplitude')
        t2.measure_keysight()
    bla
    
if 0: # T2echo
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(100, 4e3, 101), detune=1e6, echotype = T2measurement.ECHO_HAHN, necho=3, plot_seqs = False, generate=True,
                                     proj_func='amplitude')
    t2.measure_keysight()
    bla
    
if 0: # EF SSBspec
    from scripts.single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-2.5e6, 2.5e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='amplitude')
    spec.measure_keysight()
    bla

if 1: # EF rabi 
    from scripts.single_qubit import efrabi
    dig.set_naverages(5000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.4, 0.4, 101), plot_seqs=False, selective=False, generate=True, update=True, proj_func='amplitude')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(10000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.4, 0.4, 101), first_pi=False, selective=False, force_period=period, generate=True, proj_func='amplitude')
    efr.measure_keysight()
    dig.set_naverages(5000)
    bla
    
if 1: # T1, T2 vs. flux
    #define instruments
    RObrick = mclient.instruments['RObrick']
    refbrick = mclient.instruments['refbrick']
    Qbrick = mclient.instruments['Qbrick']
    yoko = mclient.instruments['yoko']
    
    currents = np.linspace(1, -1, 51) # units: mA
    rofreqs = np.zeros_like(currents)
    qfreqs = np.zeros_like(currents)
    t1times = np.zeros_like(currents)
    t2times = np.zeros_like(currents)
    t2etimes = np.zeros_like(currents)
    
    rospec_centerfreq = 6530e6
    ro_freq_range = 15e6
    
    qubitspec_centerfreq = 8500e6
    qubit_freq_range = 500e6
    
    from scripts.single_cavity import rocavspectroscopy_keysight
    from scripts.single_qubit import spectroscopy_keysight
    from scripts.single_qubit import rabi
    from scripts.single_qubit import T1measurement
    from scripts.single_qubit import T2measurement
    for i in range(len(currents)):
        yoko.set_current(currents[i])
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-15, -15, 1),
                                             np.linspace(rospec_centerfreq - ro_freq_range, rospec_centerfreq + ro_freq_range, 101), qubit_pulse=False)
        ro.measure()
        
        #Set RO and ref frequencies
        new_rofreq = ro.analyze()[0]
        rofreqs[i] = new_rofreq
        RObrick.set_frequency(new_rofreq)
        refbrick.set_frequency(new_rofreq+50e6)
    
        spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['Qbrick'], qubit_info,
                                     np.linspace(qubitspec_centerfreq-qubit_freq_range,
                                                 qubitspec_centerfreq+qubit_freq_range, 2001),
                                     [-15],
                                     plen=80000, amp=0.000001, plot_seqs=False,
                                     freq_delay=.1)
        spec.measure()
        qfreq = np.linspace(qubitspec_centerfreq-qubit_freq_range,
                                                 qubitspec_centerfreq+qubit_freq_range, 2001)[np.argmin(spec.ampdata[0,:])]
        qfreqs[i] = qfreq
        Qbrick.set_frequency(qfreq+100e6)

        tr = rabi.Rabi(qubit_info, np.linspace(-0.5, 0.5, 101), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=True, proj_func='amplitude')     
        data=tr.measure_keysight()               
        
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 10e3, 101), double_exp=False, generate=True, plot_seqs=False, proj_func='amplitude')
        t1.measure_keysight()
        t1times[i] = t1.analyze()
        
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 4e3, 101), detune=1e6, double_freq=False, generate=True, proj_func='amplitude')
        t2.measure_keysight()
        t2times[i] = t2.analyze()
        
        t2e = T2measurement.T2Measurement(qubit_info, np.linspace(100, 4e3, 61), detune=1e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='amplitude')
        t2e.measure_keysight()
        t2etimes[i] = t2e.analyze()
        
        plt.close('all')
        
    plt.plot(currents, rofreqs)
    plt.plot(currents, qfreqs)
    plt.plot(currents, t1times, 'o')
    plt.plot(currents, t2times, 'o')
    plt.plot(currents, t2etimes, 'o')
                    
                                
if 1: # Sweep Raspberry Pi parameter(s) and record currents
    raspi = mclient.instruments['raspi']
    raspi.do_set_domain('172.30.52.81')
    raspi.do_set_password('rafiki789')
    raspi.connect_ssh()
    
    Agilent1 = mclient.instruments['Agilent1']
    Agilent2 = mclient.instruments['Agilent2']
    Agilent3 = mclient.instruments['Agilent3']
    Keithley = mclient.instruments['Keithley']
    wait_time = 0.5
    index_to_sweep = 0
    sweep_range = np.linspace(0, 255, 256)
    currents = []
    
    params, data = raspi.import_data_('C:\qrlab\scripts\ROIC\spi_iface-main\default_2.csv')
    data = [int(0*data[x]) for x in range(len(data))]
    time.sleep(wait_time)
    currents.append([float(Agilent1.do_get_current()), float(Agilent2.do_get_current()), float(Agilent3.do_get_current()), float(Keithley.do_get_current())])
    
    for i in range(len(sweep_range)):
        data[index_to_sweep] = int(sweep_range[i])
        raspi.send_data_(data)
        time.sleep(wait_time)
        currents.append([float(Agilent1.do_get_current()), float(Agilent2.do_get_current()), float(Agilent3.do_get_current()), float(Keithley.do_get_current())])
        print(i, currents[i])
    tstamp = time.strftime("%Y%m%d")
    filename = 'C:\qrlab\scripts\ROIC\currents_' + str(tstamp) + '.csv'
    np.savetxt(filename, currents)
        

if 0: # 
    raspi = mclient.instruments['raspi']
    raspi.do_set_domain('172.30.52.81')
    raspi.do_set_password('rafiki789')
    raspi.connect_ssh()
    
    Agilent1 = mclient.instruments['Agilent1']
    Agilent2 = mclient.instruments['Agilent2']
    Agilent3 = mclient.instruments['Agilent3']
    Keithley = mclient.instruments['Keithley']
    wait_time = 0.5
    params, data = raspi.import_data_('C:\qrlab\scripts\ROIC\spi_iface-main\default_2.csv')
    data = [int(0*data[x]) for x in range(len(data))]
    
    current = float(Agilent1.do_get_current())
    target_current = 1e-3
    
    