# -*- coding: utf-8 -*-
"""
Created on Mon Dec 02 11:59:24 2019

@author: Wang_Lab
"""
import time
Yoko = mclient.instruments['yoko']


ramp_currents = np.linspace(1, 3,201 )


for i in ramp_currents:
    #yoko1.do_set_current(current)
    Yoko.do_set_current(i)
    print(i)
    time.sleep(2)