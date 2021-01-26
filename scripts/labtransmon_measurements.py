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

alz = mclient.instruments['alazar']

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


# Load old settings.
if 0:
    toload = ['AWG1','ag1','ag2', 'ag3' 'alazar', 'qFC14#1', 'eFC14#1','qubit_DO13#3', 'ef_DO13#3', 'qubit_DO13#4', 'ef_DO13#4']
    mclient.load_settings_from_file(r'c:\_data\settings\20131214\165409.set', toload)    # Last time-Rabi callibration
    bla

qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
#qubit2_info = mclient.get_qubit_info('qubit2ge')
ef_info = mclient.get_qubit_info('qubit1ef')
gate_info = mclient.get_gate_info('gate')
gate2_info = mclient.get_gate_info('gate2')
gate3_info = mclient.get_gate_info('gate3')


#Find read-out cavity and choose a power

if 0: # RO Cavity spec
    from scripts.single_cavity import rocavspectroscopy
    rofreq = 6543.09e6
    freq_range = 10e6

    ro = rocavspectroscopy.ROCavSpectroscopy(qubit_info, np.linspace(-10, -10, 1),
                                         np.linspace(rofreq - freq_range, rofreq + freq_range, 51), qubit_pulse=False)
    ro.measure()
    bla
 
    
#Find qubit
if 0: # Qubit spec
    from scripts.single_qubit import spectroscopy
#    from scripts.single_qubit import spectroscopy_IQ
    qubit_freq = 5200e6
    freq_range = 200e6
    spec = spectroscopy.Spectroscopy(mclient.instruments['SCqubit'], qubit_info,
                                     np.linspace(qubit_freq-freq_range,
                                                 qubit_freq+freq_range, 201),
                                     [-10],
                                     plen=80000, amp=0.01, plot_seqs=False,
                                     freq_delay=.1) #1=1ns for plen

#    spec = spectroscopy_IQ.Spectroscopy_IQ(client.instruments['gen'], qubit_info,
#                                     np.linspace(702e6, 710e6, 81), [-30],
#                                    plen=250*100, amp=0.1, ssb=False, plot_seqs=False)

    spec.measure()
#    spec.measure_keysight()
    bla

"""Qubit SSBspec"""
if 1: # Qubit SSBspec
    from scripts.single_qubit import ssbspec
#    postseq = sequencer.Delay(500)
    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 5e6, 101), plot_seqs=False, proj_func='amplitude')
    spec.measure()
#    spec.measure_keysight()
    bla

'''Flux-tuned SSBspec'''
if 0: # Flux-tuned SSBspec
    from scripts.single_qubit import ssbspec
    Yoko = mclient.instruments['yoko']
    
    currents = np.linspace(-1.1, -1.4, 4)
    q_freq = np.zeros_like(currents)
    freqs = np.linspace(-5e6, 15e6, 101)
    alz.set_naverages(1000)
    for i in range(len(currents)):
        
        Yoko.do_set_current(currents[i])
        time.sleep(1)
        
        seq = sequencer.Trigger(250)        
        spec = ssbspec.SSBSpec(qubit_info, freqs, seq=seq, plot_seqs=False, proj_func='amplitude')
        spec.measure()
        q_freq[i] = freqs[np.argmin(spec.get_ys())]
    
    print(currents)
    print(q_freq)
    plt.figure()
    plt.plot(currents, q_freq)
        
    bla

"""Power Rabi -- Pi pulse calibration"""
if 0: # Power Rabi
    for i in range(1):
        from scripts.single_qubit import rabi
#        qubitgen.set_frequency(4532.71e6)
        tr = rabi.Rabi(qubit_info, np.linspace(-0.2, 0.2, 101), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
                       update=True, proj_func='projection')
#        from scripts.single_qubit import rabi_IQ
#        tr = rabi_IQ.Rabi(qubit_info, np.linspace(0, 0.5, 101), plot_seqs=False, real_signals=False)
        data=tr.measure()
