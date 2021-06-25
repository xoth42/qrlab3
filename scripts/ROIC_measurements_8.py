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

if 0: # RO Cavity spec
    from scripts.single_cavity import rocavspectroscopy_keysight
    rofreq = 6525e6
    freq_range = 15e6
    for pulse in [False]:
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(10, 10, 1),
                                             np.linspace(rofreq - freq_range, rofreq + freq_range, 101), qubit_pulse=pulse)
        ro.measure()

    bla

if 0: # RO Cavity spec w/TWPA sweep
    from scripts.single_cavity import rocavspectroscopy_keysight
    rofreq = 6540e6
    freq_range = 8e6
    sweep_twpa = True
    if sweep_twpa:
        twpa = mclient.instruments['WF_twpa']
        powers = np.linspace(-8, -6.5, 16)
        freqs = np.linspace(8.16e9, 8.195e9, 151)
        for power in powers:
            twpa.set_power(power)
            for freq in freqs:
                twpa.set_frequency(freq)
                ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-15, -15, 1),
                                                     np.linspace(rofreq - freq_range, rofreq + freq_range, 51), qubit_pulse=False)
                ro.measure()
                plt.close('all')
    bla
    
if 0: # Qubit spec
    from scripts.single_qubit import spectroscopy_keysight
    qubit_freq = 5500e6
    freq_range = 500e6
    spec = spectroscopy_keysight.Spectroscopy_Keysight(mclient.instruments['Qbrick'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 1001),
                                     [-15],
                                     plen=20000, amp=0.05, plot_seqs=False,
                                     freq_delay=.1) #1=1ns for plen

    spec.measure()
    bla

"""Qubit SSBspec"""

if 0: # Qubit SSBspec
    from scripts.single_qubit import ssbspec
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-20e6,20e6, 151), plot_seqs=False, proj_func='amplitude')
    spec.measure_keysight()
    bla
    
if 0: # Power Rabi
    for i in range(1):
        from scripts.single_qubit import rabi
        tr = rabi.Rabi(qubit_info, np.linspace(-0.4, 0.4, 101), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=True, proj_func='amplitude')

        tr.measure_keysight()     
    bla
    
if 0: # T1
    from scripts.single_qubit import T1measurement
    for i in range(1):
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 40e3, 101), double_exp=False, generate=True, plot_seqs=False, proj_func='amplitude')
        t1.measure_keysight()
    bla
    
if 0: # T2
    from scripts.single_qubit import T2measurement
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 1.5e3, 101), detune=3e6, double_freq=False, generate=True, proj_func='amplitude')
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
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-10e6, 10e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True, proj_func='amplitude')
    spec.measure_keysight()
    bla

if 0: # EF rabi 
    from scripts.single_qubit import efrabi
    dig.set_naverages(3000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.3, 0.3, 101), plot_seqs=False, selective=False, generate=True, update=True, proj_func='amplitude')
    efr.measure_keysight()
    period = efr.fit_params['period'].value
    dig.set_naverages(20000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.3, 0.3, 101), first_pi=False, selective=False, force_period=period, generate=True, proj_func='amplitude')
    efr.measure_keysight()
    dig.set_naverages(3000)
    bla
    
if 0: # T1, T2 vs. flux
    #define instruments
    RObrick = mclient.instruments['RObrick']
    refbrick = mclient.instruments['refbrick']
    Qbrick = mclient.instruments['Qbrick']
    yoko = mclient.instruments['yoko']
    
    currents = np.linspace(3.1, 3.5, 21) # units: mA
    rofreqs = np.zeros_like(currents)
    qfreqs = np.zeros_like(currents)
    t1times = np.zeros_like(currents)
    t2times = np.zeros_like(currents)
    t2etimes = np.zeros_like(currents)
    
    rospec_centerfreq = 6530e6
    ro_freq_range = 15e6
    
    qubitspec_centerfreq = 5100e6
    qubit_freq_range = 600e6
    
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
                                                 qubitspec_centerfreq+qubit_freq_range, 1001),
                                     [-15],
                                     plen=80000, amp=0.01, plot_seqs=False,
                                     freq_delay=.1)
        spec.measure()
        qfreq = np.linspace(qubitspec_centerfreq-qubit_freq_range,
                                                 qubitspec_centerfreq+qubit_freq_range, 1001)[np.argmin(spec.ampdata[0,:])]
        qfreqs[i] = qfreq
        Qbrick.set_frequency(qfreq+100e6)

        tr = rabi.Rabi(qubit_info, np.linspace(-0.5, 0.5, 101), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=True, proj_func='amplitude')     
        data=tr.measure_keysight()               
        
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 5e3, 101), double_exp=False, generate=True, plot_seqs=False, proj_func='amplitude')
        t1.measure_keysight()
        t1times[i] = t1.analyze()
#        
#        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 1e3, 101), detune=4e6, double_freq=False, generate=True, proj_func='amplitude')
#        t2.measure_keysight()
#        t2times[i] = t2.analyze()
#        
#        t2e = T2measurement.T2Measurement(qubit_info, np.linspace(100, 4e3, 61), detune=1e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
#                                     proj_func='amplitude')
#        t2e.measure_keysight()
#        t2etimes[i] = t2e.analyze()
        
        plt.close('all')
        
    plt.plot(currents, rofreqs)
    plt.plot(currents, qfreqs)
    plt.plot(currents, t1times, 'o')
    plt.plot(currents, t2times, 'o')
    plt.plot(currents, t2etimes, 'o')
                    
                                
