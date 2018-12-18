# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 15:21:44 2018

@author: WangLab
"""

import matplotlib.pyplot as pl
import os
import numpy as np
from mclient import instruments
import time

#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
VNA = instruments['VNA']
time.sleep(0.9)
avefac = 100
VNA.set_average_factor(avefac)
VNA.do_enable_averaging()
m=0
while m<10:
    print m

    VNA.set_averaging_trigger(0)
    VNA.set_averaging_trigger(1)
    time.sleep(20)
    data = VNA.do_get_data(fmt='PLOG')#, opc=True, trig_each_avg=True)
#    data = VNA.do_get_data()
    axis = VNA.do_get_xaxis()
    
    axis = axis[:,None].T
    trace = np.concatenate([axis,data]).T
    
    filename = '1020mK\\660 ave\\10MHz V%s '%(m)
#    filename = 'S12_fridge_220mode_-35dB'
    newpath = r'C:\Users\Wang_Lab\Documents\yingying\\11162018cooldown\\%s'%(filename)
    
    if not os.path.exists(os.path.dirname(newpath)):
    
        os.makedirs(os.path.dirname(newpath))
    np.savetxt(newpath , trace , delimiter=",")# saves data
    m=m+1