#        neg = tr.avg_data
#        qubitgen.set_frequency(4535.51e6)
#        tr = rabi.Rabi(qubit_info, np.linspace(-0.2, 0.2, 101), plot_seqs=False, generate=True, selective=True, repeat_pulse=1,
#                       update=False)
#        data=tr.measure()
#        pos = tr.avg_data        
        
    bla

if 0: # Time Rabi
    from scripts.single_qubit import timerabi
    tr = timerabi.TimeRabi(gate_info, np.linspace(10, 1500, 5), amp=0.3)
    data = tr.measure()
    bla

if 0: # Qubit EFspec 
    from scripts.single_qubit import spectroscopy
    ef_freq = 4465e6
    freq_range = 5e6
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
    spec = spectroscopy.Spectroscopy(mclient.instruments['sc1'], ef_info, np.linspace(ef_freq-freq_range, ef_freq+freq_range, 151), [-40],
                                     plen=20000, amp=0.05,
                                     seq=seq, postseq=postseq,
                                     extra_info=qubit_info, plot_seqs=False)
    spec.measure()
    bla

if 0: # EF SSBspec
    from scripts.single_qubit import ssbspec
    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate_selective(np.pi, 0)])
    postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
#    postseq = sequencer.Sequence(qubit_info.rotate_selective(np.pi, 0))
    spec = ssbspec.SSBSpec(ef_info, np.linspace(-2.5e6, 2.5e6, 101), seq=seq, postseq = postseq, extra_info=qubit_info, plot_seqs=False, generate=True)
    spec.measure()
    bla

if 0: # EF rabi 
    from scripts.single_qubit import efrabi
#    alz.set_naverages(2000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.2, 0.2, 101), plot_seqs=False, selective=False, generate=True, update=True, proj_func='projection')
    efr.measure()
    period = efr.fit_params['period'].value
    alz.set_naverages(10000)
    efr = efrabi.EFRabi(qubit_info, ef_info, np.linspace(-0.2, 0.2, 101), first_pi=False, selective=False, force_period=period, generate=True, proj_func='projection')
    efr.measure()
    alz.set_naverages(1000)
    bla

if 0: # Single qubit tomography

    from scripts.single_qubit import Single_qubit_tomo
    tomo_result = []
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    sqtomo = Single_qubit_tomo.Single_qubit_tomo(qubit_info, seq=None, generate=True)  #seq=seq was added
    sqtomo.measure()
    tomo_result.append(sqtomo.get_ys())
    for i in range(5):
        sqtomo = Single_qubit_tomo.Single_qubit_tomo(qubit_info, seq=None, generate=False) #seq=seq added
        sqtomo.measure()
        tomo_result.append(sqtomo.get_ys())
        plt.close()
    print tomo_result
    bla

if 0: # Process_tomography
    from scripts.single_qubit import Process_tomo
    ptomo_result = []
    p_seq = sequencer.Sequence(sequencer.Delay(80))
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    sqtomo = Process_tomo.Process_tomo(qubit_info, process_seq=p_seq, generate=True)  #seq=seq was added
    sqtomo.measure()

    ptomo_result.append(sqtomo.get_ys())
    plt.close()

    print ptomo_result
    bla


    
if 0: # Drag test
    from scripts.single_qubit import drag_test
    dtest = drag_test.drag_test(qubit_info, np.linspace(-1.5, 1.5, 41), plot_seqs=False, generate=True)
    data=dtest.measure()
    bla

if 0: # AllXY
#    for i in range (1):
#        from scripts.single_qubit import rabi
#        tr = rabi.Rabi(qubit_info, np.linspace(0, 0.2, 81), plot_seqs=False, generate=True, selective=False, repeat_pulse=1,
#                       update=True)
#        data=tr.measure()

    alz.set_naverages(8000)
    from scripts.single_qubit import allxy
    allxy_result = []
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
    axy = allxy.All_XY(qubit_info, seq=None, generate=True, proj_func='projection')  #seq=seq was added
    axy.measure()
    allxy_result.append(allxy.get_ys())
    plt.close()
    for i in range(3):
        axy = allxy.All_XY(qubit_info, seq=None, generate=False) #seq=seq added
        axy.measure()
        allxy_result.append(allxy.get_ys())
        plt.close()
    print allxy_result
    plt.figure()
    for i in range(10): plt.plot(allxy_result[i])
    bla

