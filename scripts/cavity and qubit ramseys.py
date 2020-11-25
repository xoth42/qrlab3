# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 22:47:39 2020

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

readout_info = mclient.get_readout_info('readout')
readout = mclient.instruments['readout']

os.chdir(r'C:/qrlab/scripts')



field = -0.03

#time.sleep(300)

dig.do_set_naverages(5000)




#####for qubit 1 readout
if 1:
    
    ro_freq = 10.821e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    deltaf = 10.8223e9 - ro_freq - 100e6
    SS_mixer_info1_set.set_deltaf(deltaf)
    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
    
    mixer_info1_set.set_pi_amp(.4)
    mixer_info2_set.set_pi_amp(.4)
    mixer_info1 = mclient.get_qubit_info('mixer_info1')
    mixer_info2 = mclient.get_qubit_info('mixer_info2')
    
if 1:
    from single_qubit import photon_ramsey_test
#    delay = np.linspace(130,260,6)
    
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
                                                                 delay = delay[j], generate=True, fix_phi0 = -1.8,qubit_pulse = False,
                                                                 seq=None, postseq=None, proj_func='amplitude', plot_seqs =False) #extra_info=[qubit2_info])
                t2.measure_keysight()
                if repeat * len(delay)* len(points) >5:
                    
                    plt.close()
                for m in range(seq_num):
                    freq[m][i] = t2.fit_params[m]['freq'].value
                t2 = photon_ramsey_test.Photon_Ramsey_Test(qubit_info, qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                                 np.linspace(0, 0.001e3*(points[k]-1),points[k]), detune=60e6, 
                                                                 delay = delay[j], generate=True, fix_phi0 = -1.8,qubit_pulse = True,
                                                                 seq=None, postseq=None, proj_func='amplitude', plot_seqs =False) #extra_info=[qubit2_info])
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
if 1: #ssb with stark shift with mixer with gaussian fit
    from single_qubit import stark_shift_with_mixer
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
    phase1 =0
    pi_amps = [0,0.3,0.6]
    repeat_ssb = 1
    for j in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[j])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
#    for j in range(len(delays)):
        for i in range(repeat_ssb):        
    #        RObrick.do_set_power(i)
            seq = sequencer.Trigger(600)
            post_seq = sequencer.Delay(500)
            spec = stark_shift_with_mixer.Stark_shift_with_mixer(qubit_info, mixer_info1,mixer_info2, SS_mixer_info1, SS_mixer_info2,
                                                                 phase1, np.linspace(-50e6, 10e6,101), seq=seq, plot_seqs=False, postseq = post_seq,
                                                                 proj_func='phase')
            spec.measure_keysight()
            plt.close()
            shift = spec.center




#####for qubit 2 readout

if 1:
    
    ro_freq = 10.824e9
    power = 10
    readout_info.rfsource1.set_frequency(ro_freq - mixer_info1.deltaf)
    readout_info.rfsource1.set_power(power)
    readout_info.rfsource2.set_frequency(ro_freq+50e6)
    deltaf = 10.8223e9 - ro_freq - 100e6
    SS_mixer_info1_set.set_deltaf(deltaf)
    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')




if 1:
    
    
    
    dig.do_set_naverages(10000)
    from single_qubit import ramsey_measurement
#    seq = sequencer.Join([sequencer.Trigger(250), qubit2_info.rotate(np.pi, 0)])
    post_seq = sequencer.Delay(500)
#    A_E = []
#    A = []
    SS_mixer_info1_set.set_pi_amp(0.0000001)

    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
    t2 = ramsey_measurement.Ramsey_Measurement_mixer(qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                 np.linspace(0, 0.24e3, 121), detune=40e6,  
                                                 double_freq=False, generate=True, 
                                                 seq=None, postseq=post_seq, proj_func='phase', plot_seqs = False) #extra_info=[qubit2_info])

    t2.measure_keysight()
    
    pi_amps = np.linspace(0.6, 0.6,1)
    repeat = 10
    df_i = np.zeros([len(pi_amps),repeat])
    df_f = np.zeros([len(pi_amps),repeat])
    df_ave = np.zeros([len(pi_amps),repeat])
    tau_i = np.zeros([len(pi_amps),repeat])
    tau_f = np.zeros([len(pi_amps),repeat])
    tau_ave = np.zeros([len(pi_amps),repeat])
    
    for i in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[i])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
        
        for j in range(repeat):
            
       
#            t2 = ramsey_measurement.Ramsey_Measurement_mixer(qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
#                                                         np.linspace(0, 0.12e3, 121), detune=80e6, echotype = 'HANN', 
#                                                         necho = 1, double_freq=False, generate=True, 
#                                                         seq=None, postseq=post_seq, proj_func='phase', plot_seqs = False) #extra_info=[qubit2_info])
#            t2.measure_keysight()
#            A_E.append(t2.fit_params)
            t2 = ramsey_measurement.Ramsey_Measurement_mixer(qubit2_info, SS_mixer_info1, mixer_info1,mixer_info2, 
                                                         np.linspace(0, 0.24e3, 121), detune=40e6,  
                                                         double_freq=False, generate=True, 
                                                         seq=None, postseq=post_seq, proj_func='phase', plot_seqs = False) #extra_info=[qubit2_info])

            t2.measure_keysight()
            plt.close()
