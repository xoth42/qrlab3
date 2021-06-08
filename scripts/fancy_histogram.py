# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 14:53:09 2018

@author: jeff
"""

def gaussian(params, x, data):
    return data - params['amp'] * np.exp(-.5 * ((x - params['mean']) / params['std'])**2)




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
import datetime
from matplotlib import gridspec
import lmfit


#fxb01 = mclient.get_qubit_info('fxb01')
#fxa01 = mclient.get_qubit_info('fxa01')

readout = 'readout_IQ'
dig = mclient.instruments['dig']


qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
#fh_info = mclient.get_qubit_info('qubit1fh')
#qubit_a1 = mclient.get_qubit_info('qubit_a1')
#qubit_a1b1 = mclient.get_qubit_info('qubit_a1b1')
#qubit_a2b2 = mclient.get_qubit_info('qubit_a2b2')
#qubit_a3b3 = mclient.get_qubit_info('qubit_a3b3')

#qubit_b1 = mclient.get_qubit_info('qubit_b1')

#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#RO_info = mclient.get_qubit_info('RO')
#qubit2_info = mclient.get_qubit_info('cavityAlice')
os.chdir(r'C:/qrlab/scripts')
    
if 0: # test digitizer
    dig = mclient.instruments['dig']
    data = dig.test_dig(5200, 1, 1, 1)
    print(np.shape(data))
    plt.figure()
    plt.plot(data[0][0][:], label = 'sig')
    plt.plot(data[1][0][:], label = 'ref')
    plt.legend() 
    plt.show() 
    bla
    
if 0: # test digitizer DEMODULATED
    dig = mclient.instruments['dig']
    avgs = dig.test_dig_demod(3000, 10000)
    print(np.shape(avgs))
    plt.figure()
    plt.plot(np.real(avgs), label = 'real')
    plt.plot(np.imag(avgs), label = 'imag')
    plt.plot(np.abs(avgs), label = 'abs')
    plt.legend() 
    plt.show()
    bla


def take_snr():
    from scripts.single_qubit import rabi
    tr_e = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>',
                     readout=readout)
    tr_e.measure_keysight()
    tr_g = rabi.Rabi(qubit_info, [0.001,], histogram=True, title='|g>',
                     readout=readout)
    tr_g.measure_keysight()
    
    
    plt.close(tr_e.get_figure())
    plt.close(tr_g.get_figure())
    
    e_data = tr_e.shot_data[:]
    g_data = tr_g.shot_data[:]

    g_average = np.average(g_data)
    e_average = np.average(e_data)    
    m = (np.imag(g_average) - np.imag(e_average))/(np.real(g_average) - np.real(e_average))
    b = np.imag(g_average) - m * np.real(g_average)
    
    g_project = (np.real(g_data) + np.imag(g_data)*m) / np.sqrt(1 + m**2)
    e_project = (np.real(e_data) + np.imag(e_data)*m) / np.sqrt(1 + m**2)
    g_hist, g_bins = np.histogram(g_project, bins=100)
    e_hist, e_bins = np.histogram(e_project, bins=100)
    
    # fit projections
    xs = [g_bins[:-1], e_bins[:-1]]
    means = []
    stds = []
    for i, ys in enumerate([g_hist, e_hist]):
        params = lmfit.Parameters()
        params.add('amp', value=np.max(ys), min=0)
        params.add('mean', value=np.mean(ys))
        params.add('std', value=np.std(ys), min=0)
        result = lmfit.minimize(gaussian, params, args=(xs[i], ys))
        means += [result.params['mean']]
        stds += [result.params['std']]
        #lmfit.report_fit(result.params)
    
    snr = (means[1] - means[0]) / (stds[0] + stds[1])/2
    print('SNR = ', snr)
    return snr

if 0: # Check histogramming
    dig.set_naverages(10000)
    take_snr()
    
    
if 1: # histogram calculating and plotting
    dig.set_naverages(10000)
    from scripts.single_qubit import rabi
    tr_e = rabi.Rabi(qubit_info, [qubit_info.pi_amp,], histogram=True, title='|e>',
                     readout=readout)
    tr_e.measure_keysight()
    tr_g = rabi.Rabi(qubit_info, [0.001,], histogram=True, title='|g>',
                     readout=readout)
    tr_g.measure_keysight()

    e_data = tr_e.shot_data[:]
    g_data = tr_g.shot_data[:]
    
    #find blob centers
    g_average = np.average(g_data)
    e_average = np.average(e_data)
    midpoint = np.average([g_average, e_average])

    #setup plots
    lim = 20
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
    xs = [g_bins[:-1], e_bins[:-1]]
    colors = ['b', 'r']
    means = []
    stds = []
    for i, ys in enumerate([g_hist, e_hist]):
        params = lmfit.Parameters()
        params.add('amp', value=np.max(ys), min=0)
        params.add('mean', value=np.mean(ys))
        params.add('std', value=np.std(ys), min=0)
        result = lmfit.minimize(gaussian, params, args=(xs[i], ys))
        means += [result.params['mean']]
        stds += [result.params['std']]
        lmfit.report_fit(result.params)
        ax2.plot(xs[i], -gaussian(result.params, xs[i], 0), color=colors[i], linestyle='dashed')
    
    
    print('SNR = ', np.abs(means[1] - means[0]) / (stds[0] + stds[1])/2)
    '''
    ax2.plot(np.linspace(-lim, lim, 100), gaussian(np.linspace(-lim, lim, 100), 
                         g_mean, g_std), linestyle='dashed', color='b')
    ax2.plot(np.linspace(-lim, lim, 100), gaussian(np.linspace(-lim, lim, 100), 
                         e_mean, e_std), linestyle='dashed', color='r')
    '''
    
    
if 0: #calibrate twpa (correct w/ snr)
    dig.set_naverages(2000)
    rf_twpa = mclient.instruments['WF_twpa']
    twpa_powers = np.linspace(-4, -2, 5)
    freq = 7.844e9
    freq_range = 10e6
    twpa_freqs = np.linspace(freq-freq_range, freq+freq_range, 50)
    
    snrs = np.zeros((len(twpa_powers), len(twpa_freqs)))
    for i, power in enumerate(twpa_powers):
        rf_twpa.set_power(power)
        time.sleep(.1)
        for j, freq in enumerate(twpa_freqs):
            rf_twpa.set_frequency(freq)
            time.sleep(.1)
            snrs[i,j] = take_snr()
    
    print('max of ' + str(np.max(snrs)) + ' at ' 
          + str(twpa_powers[np.argmax(snrs)/len(twpa_freqs)]) + 'dbm and ' 
          + str(twpa_freqs[np.argmax(snrs)%len(twpa_freqs)]/1e6) + 'mhz')
    
    plt.figure()
    plt.yticks(twpa_powers)   # dumb stuff to make plotting nicer
    ys = np.concatenate((twpa_powers, np.array([2 * twpa_powers[-1] - twpa_powers[-2]])))
    ys -= (ys[1]-ys[0])/2
    plt.pcolormesh(twpa_freqs, ys, snrs)
    plt.colorbar()
    



if 0: # cav transmission
    from single_cavity import rocavspectroscopy_keysight
    rofreq = 7317.52e6
#    rofreq = 7320e6
    freq_range =1e6
    freqs = np.linspace(rofreq-freq_range, rofreq+freq_range, 51)
    powers = np.linspace(0, 5, 6)

    for i in range(1):    
        ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, powers, freqs,
         #                                        np.linspace(rofreq, rofreq+freq_range, 1), 
                                                 qubit_pulse=False, seq=None)
        ro.measure()
        
        '''amp = ro.ampdata[:]
        f= open('ampdata_2d_HP.txt', 'w')
        f.write(str(amp))
        f.close()'''
        
    bla


    
if 0: # Calibrate TWPA SNR (questionable???)
    def analysis(twpa_powers, twpa_freqs, ampdata, ax=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        data = ampdata[:]
        x, y = np.meshgrid(np.append(twpa_powers, 2* twpa_powers[-1] - twpa_powers[-2]),
                       np.append(twpa_freqs, 2* twpa_freqs[-1] - twpa_freqs[-2]))
        img = ax.pcolormesh(x, y, data.T)
        fig.colorbar(img)
        ax.set_xlabel('twpa powers')
        ax.set_ylabel('twpa frequencies')

    from single_qubit import rabi
    twpa_powers = np.linspace(-4.2, -4.0, 5)
    freq = 7.918e9
    freq_range = 3e6
    twpa_freqs = np.linspace(freq-freq_range, freq+freq_range, 7)
    naverages = 3000

    ampdata = np.zeros([len(twpa_powers), len(twpa_freqs)])
    stddata = np.zeros([len(twpa_powers), len(twpa_freqs)])
    snrdata = np.zeros([len(twpa_powers), len(twpa_freqs)])
    dig.set_naverages(naverages)    
    SCqubit.set_rf_on(False)
    
    for i, p in enumerate(twpa_powers):
        SCTWPA.set_power(p)
        for j, f in enumerate(twpa_freqs):
            SCTWPA.set_frequency(f)
            tr = rabi.Rabi(qubit_info, 
                   np.linspace(-0.9, 0.9, 41), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=None)    
            tr.measure_keysight()
            IQ = tr.avg_data
            ampdata[i,j] = np.abs(IQ.mean())
            stddata[i,j] = np.std(IQ)
            snrdata[i,j] = np.abs(IQ.mean())/np.std(IQ)/np.sqrt(naverages)
            plt.close()
    analysis(twpa_powers, twpa_freqs, ampdata)
    analysis(twpa_powers, twpa_freqs, snrdata)
    bla
    

    
if 0: # Calibrate pi pulse
    from single_qubit import rabi
    tr = rabi.Rabi(qubit_info, 
                   np.linspace(-1, 1, 51), selective=False,
#                   np.linspace(-.1, .1, 51), selective=.5,
#                  np.linspace(-0.015, 0.015, 51), selective=True,
#                   np.linspace(0.7, .9, 51), selective=False,
#                   np.linspace(0.45, 0.52, 51), selective=False,
                   plot_seqs=False, generate=True, repeat_pulse=2, update=False, seq=None)
    tr.measure_keysight()
    bla
    
if 0: # T1
#    dig.set_trigger_period(500)
    from single_qubit import T1measurement
    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 19e3, 20), np.linspace(20e3, 160e3, 20))), 
#    t1 = T1measurement.T1Measurement(qubit_info, np.concatenate((np.linspace(0, 1e3, 151),)), 
                                     double_exp=False, generate=True, plot_seqs=False, seq=None)
    t1.measure_keysight()
#    bla

if 0: # T2
    from single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0e3, 20e3, 101), detune=.5e6, 
#    t2 = T2measurement.T2Measurement(qubit_info, np.linspace(0, 3.9e3, 81), detune=2e6, 
                                     double_freq=False, generate=True, seq=None,
                                     plot_seqs=False)
    t2.measure_keysight()
    bla
    

if 0: # EF rabi for calibration
    from single_qubit import efrabi
    dig = mclient.instruments['dig']
    dig.set_naverages(1000)
    efr = efrabi.EFRabi(qubit_info, ef_info, 
#                   np.linspace(-0.9, 0.9, 51), selective=False,
                   np.linspace(-0.02, 0.02, 51), selective=True,
#                   np.linspace(0.4, .6, 51), selective=False,
#                   np.linspace(0.45, 0.52, 51), selective=False,
                        repeat_pulse=1, generate=True, postseq = None, update=True)
    efr.measure_keysight()

    
if 0: # FT1
    from single_qubit import FT1measurement
    #ft1times = np.zeros(len(range(20)))
    for i in range(1):
        ft1 = FT1measurement.FT1Measurement(qubit_info, ef_info, np.linspace(0, 100e3, 101))
        ft1.measure_keysight()
        #ft1times[i] = ft1.analyze()
        #plt.close()
    bla

if 0: # EFT2
    from single_qubit import EFT2measurement

    eft2 = EFT2measurement.EFT2Measurement(qubit_info, ef_info, np.linspace(0e3, 15e3, 161),
                                           detune=0.7e6, 
                                           double_freq=True, generate=True, seq=None)
    eft2.measure_keysight()
    bla