if 0: # Randomized benchmarking

    from scripts.single_qubit import rndm
#    rndmben_result = []
    for i in range(10):
        rndmben = rndm.rndm(qubit_info, min_gates=1, max_gates=148, gate_step=3, seq=None, generate=True) #seq=seq added
        rndmben.measure()
        rndmben_result.append(rndmben.get_ys())
#        plt.close()
        plt.figure(5)
        plt.plot(rndmben.xs, rndmben.get_ys())#, linestyle=None)
#    print rndmben_result
    bla

if 0: # Mixer calibration:
    from scripts.single_qubit import mixer_calibration
    mixer_cal = mixer_calibration.Mixer_Calibration

    cal = mixer_cal('qGB14#2',7764e6, 'VA', 'AWG1', verbose=True,
                        base_amplitude= 3,
                        va_lo='brick3') # The frequency is the targeted lower sideband frequency, not the carrier

    cal.prep_instruments(reset_offsets=True, reset_ampskew=True)
    cal.tune_lo(mode='coarse')
    cal.tune_osb(mode=(0.5, 2000, 3, 1))
    cal.tune_lo(mode='fine') # useful if using 10 dB attenuation;
                            # LO leakage may creep up during osb tuning

    # this function will set the correct qubit_info sideband phase for use in experiments
    #    i.e. combines the AWG skew with the  7036.120e6current sideband phase offset
    cal.set_tuning_parameters(set_sideband_phase=True)
    cal.load_test_waveform()
    cal.print_tuning_parameters()
    bla

if 0: # Check histogramming
    from scripts.single_qubit import rabi
    twpa = mclient.instruments['WF_twpa']
    RO = mclient.instruments['RObrick']
    ro = mclient.instruments['readout']
    alz.set_naverages(50000)
#    alz.set_nsamples(1920)
#    ro.set_pulse_len(1920)
    int_lens = [1280, 1280, 1280]
    pump_freqs = np.linspace(8.165e9, 8.165e9, 1)
    pump_powers = np.linspace(-3.38, -3.38, 1)
    RO_powers = np.linspace(3, 3, 1)
    fidelities = []
    ge_errors = []
    eg_errors = []
    overlap_errors = []
    SNRs = []
    for length in int_lens:
        alz.set_nsamples(length)
        ro.set_pulse_len(length)
        for freq in pump_freqs:
            twpa.set_frequency(freq)
