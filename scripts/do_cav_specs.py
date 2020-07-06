# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 12:24:45 2019

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
Magnet = mclient.instruments['Magnet']
f= open("C:\Users\Wang_Lab\Documents\yingying\%s.txt"%(time.strftime('%Y%m%d_%H%M%S', time.localtime())),"w+")
fields = np.linspace(0.049,-0.05,100)
for field in fields:
    f.write('\nfield : %s---------------------%s---------'%(field, time.strftime('%Y%m%d_%H%M%S', time.localtime())))
    if float(Magnet.do_get_PSwitch())==1:
        
        Magnet.do_set_field(field)
        time.sleep(10)
        Magnet.do_set_PSwitch(0)
        
        time.sleep(350)
    
    qubit_info = mclient.get_qubit_info('qubit1ge')
    qubit2_info = mclient.get_qubit_info('qubit2ge')
    from single_cavity import rocavspec_qubitge
    freq_ranges = [10e6]
    n=len(freq_ranges)
    diff_c_e1 = np.zeros(n)
    diff_c_e2 = np.zeros(n)
    diff_c_g1 = np.zeros(n)
    diff_c_g2 = np.zeros(n)
    diff_c_off1 = np.zeros(n)
    diff_c_off2 = np.zeros(n)
    diff_c_sub1 = np.zeros(n)
    diff_c_sub2 = np.zeros(n)
    diff_a_e1 = np.zeros(n)
    diff_a_e2 = np.zeros(n)
    diff_a_g1 = np.zeros(n)
    diff_a_g2 = np.zeros(n)
    diff_a_off1 = np.zeros(n)
    diff_a_off2 = np.zeros(n)
    diff_a_sub1 = np.zeros(n)
    diff_a_sub2 = np.zeros(n)
    for i, freq_range in enumerate(freq_ranges):
        rofreq = 10.935e9
    #    freq_range = 5e6
        qubit_source = mclient.instruments['SC_qubit2']
        ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit2_info, np.linspace(6, 10, 1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=True,seq=None)#,extra_info=[ef2_info])
        ro.measure()  
        ea_on = ro.ampedata[0]
        ep_on = ro.phaseedata[0]
        e_on = ea_on * np.exp(1j*(ep_on/180 * np.pi))
        ea_off = ro.ampgdata[0]
        ep_off = ro.phasegdata[0]
        e_off = ea_off * np.exp(1j*(ep_off/180 * np.pi))
        
        
        
        ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit2_info, np.linspace(6, 10, 1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=False,seq=None)#,extra_info=[ef2_info])
        ro.measure()  
        ga_on = ro.ampedata[0]
        gp_on = ro.phaseedata[0]
        g_on = ga_on * np.exp(1j*(gp_on/180 * np.pi))
        ga_off = ro.ampgdata[0]
        gp_off = ro.phasegdata[0]
        g_off = ga_off * np.exp(1j*(gp_off/180 * np.pi))    
        
        f.write('\n')
        f.write('\nQubit 2 freq_range = %s MHz\n'%(freq_range))
        diff_c_e2[i] = np.sum(np.abs(e_on-e_off))/np.sum(np.abs(e_off))
        diff_a_e2[i] = np.sum(ea_on - ea_off)/np.sum(ea_off)
        f.write('diff_c_e  = %s / %s = %s\n'%(np.sum(np.abs(e_on-e_off)),np.sum(np.abs(e_off)), diff_c_e2[i]))
        f.write('diff_a_e  = %s / %s = %s\n'%(np.sum(ea_on - ea_off),np.sum(ea_off), diff_a_e2[i]))    
        
        diff_c_g2[i] = np.sum(np.abs(g_on-g_off))/np.sum(np.abs(g_off))
        diff_a_g2[i] = np.sum(ga_on - ga_off)/np.sum(ga_off)
        f.write('diff_c_g  = %s / %s = %s\n'%(np.sum(np.abs(g_on-g_off)),np.sum(np.abs(g_off)), diff_c_g2[i]))
        f.write('diff_a_g  = %s / %s = %s\n'%(np.sum(ga_on - ga_off),np.sum(ga_off), diff_a_g2[i]))    
        
        diff_c_off2[i] = np.sum(np.abs(e_off-g_off))/np.sum(np.abs(g_off))
        diff_a_off2[i] = np.sum(ea_off - ga_off)/np.sum(ga_off)
        f.write('diff_c_off  = %s / %s = %s\n'%(np.sum(np.abs(e_off-g_off)),np.sum(np.abs(g_off)), diff_c_off2[i]))
        f.write('diff_a_off  = %s / %s = %s\n'%(np.sum(ea_off - ga_off),np.sum(ga_off), diff_a_off2[i]))
        
        diff_c_sub2[i] = np.sum(np.abs((e_on-e_off)-(g_on-g_off)))/np.sum(np.abs(g_off))
        diff_a_sub2[i] = np.sum((ea_on-ea_off) - (ga_on-ga_off))/np.sum(ga_off)
        f.write('diff_c_sub  = %s / %s = %s\n'%(np.sum(np.abs((e_on-e_off)-(g_on-g_off))),np.sum(np.abs(g_off)), diff_c_sub2[i]))
        f.write('diff_a_sub  = %s / %s = %s\n'%(np.sum((ea_on-ea_off) - (ga_on-ga_off)), np.sum(ga_off),diff_a_sub2[i]))
        
        while(i == 0 and diff_c_g2[i] > 1):
            Magnet.do_set_PSwitch(1)
            time.sleep(60)
            Magnet.do_set_field(field)
            time.sleep(10)
            Magnet.do_set_PSwitch(0)
        
            time.sleep(350)
            qubit_source = mclient.instruments['SC_qubit2']
            ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit2_info, np.linspace(6, 10, 1),
                                                     np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                     qubit_pulse=True,seq=None)#,extra_info=[ef2_info])
            ro.measure()  
            ea_on = ro.ampedata[0]
            ep_on = ro.phaseedata[0]
            e_on = ea_on * np.exp(1j*(ep_on/180 * np.pi))
            ea_off = ro.ampgdata[0]
            ep_off = ro.phasegdata[0]
            e_off = ea_off * np.exp(1j*(ep_off/180 * np.pi))
            
            
            
            ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit2_info, np.linspace(6, 10, 1),
                                                     np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                     qubit_pulse=False,seq=None)#,extra_info=[ef2_info])
            ro.measure()  
            ga_on = ro.ampedata[0]
            gp_on = ro.phaseedata[0]
            g_on = ga_on * np.exp(1j*(gp_on/180 * np.pi))
            ga_off = ro.ampgdata[0]
            gp_off = ro.phasegdata[0]
            g_off = ga_off * np.exp(1j*(gp_off/180 * np.pi))    
            
            f.write('\n')
            f.write('\n Repeat Qubit 2\n')
            diff_c_e2[i] = np.sum(np.abs(e_on-e_off))/np.sum(np.abs(e_off))
            diff_a_e2[i] = np.sum(ea_on - ea_off)/np.sum(ea_off)
            f.write('diff_c_e  = %s / %s = %s\n'%(np.sum(np.abs(e_on-e_off)),np.sum(np.abs(e_off)), diff_c_e2[i]))
            f.write('diff_a_e  = %s / %s = %s\n'%(np.sum(ea_on - ea_off),np.sum(ea_off), diff_a_e2[i]))    
            
            diff_c_g2[i] = np.sum(np.abs(g_on-g_off))/np.sum(np.abs(g_off))
            diff_a_g2[i] = np.sum(ga_on - ga_off)/np.sum(ga_off)
            f.write('diff_c_g  = %s / %s = %s\n'%(np.sum(np.abs(g_on-g_off)),np.sum(np.abs(g_off)), diff_c_g2[i]))
            f.write('diff_a_g  = %s / %s = %s\n'%(np.sum(ga_on - ga_off),np.sum(ga_off), diff_a_g2[i]))    
            
            diff_c_off2[i] = np.sum(np.abs(e_off-g_off))/np.sum(np.abs(g_off))
            diff_a_off2[i] = np.sum(ea_off - ga_off)/np.sum(ga_off)
            f.write('diff_c_off  = %s / %s = %s\n'%(np.sum(np.abs(e_off-g_off)),np.sum(np.abs(g_off)), diff_c_off2[i]))
            f.write('diff_a_off  = %s / %s = %s\n'%(np.sum(ea_off - ga_off),np.sum(ga_off), diff_a_off2[i]))
            
            diff_c_sub2[i] = np.sum(np.abs((e_on-e_off)-(g_on-g_off)))/np.sum(np.abs(g_off))
            diff_a_sub2[i] = np.sum((ea_on-ea_off) - (ga_on-ga_off))/np.sum(ga_off)
            f.write('diff_c_sub  = %s / %s = %s\n'%(np.sum(np.abs((e_on-e_off)-(g_on-g_off))),np.sum(np.abs(g_off)), diff_c_sub2[i]))
            f.write('diff_a_sub  = %s / %s = %s\n'%(np.sum((ea_on-ea_off) - (ga_on-ga_off)), np.sum(ga_off),diff_a_sub2[i]))
        
        
        qubit_source = mclient.instruments['qubitbrick']
    #    freq_range = 5e6
        ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit_info, np.linspace(6, 10, 1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=True,seq=None)#,extra_info=[ef2_info])
        ro.measure()  
        ea_on = ro.ampedata[0]
        ep_on = ro.phaseedata[0]
        e_on = ea_on * np.exp(1j*(ep_on/180 * np.pi))
        ea_off = ro.ampgdata[0]
        ep_off = ro.phasegdata[0]
        e_off = ea_off * np.exp(1j*(ep_off/180 * np.pi))
        
        
        ro = rocavspec_qubitge.ROCavSpec_Qubitge(qubit_source, qubit_info, np.linspace(6, 10, 1),
                                                 np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                                 qubit_pulse=False,seq=None)#,extra_info=[ef2_info])
        ro.measure()  
        ga_on = ro.ampedata[0]
        gp_on = ro.phaseedata[0]
        g_on = ga_on * np.exp(1j*(gp_on/180 * np.pi))
        ga_off = ro.ampgdata[0]
        gp_off = ro.phasegdata[0]
        g_off = ga_off * np.exp(1j*(gp_off/180 * np.pi))    
        
        f.write('\n')
        f.write('\nQubit 1\n')
        diff_c_e1[i] = np.sum(np.abs(e_on-e_off))/np.sum(np.abs(e_off))
        diff_a_e1[i] = np.sum(ea_on - ea_off)/np.sum(ea_off)
        f.write('diff_c_e  = %s / %s = %s\n'%(np.sum(np.abs(e_on-e_off)),np.sum(np.abs(e_off)), diff_c_e1[i]))
        f.write('diff_a_e  = %s / %s = %s\n'%(np.sum(ea_on - ea_off),np.sum(ea_off), diff_a_e1[i]))    
        
        diff_c_g1[i] = np.sum(np.abs(g_on-g_off))/np.sum(np.abs(g_off))
        diff_a_g1[i] = np.sum(ga_on - ga_off)/np.sum(ga_off)
        f.write('diff_c_g  = %s / %s = %s\n'%(np.sum(np.abs(g_on-g_off)),np.sum(np.abs(g_off)), diff_c_g1[i]))
        f.write('diff_a_g  = %s / %s = %s\n'%(np.sum(ga_on - ga_off),np.sum(ga_off), diff_a_g1[i]))    
        
        diff_c_off1[i] = np.sum(np.abs(e_off-g_off))/np.sum(np.abs(g_off))
        diff_a_off1[i] = np.sum(ea_off - ga_off)/np.sum(ga_off)
        f.write('diff_c_off  = %s / %s = %s\n'%(np.sum(np.abs(e_off-g_off)),np.sum(np.abs(g_off)), diff_c_off1[i]))
        f.write('diff_a_off  = %s / %s = %s\n'%(np.sum(ea_off - ga_off),np.sum(ga_off), diff_a_off1[i]))
        
        diff_c_sub1[i] = np.sum(np.abs((e_on-e_off)-(g_on-g_off)))/np.sum(np.abs(g_off))
        diff_a_sub1[i] = np.sum((ea_on-ea_off) - (ga_on-ga_off))/np.sum(ga_off)
        f.write('diff_c_sub  = %s / %s = %s\n'%(np.sum(np.abs((e_on-e_off)-(g_on-g_off))),np.sum(np.abs(g_off)), diff_c_sub1[i]))
        f.write('diff_a_sub  = %s / %s = %s\n'%(np.sum((ea_on-ea_off) - (ga_on-ga_off)), np.sum(ga_off),diff_a_sub1[i]))
        
    print('field : %s------------------------------'%(field))
    
    for i , freq_range in enumerate(freq_ranges):
        print('\nQubit 2\n')
        print('freq_range %sMHz'%(freq_range/1e6))
        print('diff_c_e  = %s'%( diff_c_e2[i]))
        print('diff_a_e  = %s'%( diff_a_e2[i]))    
        
    
        print('diff_c_g = %s'%( diff_c_g2[i]))
        print('diff_a_g = %s'%( diff_a_g2[i]))    
        
    
        print('diff_c_off = %s'%( diff_c_off2[i]))
        print('diff_a_off = %s'%( diff_a_off2[i]))
        
    
        print('diff_c_sub  %s'%(diff_c_sub2[i]))
        print('diff_a_sub %s'%(diff_a_sub2[i]))
        
    for i , freq_range in enumerate(freq_ranges):
        print('\nQubit 1\n')
        print('freq_range %sMHz'%(freq_range/1e6))
        print('diff_c_e  = %s'%( diff_c_e1[i]))
        print('diff_a_e  = %s'%( diff_a_e1[i]))    
        
    
        print('diff_c_g = %s'%( diff_c_g1[i]))
        print('diff_a_g = %s'%( diff_a_g1[i]))    
        
    
        print('diff_c_off = %s'%( diff_c_off1[i]))
        print('diff_a_off = %s'%( diff_a_off1[i]))
        
    
        print('diff_c_sub  %s'%(diff_c_sub1[i]))
        print('diff_a_sub %s'%(diff_a_sub1[i]))
        
    Magnet.do_set_PSwitch(1)
    time.sleep(60)
    

        
f.close()