if 0: # Sweep Raspberry Pi parameter(s) and record currents
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
    
    params, chip_data = raspi.import_data_('C:\qrlab\scripts\ROIC\spi_iface-main\default_2.csv')
    chip_data = [int(0*chip_data[x]) for x in range(len(chip_data))]
    time.sleep(wait_time)
    currents.append([float(Agilent1.do_get_current()), float(Agilent2.do_get_current()), float(Agilent3.do_get_current()), float(Keithley.do_get_current())])
    
    for i in range(len(sweep_range)):
        chip_data[index_to_sweep] = int(sweep_range[i])
        raspi.send_data_(chip_data)
        time.sleep(wait_time)
        currents.append([float(Agilent1.do_get_current()), float(Agilent2.do_get_current()), float(Agilent3.do_get_current()), float(Keithley.do_get_current())])
        print(i, currents[i])
    tstamp = time.strftime("%Y%m%d%H%M")
    filename = 'C:\qrlab\scripts\ROIC\currents_' + str(tstamp) + '.csv'
    np.savetxt(filename, currents)

if 1: # Sweep chip param, get voltage
    DMM = mclient.instruments['DMM']
    wait_time = 0.5
    indices_to_sweep = [38, 39]
    sweep_range = np.linspace(0, 255, 256)
    voltages = []
    
    for i in range(len(sweep_range)):
        chipdata[indices_to_sweep[0]] = int(sweep_range[i])
        for j in range(len(sweep_range)):
            chipdata[indices_to_sweep[1]] = int(sweep_range[j])
            raspi.send_data_(chipdata)
            time.sleep(wait_time)
            voltages.append(float(DMM.do_get_voltage()))
            print(i, j, chipdata[indices_to_sweep[0]], chipdata[indices_to_sweep[1]])
    tstamp = time.strftime("%Y%m%d%H%M")
    filename = 'C:\qrlab\scripts\ROIC\DACvoltages_' + str(tstamp) + '.csv'
    np.savetxt(filename, voltages)        

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

if 0: # Sequence to run before doing test dig for ROIC
    import ROIC_test_dig_sequence
    rofreq = 6000e6
    freq_range = 0
    roic = ROIC_test_dig_sequence.roic_test_dig_sequence(qubit_info, np.linspace(-40, -40, 1),
                                         np.linspace(rofreq - freq_range, rofreq + freq_range, 11), qubit_pulse=False)
    roic.measure()

    bla

if 1: # Sweep phase of RF pulse for ROIC RT test
    from scripts.single_qubit import ROIC_roomtemp_testing
    qubit_freq = 6625.1e6
    freq_range = 0e6
    phases = np.linspace(0, 2*np.pi, 5)
    dig = mclient.instruments['dig']
    threshold = 100
    count = 10
    PWR = np.linspace(0.001,0.01,1)
    for pwr in PWR:
        roic_stats = []
        for phase in [0]:
            #raspi.send_data_(chip_data)
            print("currents" + str([float(LNA23.do_get_current()), float(BBAC.do_get_current()), float(LNA1.do_get_current()), float(IREF.do_get_current())]))
            roic_phase = ROIC_roomtemp_testing.roic_roomtemp_testing(mclient.instruments['Qbrick'], qubit_info, qubit2_info,
                                             np.linspace(qubit_freq-freq_range,
                                                         qubit_freq+freq_range, count),
                                             [-15],
                                             plen_RF=1000, plen_LO=80000, amp_RF=0.1, amp_LO=0.6, phase=phase, plot_seqs=True,
                                             freq_delay=.1) #1=1ns for plen
        
            roic_phase.measure(threshold=threshold)

#        np.savetxt('C:\qrlab\scripts\ROIC\stats_RF_'+str(pwr)+'_time_'+str(time.strftime("%Y%m%d%H%M"))+'.csv',np.asarray(roic_stats))
#        stats_array = np.asarray(roic_stats)
#        fig = plt.figure()
#        gs = gridspec.GridSpec(1,2)
#        ax1 = fig.add_subplot(gs[0,0])
#        ax2 = fig.add_subplot(gs[0,1])
#        ax1.plot(stats_array[:,0], stats_array[:,1], label='I')
#        ax1.plot(stats_array[:,0], stats_array[:,2], label='Q')
#        ax1.set_ylim(0,1)
#        ax2.plot(stats_array[:,1], stats_array[:,2], label='IQ')
#        ax2.set_xlim(0,1)
#        ax2.set_ylim(0,1)
#        gs.tight_layout(fig,rect[1,0,2,1])
#        plt.show()
    bla
    
if 0: # test digitizer ROIC 4 channels
    dig = mclient.instruments['dig']
    threshold_list = []; Itrig=0; Qtrig=0
    threshold = 100
    count = 4000
    for i in range(count):
        print(i)
        data = dig.test_dig_ROIC(2000, 1, 1, 1)
        print(np.shape(data))
        if np.max(data[2][0][:]) > threshold:
            Itrig = 1
        else:
            Itrig = 0
        if np.max(data[3][0][:]) > threshold:
            Qtrig = 1
        else:
            Qtrig = 0
        
        threshold_list.append([Itrig,Qtrig])
#        plt.figure()
    #    plt.plot(data[0][0][:], label = '1')
    #    plt.plot(data[1][0][:], label = '2')
#        plt.plot(data[2][0][:], label = '3')
#        plt.plot(data[3][0][:], label = '4')
#        plt.legend() 
#        plt.show()
    print(np.sum(threshold_list, axis=0)/float(count))
    bla   