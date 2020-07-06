# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 15:37:21 2020

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


fieldlist =[ 0.04,-0.03,0.025,-0.02,0.015,-0.01,0.005,-0.0025,0.001,-0.0005,0]

#fieldlist = - np.asarray(fieldlist)
freqs = np.linspace(10.8e9,10.84e9 , 1601)
for field in fieldlist:
    if float(Magnet.do_get_PSwitch()) == 0:
        Magnet.do_set_PSwitch(1)
        time.sleep(35)
        
    if np.abs(field) > 0.1:
        Magnet.do_set_field(0)
        time.sleep(600)
    
    Magnet.do_set_field(field)
    time.sleep(600)
   
    from scripts.single_cavity import VNA_single_trace_V2
    ro = VNA_single_trace_V2.SingleTrace(freqs = freqs, 
                                     average_factor =20, avelimit = 10, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
    ro.measure()
    pl.show()
    pl.close()