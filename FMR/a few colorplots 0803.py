# -*- coding: utf-8 -*-
"""
Created on Sat Aug 03 18:11:13 2019

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
from pulseseq import sequencer, pulselib
import matplotlib as mpl
#from t1t2_plotting import smart_T1_delays
import math as math
import datetime
import time
import os
import re
#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
VNA = mclient.instruments['VNA']

from scripts.single_cavity import power_sweep_VNA
date = datetime.datetime.now()
filename = '9mk_%s_%s_%s'%(date.hour,date.minute,date.second)

filenames = []
PowerList = np.linspace(-45,10,12)





# 110 lower freq --------------------------------------------------------------------------------------------------------------
num = np.ceil(np.power(10, -PowerList/10 -1)) + 9
print (np.sum(num)*10 )/3600
for ipower, power  in enumerate(PowerList):
    VNA.set_power(power)

    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    a = np.linspace(0,num[ipower]-1,num[ipower])
    average_factor = 0*a +1
#    average_factor = np.ceil(np.power(10, -a/10 -1 ))
#    average_factor [0] = 100

    ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, freqs = np.linspace(8.247e9, 8.297e9, 101),
                                                   average_factor = average_factor, avelimit =1,if_bandwidth =10, Sij =['S21'],fig_name ='power = %sdB '%(power),comment = '')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", ro.data.get_fullname())
    filenames.append(int(digit[-1]))
    pl.show()

    
  
    
#110 higher freq------------------------------------------------------------------------------------------------------------------------------  
    



#num = 15
#for power in PowerList:
#    VNA.set_power(power)
#
#    VNA.set_timeout(40000)
#    VNA.do_enable_averaging(True)
#    VNA.set_averaging_trigger(1)
#    VNA.set_trigger_source('internal')
#    a = np.linspace(0,num-1,num)
#    average_factor = 0*a +1
##    average_factor = np.ceil(np.power(10, -a/10 -1 ))
##    average_factor [0] = 100
#
#    ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, freqs = np.linspace(7.8992e9, 7.9052e9, 101),
#                                                   average_factor = average_factor, avelimit =1,if_bandwidth =10, Sij =['S21'],fig_name ='110 higher freq power = %sdB '%(power),comment = '')
#    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
#    ro.measure()
#    digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", ro.data.get_fullname())
#    filenames.append(int(digit[-1]))
#    pl.show()

# mode 220 -----------------------------------------------------------------------------------------------------------------------------    




# ---------------------------------------------------------------------------------------------------------------------------------------------------    
np.savetxt(r'C:\Users\WangLab\Documents\yingying\0612cooldown\%s'%(filename),  filenames)