#            tr_g = rabi.Rabi(qubit_info, [0.0000001,], histogram=True, proj_func='amplitude', title='|g>')
#            tr_g.measure()
#            tr_e = rabi.Rabi(qubit_info, [qubit_info.pi_amp], histogram=True, proj_func='amplitude', title='|e>')
#            tr_e.measure()
            tr = rabi.Rabi(qubit_info, [0.00000001, qubit_info.pi_amp,], histogram=True, proj_func='amplitude', title='|g> and |e>')
            tr.measure()
    #        alz.set_naverages(1000)
            
        #if 1: # histogram calculating and plotting
            e_data = tr.shot_data[1::2]
            g_data = tr.shot_data[::2]
            
            #find blob centers
            g_average = np.average(g_data)
            e_average = np.average(e_data)
            midpoint = np.average([g_average, e_average])
        
            #setup plots
            lim = 300
            xvec = np.linspace(-lim, lim, 100)
            fig = plt.figure(figsize=(6, 8))
            gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
            ax1 = fig.add_subplot(gs[0])    
            ax2 = fig.add_subplot(gs[1])
            ax1.set_xlim(-lim, lim)
            ax1.set_ylim(-lim, lim)
            
            #plot centers
            ax1.scatter(np.real(g_average), np.imag(g_average), color='b')
            ax1.scatter(np.real(e_average), np.imag(e_average), color='r')
            ax1.scatter(np.real(midpoint), np.imag(midpoint), color='k')
            
            #calculate separatrix
            m = (np.imag(g_average) - np.imag(e_average))/(np.real(g_average) - np.real(e_average))
            b = np.imag(g_average) - m * np.real(g_average)
            ax1.plot(xvec, m*xvec+b, linestyle='dashed', color='k')
            
            #plot blobs in 2d
            ax1.hexbin(np.real(g_data), np.imag(g_data), bins=100, alpha=.4, 
                       cmap='Blues', edgecolors='none')
            ax1.hexbin(np.real(e_data), np.imag(e_data), bins=100, alpha=.4, 
                       cmap='Reds', edgecolors='none')
            
            # calculate and plot projections
            g_project = (np.real(g_data) + np.imag(g_data)*m) / np.sqrt(1 + m**2)
            e_project = (np.real(e_data) + np.imag(e_data)*m) / np.sqrt(1 + m**2)
            g_hist, g_bins, patches = ax2.hist(g_project, bins=100, alpha=.4, color='b')
            e_hist, e_bins, patches = ax2.hist(e_project, bins=100, alpha=.4, color='r')
            
            # fit projections
        #    xs = [g_bins[:-1], e_bins[:-1]]
        #    colors = ['b', 'r']
        #    means = []
        #    stds = []
        #    for i, ys in enumerate([g_hist, e_hist]):
        #        params = lmfit.Parameters()
        #        params.add('amp', value=np.max(ys), min=0)
        #        params.add('mean', value=np.mean(ys))
        #        params.add('std', value=np.std(ys), min=0)
        #        result = lmfit.minimize(gaussian, params, args=(xs[i], ys))
        #        means += [result.params['mean']]
        #        stds += [result.params['std']]
        #        lmfit.report_fit(result.params)
        #        ax2.plot(xs[i], -gaussian(result.params, xs[i], 0), color=colors[i], linestyle='dashed')
                
            # fit sum of two gaussians
            xs = [g_bins[:-1], e_bins[:-1]]
            g_center = g_bins[g_hist.argmax()]
            e_center = e_bins[e_hist.argmax()]
            lines = []
            colors = ['b', 'r']
            amps = []
            means = []
            stds = []
            for i, ys in enumerate([g_hist, e_hist]):
                params = lmfit.Parameters()
                params.add('amp1', value=np.max(ys), min=0)
                params.add('mean1', value=g_center)
                params.add('std1', value=np.std(xs[i]), min=1)
                params.add('amp2', value=np.max(ys), min=0)
                params.add('mean2', value=e_center)
                params.add('std2', value=np.std(xs[i]), min=1)
                result = lmfit.minimize(gaussian_sum, params, args=(xs[i], ys))
                amps += [result.params['amp1'], result.params['amp2']]
                means += [result.params['mean1'], result.params['mean2']]
                stds += [result.params['std1'], result.params['std2']]
                lmfit.report_fit(result.params)
                ax2.plot(xs[i], -gaussian_sum(result.params, xs[i], 0), color=colors[i], linestyle='dashed')
                lines += [-gaussian_sum(result.params, xs[i], 0)]
                
            threshold = (np.min([means[0], means[1]])+np.max([means[2],means[3]]))/2
            ax2.axvline(threshold)
            threshold_indices = [np.where(g_bins == g_bins[np.abs(g_bins-threshold).argmin()])[0][0], np.where(e_bins == e_bins[np.abs(e_bins-threshold).argmin()])[0][0]]
            ge_error_prob = np.sum(g_hist[threshold_indices[0]:])/np.sum(g_hist)
            ge_errors += [ge_error_prob]
            eg_error_prob = np.sum(e_hist[:threshold_indices[1]])/np.sum(e_hist)
            eg_errors += [eg_error_prob]
            fidelity = 1 - (ge_error_prob + eg_error_prob)/2
            fidelities += [fidelity]
            print('Fidelity = ', fidelity)
            print('|g>-|e> error = ', ge_error_prob)
            print('|e>-|g> error = ', eg_error_prob)
            plt.figure()
            plt.plot(g_bins[:-1], lines[0])
            plt.plot(e_bins[:-1], lines[1])
            plt.axvline(threshold, color='g', linestyle='dashed')
            plt.title(fidelity)
            
            print('SNR = ', np.abs(means[3] - means[0]) / (stds[3] + stds[0])/2)
            SNRs += [np.abs(means[3] - means[0]) / (stds[3] + stds[0])/2]
            '''
            ax2.plot(np.linspace(-lim, lim, 100), gaussian(np.linspace(-lim, lim, 100), 
                                 g_mean, g_std), linestyle='dashed', color='b')
            ax2.plot(np.linspace(-lim, lim, 100), gaussian(np.linspace(-lim, lim, 100), 
                                 e_mean, e_std), linestyle='dashed', color='r')
            '''
            
