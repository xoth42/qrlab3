# -*- coding: utf-8 -*-
"""
Created on Mon Feb 08 15:58:43 2021

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
from matplotlib import gridspec



qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
qubit2_info = mclient.get_qubit_info('qubit2ge')
ef2_info = mclient.get_qubit_info('qubit2ef')
ef2_info_set = mclient.instruments['qubit2ef']
mixer_info1 = mclient.get_qubit_info('mixer_info1')
SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
SS_mixer_info2 = mclient.get_qubit_info('SS_mixer_info2')
mixer_info2 = mclient.get_qubit_info('mixer_info2')
mixer_info1_set = mclient.instruments['mixer_info1']
mixer_info2_set = mclient.instruments['mixer_info2']
SS_mixer_info1_set = mclient.instruments['SS_mixer_info1']
SS_mixer_info2_set = mclient.instruments['SS_mixer_info2']
readout_IQ = mclient.instruments['readout_IQ']
readout_info = mclient.get_readout_info('readout')
readout = mclient.instruments['readout']

os.chdir(r'C:/qrlab/scripts')

import time
import objectsharer as objsh
import re

Magnet = mclient.instruments['Magnet']



#time.sleep(300)
dig = mclient.instruments['dig']
#dig.do_set_naverages(10000)
def gaussian(params, x, data):
    return data - params['amp'] * np.exp(-.5 * ((x - params['mean']) / params['std'])**2)
#if 0: #demag
##    avgs = [3000]
#    fields = [-.04,0.03, -0.025, 0.02, -0.015, 0.01,-0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
##    fields = - np.asarray(fields)
#    #Magnet.do_set_PSwitch(1)
#    #time.sleep(35)
#    #fields = np.linspace(0,-0.05,26)
#    for field in fields:
#        print(field)
#        if abs(field)>0.01:
#            Magnet.do_set_field(0)
#            time.sleep(400)
#    
#        
#    #    Magnet.do_set_PSwitch(1)
#    #    time.sleep(35)
#    #            
#        Magnet.do_set_field(field)
#        time.sleep(300)

#for field in [-.019,-.019,-.019,-.02,-.02,-.02, -.021,-.021,-.021]:  
for field in [-0.021,-0.021,-0.021]:
    if 1:
        
        if float(Magnet.do_get_PSwitch()) == 1:
        
            Magnet.do_set_field(field)
            time.sleep(100)
    
            
            Magnet.do_set_PSwitch(0)    
            time.sleep(350)
            try:
                while not float(Magnet.do_get_PSwitch()) == 0:
        
                    objsh.helper.backend.main_loop(100)
        
            except:
                print 'error in setting persistent mode'
            
#        elif abs(float(Magnet.do_get_field()) - field) > 0.0002:
        else:
            Magnet.do_set_PSwitch(1)    
            time.sleep(40)
            Magnet.do_set_field(field)
            time.sleep(100)
    
            
            Magnet.do_set_PSwitch(0)    
            time.sleep(350)
            try:
                while not float(Magnet.do_get_PSwitch()) == 0:
        
                    objsh.helper.backend.main_loop(100)
        
            except:
                print 'error in setting persistent mode'        
            
        
            
        field0 = Magnet.do_get_field()
        print 'field at %sT'%(float(field0))
    
    from single_cavity import rocavspectroscopy_keysight_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cavity_infoA.rotate_selective(np.pi, 0)])
#    seq = sequencer.Sequence([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0), ef2_info.rotate(np.pi, 0)])
#    Yoko.do_set_current(-0.00175)
    delay = 20
    postseq = sequencer.Delay(delay)
#    postseq = None
    amps = np.linspace(0.1,.1,1)
    amps2 = np.linspace(0.1,.1,1)
    dig.do_set_naverages(10000)
    for i in range(len(amps)):
        mixer1_amp = amps[i]
        mixer2_amp =0# amps[i]
        
        mixer_info1_set.set_pi_amp(mixer1_amp)
        mixer_info2_set.set_pi_amp(mixer2_amp)
        
        rofreq = 10.807e9
        freq_range = 7e6
        mixer_info1_set.set_w(1000)
        mixer_info2_set.set_w(1000)
        dig.set_nsamples(850)
        mixer_info1 = mclient.get_qubit_info('mixer_info1')
        mixer_info2 = mclient.get_qubit_info('mixer_info2')
        ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit_info, mixer_info1, mixer_info2, np.linspace(10,10,1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=False, seq=None, postseq =postseq,)#,extra_info=[ef2_info])
        ro.measure()
        plt.close()
        plt.close()
#        
##        figure_name = 'S31 + S32'
        figure_name = '%s T qubit'%(field)
#        
#        comp_g = ro.ampdata[0] * np.exp(1j * ro.phasedata[0]*np.pi/180)
#        
        plt.figure('amp%s'%(figure_name))
        plt.plot(ro.freqs,ro.ampdata[0],label = ' g, amp = %s, delay = %s ns'%(amps[i], delay))
        plt.legend()
        plt.figure('phase%s'%(figure_name))
        plt.plot(ro.freqs,ro.phasedata[0],label = 'g, amp = %s'%(amps[i]))
        plt.legend()
        
        
        ro = rocavspectroscopy_keysight_mixer.ROCavSpectroscopy_keysight_mixer(qubit2_info, mixer_info1, mixer_info2, np.linspace(10,10,1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=True, seq=None, postseq = postseq)#,extra_info=[ef2_info])
        ro.measure()
        plt.close()
        plt.close()
        comp_e1 = ro.ampdata[0] * np.exp(1j * ro.phasedata[0]*np.pi/180)
        plt.figure('amp%s'%(figure_name))
        plt.plot(ro.freqs,ro.ampdata[0],label = 'qubit 2 in e')
        plt.plot(ro.freqs, np.abs(comp_e1 - comp_g), label = 'diff g and qubit1 e')
        plt.legend()
        plt.figure('phase%s'%(figure_name))
        plt.plot(ro.freqs,ro.phasedata[0],label = 'qubit 2 in e')
        plt.legend()
    
    #####for qubit 1 readout
    if 1:   #qubit1 readout setting
        
        ro_freq = 10.8074e9
        power = 10
        readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
        readout_info.rfsource1.set_power(power)
    #    readout_info.rfsource2.set_frequency(ro_freq+50e6)
        deltaf = 10.811e9 - ro_freq + mixer_info1.deltaf
        SS_mixer_info1_set.set_deltaf(deltaf)
        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
        
        mixer_info1_set.set_pi_amp(0.4)
        mixer_info2_set.set_pi_amp(0)
        mixer_info1_set.set_w(300)
        mixer_info2_set.set_w(300)
        dig.set_nsamples(500)
        mixer_info1 = mclient.get_qubit_info('mixer_info1')
        mixer_info2 = mclient.get_qubit_info('mixer_info2')
        
        from scripts.single_qubit import rabi_mixer
        tr_e = rabi_mixer.Rabi_mixer(qubit2_info, mixer_info1, mixer_info2,[qubit_info.pi_amp,], histogram=True, title='|e>',
    #                   readout = 'readout_IQ',
                                     )
        tr_e.measure_keysight()
        tr_g = rabi_mixer.Rabi_mixer(qubit2_info,mixer_info1, mixer_info2, [0.001,], histogram=True, title='|g>',
    #                                 readout = 'readout_IQ',
                       )
        tr_g.measure_keysight()
        tr = rabi_mixer.Rabi_mixer(qubit2_info, mixer_info1, mixer_info2,[qubit_info.pi_amp/2,], histogram=True, title='|g>+|e>',
    #                               readout = 'readout_IQ',
                       )
        tr.measure_keysight()
        plt.close()
        plt.close()
        plt.close()
        
        e_data = tr_e.shot_data[:]
        g_data = tr_g.shot_data[:]
        
        #find blob centers
        g_average = np.average(g_data)
        e_average = np.average(e_data)
        readout.set_IQg(g_average)
        readout.set_IQe(e_average)
        readout_IQ.set_IQg(g_average)
        readout_IQ.set_IQe(e_average)
        readout_info = mclient.get_readout_info('readout')    
        midpoint = np.average([g_average, e_average])
    
        #setup plots
        lim = 400
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
        
        
        print('SNR = ', (means[1] - means[0]) / (stds[0] + stds[1])/2)
    
    dig.do_set_naverages(10000)
    
    
    if 1: #ssb with stark shift with mixer with gaussian fit
        from single_qubit import stark_shift_with_mixer
    #    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
        phase1 =0
        pi_amps = [0,0.3,0.6, 0.7]
        repeat_ssb = 1
        for j in range(len(pi_amps)):
            SS_mixer_info1_set.set_pi_amp(pi_amps[j])
    
            SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
    #    for j in range(len(delays)):
            for i in range(repeat_ssb):        
        #        RObrick.do_set_power(i)
                seq = sequencer.Trigger(600)
                post_seq = sequencer.Delay(150)
                spec = stark_shift_with_mixer.Stark_shift_with_mixer(qubit_info, mixer_info1,mixer_info2, SS_mixer_info1, SS_mixer_info2,
                                                                     phase1, np.linspace(-50e6, 10e6,101), seq=seq, plot_seqs=False, postseq = post_seq,
                                                                     proj_func='projection')#, readout = 'readout_IQ')
                spec.measure_keysight()
                plt.close()
                shift = spec.center
    
    if 1:    #photon ramsey
        from single_qubit import photon_ramsey_test
    #    delay = np.linspace(130,260,6)
        SS_mixer_info1_set.set_pi_amp_selective(0.4)
    
        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')    
        delay = [200]
        points = [101]
        repeat = 10
        seq_num = 3
        data = np.zeros([len(points),len(delay),seq_num])
        data_q = np.zeros([len(points),len(delay),seq_num])
        labels = ['phase 0','phase pi','averages phase']
    #    freq = np.zeros([4,repeat])
        for k in range(len(points)):
            for j in range(len(delay)): 
                freq = np.zeros([seq_num,repeat])
                freq_q = np.zeros([seq_num,repeat])
                for i in range(repeat):
                    t2 = photon_ramsey_test.Photon_Ramsey_Test(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                                     np.linspace(0, 0.001e3*(points[k]-1),points[k]), detune=60e6, 
                                                                     delay = delay[j], generate=True, fix_phi0 = 1.8,qubit_pulse = False,
                                                                     seq=None, postseq=None, proj_func='projection', plot_seqs =False,
    #                                                                 readout = 'readout_IQ',
                                                                     ) #extra_info=[qubit2_info])
                    t2.measure_keysight()
                    if repeat * len(delay)* len(points) >5:
                        
                        plt.close()
                    for m in range(seq_num):
                        freq[m][i] = t2.fit_params[m]['freq'].value
                    t2 = photon_ramsey_test.Photon_Ramsey_Test(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                                     np.linspace(0, 0.001e3*(points[k]-1),points[k]), detune=60e6, 
                                                                     delay = delay[j], generate=True, fix_phi0 = 1.8,qubit_pulse = True,
                                                                     seq=None, postseq=None, proj_func='projection', plot_seqs =False,
    #                                                                 readout = 'readout_IQ',
                                                                     ) #extra_info=[qubit2_info])
                    t2.measure_keysight()
                    if repeat * len(delay)* len(points) >5:
                        
                        plt.close()
                    for m in range(seq_num):
                        freq_q[m][i] = t2.fit_params[m]['freq'].value
    #            labels = ['without qubit','without qubit, delay %s'%(delay[j]), 'with qubit','with qubit, delay %s'%(delay[j])]
    #            labels = ['without qubit, delay %s'%(delay[j]),'with qubit, delay %s'%(delay[j])]
            #    labels = ['without qubit, delay %s'%(delay),'without qubit', 'with qubit','with qubit, delay %s'%(delay)]
            #    labels = ['without qubit', 'with qubit','without qubit, delay %s'%(delay),'with qubit, delay %s'%(delay)]
            #    labels = ['with qubit', 'without qubit','with qubit, delay %s'%(delay),'without qubit, delay %s'%(delay)]
                if repeat >1:
                    plt.figure()
                    plt.title('delay = %s, points = %s'%(delay[j],points[k]))
                    for l in range(seq_num):
                        plt.plot(freq[l]*1000, label = labels[l] + ' w/o qubit, ave freq = %.3f +/- %.3f MHz'%(
                                np.average(freq[l]*1000), np.std(freq[l])/np.sqrt(len(freq[l]))*1000))
                        plt.plot(freq_q[l]*1000, label = labels[l] + ' w/ qubit, ave freq = %.3f +/- %.3f MHz'%(
                                np.average(freq_q[l]*1000), np.std(freq_q[l])/np.sqrt(len(freq_q[l]))*1000))
                    plt.legend()
                    fn = os.path.join(r'C:\_Data', 'images/%s_cavity_df.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
                    fdir = os.path.split(fn)[0]
                    if not os.path.isdir(fdir):
                        os.makedirs(fdir)
                    kwargs = dict()
                    plt.savefig(fn, **kwargs) 
    #                plt.figure()
    #                plt.title('freq_shifts, delay = %s, points = %s'%(delay[j],points[k]))
    #                for l in range(4):
    #                    plt.plot(freq[l]*1000 - freq[0] * 1000, label = labels[l])
    #                plt.legend()
                for p in range(seq_num):
                    data[k][j][p]=np.average(freq[p])
                    data_q[k][j][p]=np.average(freq_q[p])
        if len(points) > 1:
            
            for u in range(len(delay)):
    #            labels_ = ['without qubit','without qubit, delay', 'with qubit','with qubit, delay']
    #            labels_ = ['without qubit, delay','with qubit, delay']
                plt.figure()
                plt.title('delay = %s'%(delay[u]))#%(points[u]))
                for t in range(seq_num):
                    plt.plot(points,data.transpose()[t][0],label = labels[t]+' w/o qubit')
                    plt.plot(points,data_q.transpose()[t][0],label = labels[t]+ ' w/ qubit')
                plt.legend()
                fn = os.path.join(r'C:\_Data', 'images/%s_cavity_df.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
                fdir = os.path.split(fn)[0]
                if not os.path.isdir(fdir):
                    os.makedirs(fdir)
                kwargs = dict()
                plt.savefig(fn, **kwargs)
        if len(delay) > 1:
            
            for u in range(len(points)):
    #            labels_ = ['without qubit','without qubit, delay', 'with qubit','with qubit, delay']
    #            labels_ = ['without qubit, delay','with qubit, delay']
                plt.figure()
                plt.title('pts = %s'%(points[u]))
                for t in range(seq_num):
                    plt.plot(delay,data[u].transpose()[t],label = labels[t] + ' w/o qubit')
                    plt.plot(delay,data_q[u].transpose()[t],label = labels[t]+' w/ qubit')
                plt.legend() 
                fn = os.path.join(r'C:\_Data', 'images/%s_cavity_df_vs_amp.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
                fdir = os.path.split(fn)[0]
                if not os.path.isdir(fdir):
                    os.makedirs(fdir)
                kwargs = dict()
                plt.savefig(fn, **kwargs)
        