#            A.append(t2.fit_params)
            xs = t2.delays
            df_i[i][j] = t2.fit_params['freq'].value*1e6 + t2.fit_params['A']*1e6*np.exp(-xs[0]*t2.fit_params['slope'])
            df_f[i][j] = t2.fit_params['freq'].value*1e6 + t2.fit_params['A']*1e6*np.exp(-xs[-1]*t2.fit_params['slope'])
            df_ave[i][j] = np.average(t2.fit_params['freq'].value*1e6 + t2.fit_params['A']*1e6*np.exp(-xs*t2.fit_params['slope']))
            tau_i[i][j] = 0.001/((1/t2.fit_params['tau'].value) + t2.fit_params['A2'].value*np.exp(-xs[0]*t2.fit_params['slope'].value/2))
            tau_f[i][j] = 0.001/((1/t2.fit_params['tau'].value) + t2.fit_params['A2'].value*np.exp(-xs[-1]*t2.fit_params['slope'].value/2))
            tau_ave[i][j] = 0.001/np.average((1/t2.fit_params['tau'].value) + t2.fit_params['A2'].value*np.exp(-xs*t2.fit_params['slope'].value/2))

        if repeat >1:
            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(df_i[i], label = ' df_initial, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df_i[i]), np.std(df_i[i])/np.sqrt(len(df_i[i]))))
            plt.plot(df_f[i], label = ' df_final, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df_f[i]), np.std(df_f[i])/np.sqrt(len(df_f[i]))))
            plt.plot(df_ave[i], label = ' df_average, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df_ave[i]), np.std(df_ave[i])/np.sqrt(len(df_ave[i]))))
            plt.legend()
            fn = os.path.join(r'C:\_Data', 'images/%s_qubit_df.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
            fdir = os.path.split(fn)[0]
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            kwargs = dict()
            plt.savefig(fn, **kwargs)
            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(tau_i[i], label = ' tau_initial, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau_i[i]), np.std(tau_i[i])/np.sqrt(len(tau_i[i]))))
            plt.plot(tau_f[i], label = ' tau_final, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau_f[i]), np.std(tau_f[i])/np.sqrt(len(tau_f[i]))))
            plt.plot(tau_ave[i], label = ' tau_average, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau_ave[i]), np.std(tau_ave[i])/np.sqrt(len(tau_ave[i]))))
            plt.legend()
            fn = os.path.join(r'C:\_Data', 'images/%s_tau.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
            fdir = os.path.split(fn)[0]
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            kwargs = dict()
            plt.savefig(fn, **kwargs)

    if len(pi_amps) > 1:

        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(df_i, axis = 1),label = 'df_initial')
        plt.plot(pi_amps,np.mean(df_f, axis = 1),label = 'df_final')
        plt.plot(pi_amps,np.mean(df_ave, axis = 1),label = 'df_average')
        plt.legend()   
        fn = os.path.join(r'C:\_Data', 'images/%s_qubit_df_vs_amp.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        plt.savefig(fn, **kwargs)
        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(tau_i, axis = 1),label = 'tau_initial')
        plt.plot(pi_amps,np.mean(tau_f, axis = 1),label = 'tau_final')
        plt.plot(pi_amps,np.mean(tau_ave, axis = 1),label = 'tau_average')
        plt.legend() 
        fn = os.path.join(r'C:\_Data', 'images/%s_tau_vs_amp.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        plt.savefig(fn, **kwargs)




if 1:
    from single_qubit import cw_ramsey_mixer
#    SS_mixer_info1_set.set_pi_amp(0.000000001)
#
#    SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
#    
#    
#    
#    t2 = cw_ramsey_mixer.CW_Ramsey_Mixer(qubit2_info,  SS_mixer_info1, mixer_info1,mixer_info2, 
#                                                 np.linspace(0, 0.5e3, 101), detune = 20e6, 
#                                                 generate=True, fix_phi0 =None,qubit_pulse = False,double_freq = False,
#                                                 seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
#    t2.measure_keysight()   
    dig.do_set_naverages(10000)

    pi_amps = np.linspace(0,0.1,11)
    repeat = 1
    df = np.zeros([len(pi_amps),repeat])
    tau = np.zeros([len(pi_amps),repeat])
    for i in range(len(pi_amps)):
        SS_mixer_info1_set.set_pi_amp(pi_amps[i])

        SS_mixer_info1 = mclient.get_qubit_info('SS_mixer_info1')
        
        
        for j in range(repeat):
            t2 = cw_ramsey_mixer.CW_Ramsey_Mixer(qubit2_info,  SS_mixer_info1, mixer_info1,mixer_info2, 
                                                         np.linspace(0, 0.5e3, 101), detune = 20e6, 
                                                         generate=True, fix_phi0 =None,qubit_pulse = False,double_freq = False,
                                                         seq=None, postseq=None, proj_func='phase', plot_seqs =False) #extra_info=[qubit2_info])
            t2.measure_keysight() 

            df[i][j] = t2.fit_params[2]['freq'].value*1e6 

            tau[i][j] =(t2.fit_params[2]['tau'].value)/1000
            if len(pi_amps) * repeat >5:
                plt.close()
        if repeat >1:
            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(df[i], label = ' df, ave freq = %.3f +/- %.3f kHz'%(
                    np.average(df[i]), np.std(df[i])/np.sqrt(len(df[i]))))
            plt.legend()

            plt.figure()
            plt.title('pi_amp = %s'%(pi_amps[i]))
            plt.plot(tau[i], label = ' tau, ave tau = %.3f +/- %.3f us'%(
                    np.average(tau[i]), np.std(tau[i])/np.sqrt(len(tau[i]))))

            plt.legend()

    if len(pi_amps) > 1:

        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(df, axis = 1),label = 'df')
        plt.legend()   
        plt.figure()
        plt.title('field = %s'%(field))#%(points[u]))
        plt.plot(pi_amps,np.mean(tau, axis = 1),label = 'tau')
        
        
        plt.legend()
        
        