#            plt.figure()
            if amps[0].value > amps[1].value:
                gaussian1 = amps[0].value*np.exp(-.5*((xs[0] - means[0].value) / stds[0].value)**2)
                princ1 = 0
            else:
                gaussian1 = amps[1].value*np.exp(-.5*((xs[0] - means[1].value) / stds[1].value)**2)
                princ1 = 1
            if amps[2].value > amps[3].value:
                gaussian2 = amps[2].value*np.exp(-.5*((xs[1] - means[2].value) / stds[2].value)**2)
                princ2 = 2
            else:
                gaussian2 = amps[3].value*np.exp(-.5*((xs[1] - means[3].value) / stds[3].value)**2)
                princ2 = 3
            plt.plot(xs[0], gaussian1, color='purple', linestyle='dashed')
            plt.plot(xs[1], gaussian2, color='r', linestyle='dashed')
            plt.ylim(10, 3000)
            plt.yscale('log')
#            plt.axvline((means[princ1].value+means[princ2].value)/2, color='g', linestyle='dashed')
            overlap_error = np.sum(gaussian1[threshold_indices[0]:])/np.sum(gaussian1) + np.sum(gaussian2[:threshold_indices[1]])/np.sum(gaussian2)
            overlap_errors += [overlap_error]
            print('overlap error = ', overlap_error)
#            plt.title(overlap_error)
#            alz.set_naverages(1000)
        #    e_data = np.abs(e_data)
        #    g_data = np.abs(g_data)
        #    plt.hist(e_data, bins=100, color='r', alpha=0.5)
        #    plt.hist(g_data, bins=100, color='b', alpha=0.5)


if 1: # TWPA histogram sweep
    from scripts.single_qubit import rabi
    alz.set_naverages(50000)
    twpa = mclient.instruments['WF_twpa']
    RO = mclient.instruments['RObrick']
    twpa.set_rf_on(True)
    powers = np.linspace(-3.5, -3, 11)
    freqs = np.linspace(8.16e9, 8.17e9, 51)
    ROpowers = np.linspace(-20, -10, 5)
    SNRs = []
    for r in ROpowers:
        RO.set_power(r)
        for p in powers:
            twpa.set_power(p)
            for f in freqs:
                twpa.set_frequency(f)
                print(r, p, f)
                tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp, 0.000001], histogram=True, title='|e>')
                tr.measure()
                dat = tr.shot_data[1::2]
                SNR = np.abs(np.mean(dat))/np.std(dat)
                SNRs.append(SNR)
                plt.close()
#    tr = rabi.Rabi(qubit_info, [0.0000001,], histogram=True, title='|g>')
#    tr.measure()
#    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp], histogram=True, title='|e>')
#    tr.measure()
    alz.set_naverages(1000)
#    array = np.asarray(SNRs)
#    SNRs_array = array.reshape((len(powers), len(freqs)))
#    plt.pcolormesh(freqs, powers, SNRs_array)
    twpa.set_rf_on(False)
#    tr = rabi.Rabi(qubit_info, [qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>')
#    tr.measure()


if 0: # T1
    from scripts.single_qubit import T1measurement
