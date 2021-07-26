# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 15:21:44 2018

@author: WangLab
"""

import matplotlib.pyplot as pl
import numpy as np
from mclient import instruments

#Yoko = instruments.create('Yoko','Yokogawa_7651',address='GPIB1::3::INSTR')


#AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='AWG1', clock=1e9, refsrc='EXT', reffreq=10e6)


#VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
#Yoko = instruments.create('Yoko','Yokogawa_GS200',address='GPIB1::11::INSTR')
VNA = instruments['VNA']

m=0
while m<10:
    time.sleep(6)
    data = VNA.do_get_data()
    axis = VNA.do_get_xaxis()
    
    axis = axis[:,None].T
    trace = np.concatenate([axis,data]).T
    np.savetxt(r'C:\qrlab-3\FMR\0mT_1mm_trace\%s.txt'%(m) , trace , delimiter=",")# saves data
    m=m+1