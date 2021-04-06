# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 20:07:25 2019

@author: WangLab
"""
import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
import time
import objectsharer as objsh
import re

VNA = mclient.instruments['VNA']
Magnet = mclient.instruments['Magnet']

VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

if 1: #demag
    from scripts.single_cavity import VNA_single_trace_V2
    fields = [-0.04,0.03,-0.025,0.02, -0.015, 0.01, -0.008, 0.006, -0.004, 0.0025, -0.001,0.0005,-0.00025, 0]
#    fields = -np.asarray(fields)
    #Magnet.do_set_PSwitch(1)
    #time.sleep(35)
    #fields = np.linspace(0,-0.05,26)
    for field in fields:
        print(field)
        if abs(field)>0.01:
            Magnet.do_set_field(0)
            time.sleep(400)
    
        
    #    Magnet.do_set_PSwitch(1)
    #    time.sleep(35)
    #            
        Magnet.do_set_field(field)
        time.sleep(300)
    #    Magnet.do_set_PSwitch(0)
    #    time.sleep(350)
    #    from scripts.single_cavity import VNA_single_trace_V2
    #    print 'OK2'
        freqs = VNA.do_get_xaxis()
        ro = VNA_single_trace_V2.SingleTraceNoAsync(freqs, fit_S12 = 1, fit_S11 =0)
    
        ro.measure()
    
        pl.show()

filename = '20201106'
filenames = []
fieldlist = np.linspace(0,-0.05,26)
freqs = np.linspace(10.75e9,10.85e9 , 1601)
for field in fieldlist:
    if float(Magnet.do_get_PSwitch()) == 1:
    
        Magnet.do_set_field(field)
        time.sleep(10)

        
        Magnet.do_set_PSwitch(0)    
        from scripts.single_cavity import VNA_single_trace_V2
        ro = VNA_single_trace_V2.SingleTrace(freqs = freqs, 
                                         average_factor =200, avelimit = 10, if_bandwidth = 1000, fit_S12 = 1, fit_S11 =0,title = 'cooldown')
        ro.measure()
        pl.show()
        pl.close()
        try:
            while not float(Magnet.do_get_PSwitch()) == 0:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in setting persistent mode'
        
    elif abs(float(Magnet.do_get_field()) - field) > 0.0002:
        print 'heat PSwitch first'
        exit
        
    
        
    field0 = Magnet.do_get_field()
    print 'field at %sT'%(float(field0))
    

    from scripts.single_cavity import power_sweep_VNA

    power = np.linspace(-40,0,5)
    average_factor = np.ceil(np.power(10, -power/10 -1.3)) + 9
    print (np.sum(average_factor)*1.6 + len(power)*10)/3600
    ro = power_sweep_VNA.Power_Sweep_VNA(powers = power, freqs = np.linspace(10.75e9,10.85e9,1601),
                                                   average_factor = average_factor, avelimit = 40,if_bandwidth =1000, Sij =['S21'],fig_name ='S21 power sweep at %sT '%(field),comment = '')
    ro.measure()
    digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", ro.data.get_fullname())
    filenames.append(int(digit[-1]))
    pl.show()
    
    
#    if not field == fieldlist[-1]:
    Magnet.do_set_PSwitch(1)
    from scripts.single_cavity import VNA_single_trace_V2
    ro = VNA_single_trace_V2.SingleTrace(freqs = freqs, 
                                     average_factor =20, avelimit = 10, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0,title = 'warm up')
    ro.measure()
    pl.show()
    pl.close()
    
    try:
        while not float(Magnet.do_get_PSwitch()) == 1:

            objsh.helper.backend.main_loop(100)

    except:
        print 'error in getting out of persistent mode'
    
#np.savetxt(r'C:\Users\WangLab\Documents\yingying\20200626cooldown\%s'%(filename),  filenames)   



    
#fields = [0.04, -0.03, 0.02, -0.015, 0.01, -0.005, 0.0025, -0.001,0.0005,-0.00025, 0]
##fields = -np.asarray(fields)
##Magnet.do_set_PSwitch(1)
##time.sleep(35)
##fields = np.linspace(0,-0.05,26)
#for field in fields:
#    print(field)
#    if abs(field)>0.01:
#        Magnet.do_set_field(0)
#        time.sleep(600)
#
#    
##    Magnet.do_set_PSwitch(1)
##    time.sleep(35)
##            
#    Magnet.do_set_field(field)
#    time.sleep(600)
##    Magnet.do_set_PSwitch(0)
##    time.sleep(350)
#    from scripts.single_cavity import VNA_single_trace_V2
##    print 'OK2'
#    freqs = VNA.do_get_xaxis()
#    ro = VNA_single_trace_V2.SingleTraceNoAsync(freqs, fit_S12 = 1, fit_S11 =0)
#
#    ro.measure()
#
#    pl.show()
'''
filenames = []
fieldlist = np.linspace(-0.01, -0.04,16)
freqs = np.linspace(10.75e9,10.85e9 , 201)
for field in fieldlist:
    if float(Magnet.do_get_PSwitch()) == 1:
    
        Magnet.do_set_field(field)
        time.sleep(10)

        
        Magnet.do_set_PSwitch(0)    
        from scripts.single_cavity import VNA_single_trace_V2
        ro = VNA_single_trace_V2.SingleTrace(freqs = freqs, 
                                         average_factor =200, avelimit = 10, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
        ro.measure()
        pl.show()
        pl.close()
        try:
            while not float(Magnet.do_get_PSwitch()) == 0:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in setting persistent mode'
        
    elif abs(float(Magnet.do_get_field()) - field) > 0.0002:
        print 'heat PSwitch first'
        exit
        
    
        
    field0 = Magnet.do_get_field()
    print 'field at %sT'%(float(field0))
    

    from scripts.single_cavity import power_sweep_VNA

    power = np.linspace(-30,0,4)
    average_factor = np.ceil(np.power(10, -power/10 + 0.5)) + 9
    print (np.sum(average_factor)*0.2 + len(power)*10)/3600
    ro = power_sweep_VNA.Power_Sweep_VNA(powers = power, freqs = freqs,
                                                   average_factor = average_factor, avelimit = 50,if_bandwidth =1000, Sij =['S21'],fig_name ='S21 power sweep at %sT'%(field),comment = '')
    ro.measure()
    digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", ro.data.get_fullname())
    filenames.append(int(digit[-1]))
    pl.show()
    
    
    if not field == fieldlist[-1]:
        Magnet.do_set_PSwitch(1)
        from scripts.single_cavity import VNA_single_trace_V2
        ro = VNA_single_trace_V2.SingleTrace(freqs = freqs, 
                                         average_factor =20, avelimit = 10, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
        ro.measure()
        pl.show()
        pl.close()
        
        try:
            while not float(Magnet.do_get_PSwitch()) == 1:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in getting out of persistent mode'
            
'''