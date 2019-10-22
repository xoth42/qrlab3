# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:06:37 2019

@author: Wang_Lab
"""

import mclient
Yoko = mclient.instruments['Yoko']
import matplotlib.pyplot as plt


if 0:
    current =2.1319e-3
    
    for i in range(100):
        Yoko.do_set_current(current + i*0.01e-5)
        time.sleep(1)  


if 1:
    from mclient import instruments
    VNA = instruments.create('VNA', 'Agilent_E5071C', address='GPIB1::17::INSTR')
    data = VNA.do_get_data()
    axis = VNA.do_get_xaxis()
    
    import numpy as np
    import matplotlib.pyplot as pl
    plt.figure()
    plt.plot(axis, data[0])
    pl.title('%f %s' %(data[0,338], 'dB'))


