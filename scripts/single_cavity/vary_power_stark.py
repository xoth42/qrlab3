# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 16:37:55 2019

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
from measurement import Measurement1D
from lib.math import fit
import objectsharer as objsh
import time
from matplotlib import gridspec

VNA = mclient.instruments['VNA']
SC = mclient.instruments['SC']

VNA.set_timeout(200000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('bus')

start = 8.6455e9
stop = 8.6515e9
points = 201
avg_limit = 3
averages = 50

init_power = 10

VNA.set_start_freq(start)
VNA.set_stop_freq(stop)
VNA.set_points(points)
VNA.set_average_factor(avg_limit)
frequencies = np.linspace(start,stop,points)


SC.do_set_rf_on(True)
SC.do_set_power(init_power)

def measure():
    data = np.zeros(points, dtype = 'complex')
    count = 0
    while count < averages:
        VNA.trigger()
        wait = VNA.opc(async=True)
        try:
            while not wait.is_valid():
                objsh.helper.backend.main_loop(100)
                VNA.set_format('MLOG')
        except:
            print 'error with async'
        
        prev_fmt = VNA.get_format()
        VNA.set_format('REAL')
        ret = VNA.do_get_yaxes()
        reals = ret[0]
        VNA.set_format('IMAG')
        ret = VNA.do_get_yaxes()
        imags = ret[0]
        VNA.set_format(prev_fmt)
        count = count + 1
    return(reals +1j*imags)
    
print(measure())