#    alz.set_naverages(5000)
#    t1times = np.zeros(len(range(1000)))
    for i in range(1):
        #postseq = sequencer.Sequence(qubit_info.rotate(np.pi, 0))
        t1 = T1measurement.T1Measurement(qubit_info, np.linspace(0, 60e3, 101), double_exp=False, generate=True, plot_seqs=False, proj_func='projection')
        t1.measure()
#        t1times[i] = t1.analyze()
#        plt.close()
    bla

if 0: # T2
    from scripts.single_qubit import T2measurement
    for i in range(1):
        t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 20e3, 101), detune=0.2e6, double_freq=False, generate=True, proj_func='projection')
        t2.measure()
    bla

if 0: # T2echo
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(100, 30e3, 101), detune=0.2e6, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                     proj_func='projection')
    t2.measure()
    bla

if 0: # FT1
    from scripts.single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))
    for i in range(1):
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 30e3, 101))
        ft1.measure()
        #ft1times[i] = ft1.analyze()
        #plt.close()
    bla

if 0: # EFT2
    from scripts.single_qubit import EFT2measurement # frequency stability of |f> vs |e>
    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_NONE)
    eft2.measure()

if 0: # GFT2
    from scripts.single_qubit import GFT2measurement # frequency stability of |f> vs |g> # Echo does not work
    gft2 = GFT2measurement.GFT2Measurement(qubit_info, ef_info, np.linspace(0, 10e3, 101), detune=0.5e6, double_freq=False, plot_seqs = False, echotype = EFT2measurement.ECHO_HAHN)
    gft2.measure()

if 0: # Number splitting:
    from scripts.single_qubit import spectroscopy
    seq = sequencer.Join([sequencer.Trigger(250), cavity_info.rotate(np.pi, 0)])
#    postseq = sequencer.Sequence([sequencer.Trigger(250), cavity_info.rotate(np.pi, 0)])
    qubit_freq = 4534.0e6
    spec = spectroscopy.Spectroscopy(mclient.instruments['geFG'], qubit_info, np.linspace(qubit_freq-8e6, qubit_freq+2e6, 101), [-4],
                                     plen=1000, seq = seq, amp=0.01, freq_delay=.1, extra_info=cavity_info, plot_seqs=True)
    spec.measure()


if 0: # SSB number splitting:
    from scripts.single_qubit import ssbspec
#    geFG = mclient.instruments['geFG']
#    geFG.set_frequency(geFG.get_frequency()-1.25e6)
    seq = sequencer.Join([sequencer.Trigger(250), cavity_info.rotate(np.pi, 0)])
#    postseq = sequencer.Delay(2000)
#    cav_pulse = sequencer.Combined([
#                    sequencer.Constant(1000, 1, chan="3m2"),
#                    ])
#    seq = sequencer.Join([sequencer.Trigger(250), cav_pulse])
#    seq = sequencer.Join([sequencer.Trigger(250), sequencer.Constant(50000, 1, chan="3m2")])

    spec = ssbspec.SSBSpec(qubit_info, np.linspace(-5e6, 1e6, 81),
                           seq=seq, extra_info=cavity_info, plot_seqs=False, generate=True)
#    geFG.set_frequency(geFG.get_frequency()+1.25e6)
    spec.measure()
#    for coplay_delay in [12000]:
#        spec = ssbspec.SSBSpec(qubit_info, np.linspace(-3e6, 2e6, 121),
#                           seq=None, extra_info=cavity_info, plot_seqs=False, coplay_delay=coplay_delay)
#        spec.measure()
    bla


if 0: # Two-Qubit Randomized Benchmarking
    from scripts.fluxonium import TwoQ_RB
    for i in range(1):
    
        TwoQ = TwoQ_RB.TwoQubit_RB(gate_info, gate2_info, gate3_info, gate3_info, num_cal_points=3, N_cliffords=10, 
                                   plot_seqs=False, category='all',
                                   find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, 
                                   use_lookup_table=True, generator='CZ')
        TwoQ.measure()
#    (err_clif, err_gate) = TwoQ.analyze()
#    print('error per Clifford:', err_clif)
#    print('error per gate:', err_gate)
