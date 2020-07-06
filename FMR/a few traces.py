# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 19:05:27 2019

@author: WangLab
"""
import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl

VNA = mclient.instruments['VNA']



from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')



ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.8273e9, 7.8323e9, 101), 
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()



ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.9226e9, 7.9276e9, 101), 
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()



ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(8.2573e9, 8.2623e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()



ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(8.4205e9, 8.4255e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()


#------------------------------
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.8283e9, 7.8333e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()

ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.9236e9, 7.9286e9, 101), 
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()


ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(8.2583e9, 8.2633e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()


ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(8.4215e9, 8.4265e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()


#-------------------------------
ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.8293e9, 7.8343e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()

ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.9246e9, 7.9296e9, 101), 
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()


ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(8.2593e9, 8.2643e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()


ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(8.4225e9, 8.4275e9, 101),
                                     average_factor =1, avelimit = 1, if_bandwidth = 10, fit_S12 = 1, fit_S11 =0)

ro.measure()
pl.show()
