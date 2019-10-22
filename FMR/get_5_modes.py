# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 19:52:28 2019

@author: Wang_Lab
"""


from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
VNA.set_timeout(40000)
VNA.do_enable_averaging(True)
VNA.set_averaging_trigger(1)
VNA.set_trigger_source('internal')

VNA.set_power(0)
ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()


VNA.set_power(-30)
ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =10, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()


VNA.set_power(0)
ro = VNA_single_trace_V2.SingleTrace(
        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()

ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
        freqs = np.linspace(8.032e9, 8.042e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()

ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
        freqs = np.linspace(8.123e9, 8.133e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()

ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
        freqs = np.linspace(8.179e9, 8.189e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()


ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
        freqs = np.linspace(8.035e9, 8.045e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()

ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
        freqs = np.linspace(8.126e9, 8.136e9, 101),
#        freqs = np.linspace(8.179e9, 8.189e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()

ro = VNA_single_trace_V2.SingleTrace(
#        freqs = np.linspace(7.865e9, 7.875e9, 101), 
#        freqs = np.linspace(8.032e9, 8.042e9, 101),
#        freqs = np.linspace(8.123e9, 8.133e9, 101),
        freqs = np.linspace(8.182e9, 8.192e9, 101),
#        freqs = np.linspace(7.394e9, 7.404e9, 101),
        average_factor =1, 
        avelimit = 2, 
        if_bandwidth = 10, 
        fit_S12 = 1, fit_S11 =0)



#    print 'ok3'
ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
pl.show()