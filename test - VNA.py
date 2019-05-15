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

#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
#VNA = mclient.instruments['VNA']


Yoko = mclient.instruments['Yoko']
#print 'OK1'
#if 0: #get single trace from VNA
#    from scripts.single_cavity import VNA_single_trace
##    print 'OK2'
#    VNA.do_enable_averaging(True)
#    VNA.set_averaging_trigger(1)
#    VNA.set_trigger_source('internal')
#    VNA.set_average_factor(200)
#    ro = VNA_single_trace.SingleTrace(freqs = np.linspace(10e9, 13e9, 1601), use_async = True)# if use async is False, it simply takes data, and with asnyc, it will set freq to your requst region, wait till finishes the measurement, and get the data.
##    print 'ok3'
#    ro.measure()
##    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
##    print 'ok5'
#    plt.show()
#    bla 
#    
    
if 0: #sweep voltage Yoko and get 2D plot
    from scripts.single_cavity import VNA_sweep_yoko 
    VNA.set_timeout(400000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    ro = VNA_sweep_yoko.Sweep_YOKO(volts = np.linspace(4.5,5.7,101), freqs = np.linspace(8e9, 9e9, 1601), average_factor =5, fig_name ='YIG in Drilled Cavity, Take 1')
    ro.measure()
    pl.show()
    bla
    
if 0: #sweep current Yoko and get 2D plot
    from scripts.single_cavity import VNA_current_sweep_yoko 
    Yoko.do_set_output_state(0)
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    ro = VNA_current_sweep_yoko.Current_Sweep_YOKO(currents = np.linspace(0,0.1,11), freqs = np.linspace(8.0e9, 9.0e9, 1601),
                                                   average_factor =1, avelimit = 1,if_bandwidth = 1000, Sij =['S12'],fig_name ='test',comment = 'with Yoko, and VNA data')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla

if 0: #get single trace from VNA, for long meaasurements
    from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(11.8e9, 12.2e9, 1601), average_factor = 40, avelimit = 2, fit_S12 = 0, fit_S11 =1)

#    print 'ok3'
    ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
    pl.show()
    bla 

if 1: #get single trace from VNA, withoout waiting, just take screenshot and fit it.
    from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
    freqs = VNA.do_get_xaxis()
    ro = VNA_single_trace_V2.SingleTraceNoAsync(freqs, fit_S12 = 0, fit_S11 =1)

    ro.measure()

    pl.show()
    bla