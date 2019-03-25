# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:01:50 2018

@author: Wang_Lab
"""

import matplotlib
matplotlib.interactive(True)

import os
import mclient
import time
import datetime
import numpy as np
#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
VNA = mclient.instruments['VNA']


import matplotlib.pyplot as pl 
pl.figure()
#VNA.do_power_sweep(10, -10, -1)
for i, power in enumerate(np.arange(10,-60,-5)):
    VNA.set_power(power)
    for cf in[10.838,11.303]:  
        VNA.set_center_freq(cf*1e9)
    #    if i != 0:
    #        VNA.set_center_freq(cf)
    #    VNA.set_average_factor(30)
        if power<-40:
            time.sleep(1400)
        elif power<-20:
            time.sleep(600)
        elif power<=-10:
            time.sleep(120)
        else:
            time.sleep(10)
#        yield self.do_get_data()
#VNA.set_power(0)

        date = datetime.datetime.now()
        filename = '%s_%s_%s_%sdB'%(date.hour,date.minute,date.second,power)
        #    filename = 'S12_fridge_220mode_-35dB'
        newpath = r'C:\Users\WangLab\Documents\\12142018 cooldown\\power sweep\\S13 0.021T %sGHz\\%s.txt'%(cf,filename)
        
        if not os.path.exists(os.path.dirname(newpath)):
        
            os.makedirs(os.path.dirname(newpath))
        
        data = VNA.do_get_data()
        axis = VNA.do_get_xaxis()
        
    #    pl.figure()
        if axis[len(axis) - 1] > 10 **9:
            xaxis = axis / float(1000000000)
            pl.xlabel('frequency(GHZ)')
        elif axis[len(axis) - 1] > 10 **6:
            xaxis = axis / float(1000000)
            pl.xlabel('frequency(MHZ)')
    
    
        pl.plot(xaxis, data[0], label = filename)
        
        pl.ylabel('dB')
        #pl.show()
        pl.legend()
        
        axis = axis[:,None].T
        trace = np.concatenate([axis,data]).T
        
        np.savetxt(newpath , trace , delimiter=",") # saves data
        print power, ' dB done'
    #    data=list(data[0])
    #    cf=trace[data.index(max(data))][0]
    #    print cf