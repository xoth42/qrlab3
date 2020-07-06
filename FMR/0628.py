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
#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
VNA = mclient.instruments['VNA']

VNA.set_power(-30)

from scripts.single_cavity import current_sweep_varies_freq_VNA
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

a =  np.linspace(0,19,20)
#    center_freq = 27.74* (a - 0.31) + 8.414
#    center_freq = center_freq * 1e9
center_freq = np.linspace(6.15e9, 11.85e9, 20)
ro = current_sweep_varies_freq_VNA.Current_Sweep_Varies_freq_VNA(currents = a, center_freqs = center_freq, span = 300e6, VNA_points = 1601,
                                               average_factor =10, avelimit =1,if_bandwidth =100, Sij =['S21'],fig_name ='search for qubit -55dB',comment = '')

#we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
ro.measure()
pl.show()

VNA.set_power(-10)

from scripts.single_cavity import current_sweep_varies_freq_VNA
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

a =  np.linspace(0,19,20)
#    center_freq = 27.74* (a - 0.31) + 8.414
#    center_freq = center_freq * 1e9
center_freq = np.linspace(6.15e9, 11.85e9, 20)
ro = current_sweep_varies_freq_VNA.Current_Sweep_Varies_freq_VNA(currents = a, center_freqs = center_freq, span = 300e6, VNA_points = 1601,
                                               average_factor =1, avelimit =1,if_bandwidth =100, Sij =['S21'],fig_name ='search for qubit 0dB',comment = '')

#we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
ro.measure()
pl.show()