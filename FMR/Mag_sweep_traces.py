# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 11:45:30 2019

@author: WangLab
"""
import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
import time

VNA = mclient.instruments['VNA']
Magnet = mclient.instruments['Magnet']

#Yoko = mclient.instruments['Yoko']

VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')
from scripts.single_cavity import Magnet_sweep_VNA
VNA.set_power(-10)
field = np.linspace(0,0.04,81)
ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = field, freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                                   average_factor = 8, avelimit =3,if_bandwidth = 1000, Sij =['S21'],fig_name ='S33   -10dB',comment = '')
ro.measure()
pl.show() 

VNA.set_power(-35)
field = np.linspace(0.04,0,81)
ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = field, freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                                   average_factor = 8, avelimit =3,if_bandwidth = 1000, Sij =['S21'],fig_name ='S33     -35dB',comment = '')
ro.measure()
pl.show() 

VNA.set_power(-35)
field = np.linspace(0,-0.03,61)
ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = field, freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                                   average_factor = 8, avelimit =3,if_bandwidth = 1000, Sij =['S21'],fig_name ='S33     -35dB',comment = '')
ro.measure()
pl.show() 


VNA.set_power(-10)
field = np.linspace(-0.03,0,61)
ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = field, freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                                   average_factor = 8, avelimit =3,if_bandwidth = 1000, Sij =['S21'],fig_name ='S33    -10dB',comment = '')
ro.measure()
pl.show() 


VNA.set_power(-10)
field = np.linspace(0,0.02,41)
ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = field, freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                                   average_factor = 8, avelimit =3,if_bandwidth = 1000, Sij =['S21'],fig_name ='S33    -10dB',comment = '')
ro.measure()
pl.show() 


VNA.set_power(-35)
field = np.linspace(0.02,0,41)
ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = field, freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                                   average_factor = 8, avelimit =3,if_bandwidth = 1000, Sij =['S21'],fig_name ='S33    -35dB',comment = '')
ro.measure()
pl.show() 



Magnet.do_set_field(-.01)

time.sleep(1000)


from scripts.single_cavity import VNA_single_trace_V2
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601), 
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.01, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601), 
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.01, power = -10')
pl.legend()
pl.show()

Magnet.do_set_field(.005)

time.sleep(1000)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0.005, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0.005, power = -10')
pl.legend()
pl.show()
Magnet.do_set_field(-.0025)
time.sleep(1000)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601), 
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.0025, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.0025, power = -10')
pl.legend()
pl.show()
Magnet.do_set_field(.00125)
time.sleep(1000)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601), 
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0.00125, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0.00125, power = -10')
pl.legend()
pl.show()
Magnet.do_set_field(-.0006)
time.sleep(600)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -.0006, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601), 
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.0006, power = -10')
pl.legend()
pl.show()
Magnet.do_set_field(.0003)
time.sleep(600)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs =np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field =0.0003, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0.0003, power = -10')
pl.legend()
pl.show()
Magnet.do_set_field(-.0001)
time.sleep(600)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.001, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = -0.001, power = -10')
pl.legend()
pl.show()


Magnet.do_set_field(0)
time.sleep(600)
VNA.set_power(-35)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0, power = -35')
pl.legend()
pl.show()

VNA.set_power(-10)
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(10.925e9, 10.945e9, 1601),
                                     average_factor =8, avelimit = 3, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
ro.measure()
pl.title('field = 0, power = -10')
pl.legend()
pl.show()