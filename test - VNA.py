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
#    Yoko.do_set_output_state(0)
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    ro = VNA_current_sweep_yoko.Current_Sweep_VNA(currents = np.linspace(0.45,0.6,201), freqs = np.linspace(7.5e9, 9e9, 1601),
                                                   average_factor =1, avelimit = 1,if_bandwidth = 1000, Sij =['S21'],fig_name ='test',comment = 'with Yoko, and VNA data')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla

    
if 0: #sweep current and changing frequency
    from scripts.single_cavity import current_sweep_varies_freq_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    a = np.linspace(0.5225, 0.5235,11)
    center_freq = 13.3* (a - a[0]) + 8.22
    center_freq = center_freq * 1e9

    ro = current_sweep_varies_freq_VNA.Current_Sweep_Varies_freq_VNA(currents = a, center_freqs = center_freq, span = 20e6, VNA_points = 1601,
                                                   average_factor =1, avelimit =1,if_bandwidth =50000, Sij =['S21'],fig_name ='current sweep for 550 ',comment = 'yig cavity measurement')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla

if 0: #sweep sets of field ranges and get 2D plot
    from scripts.single_cavity import Magnet_sweep_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    
    a = [0,0,0,0]
    a[0] = np.linspace(0,0.1,101)
    a[1] = np.linspace(0.1,0,101)
    a[2] = np.linspace(0,-0.1,101)
    a[3] = np.linspace(-0.1,0,101)
    for i in range(len(a)):
        
    #    a= np.log10(a)*10
    #    a[0] = -11
        ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = a[i], freqs = np.linspace(5.5665e9, 5.5725e9, 101),
                                                       average_factor =10, avelimit =3,if_bandwidth = 10, Sij =['S21'],fig_name ='field sweep',comment = 'qubit in waveguide')
        #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
        ro.measure()
        pl.show()
    bla
    
if 0: #sweep power and get 2D plot
    from scripts.single_cavity import power_sweep_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    a = np.linspace(0,1,101)
#    a= np.log10(a)*10
#    a[0] = -11
    ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, freqs = np.linspace(5.5665e9, 5.5725e9, 101),
                                                   average_factor =10, avelimit =3,if_bandwidth = 10, Sij =['S21'],fig_name ='no pump',comment = 'qubit in waveguide')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla

if 0: #sweep power and changing frequency
    from scripts.single_cavity import power_sweep_varies_freq_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    a = np.linspace(0,1,21)
    center_freq = -0.1739* a + 5.5604
    center_freq = center_freq * 1e9
    a= np.log10(a)*10
    a[0] = -14
    ro = power_sweep_varies_freq_VNA.Power_Sweep_Varies_freq_VNA(powers = a, center_freqs = center_freq, span = 30e6, VNA_points = 401,
                                                   average_factor =500, avelimit =10,if_bandwidth = 100, Sij =['S21'],fig_name ='pump power sweep ',comment = 'power sweep for qubit in waveguide')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla



if 1: #get single trace from VNA, for long meaasurements
    from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')

    ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(7.78e9, 7.82e9, 1601), average_factor = 1, avelimit = 1, fit_S12 = 1, fit_S11 =0)


#    print 'ok3'
    ro.measure()
#    print 'ok4'
#    a=ro.ampdata
#    b= ro.freqdata
#    print 'ok5'
    pl.show()
    bla 


if 0: #get single trace from VNA, withoout waiting, just take screenshot and fit it.
    from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
    freqs = VNA.do_get_xaxis()
    ro = VNA_single_trace_V2.SingleTraceNoAsync(freqs, fit_S12 = 0, fit_S11 =0)

    ro.measure()

    pl.show()
    bla
    
    
    
if 0: #sweep field to 
    from scripts.single_cavity import VNA_single_trace_V2
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')   
    average = 1000
    '''Create all your empty arrays to save fit parameters in'''    
    m_list = np.linspace(0,20,11)
    
    time_of_m = np.zeros(len(m_list))
    kappa_result = np.zeros(len(m_list))
    kappa_err = np.zeros(len(m_list))
    Q_result = np.zeros(len(m_list))

    '''Just helps with bookkeeping later on during data analysis'''
    start_time = list(str(datetime.datetime.now())[:19])
    start_time[13] = '-'
    start_time[16] = '-'
#    magnet = mclient.instruments['Magnet']
    SCqubit = mclient.instruments['SCqubit']
    for i,m in enumerate(m_list):
#        magnet.do_set_field(m)
        SCqubit.set_power(m)
#        time.sleep(5)       
        
    #    print 'OK2'
        time_of_m[i] = int(time.strftime('%H%M%S'))

        print '###############'
        print m,'dB'
        print '##############'
        ro = VNA_single_trace_V2.SingleTrace(freqs = np.linspace(5.42e9, 5.72e9, 401), average_factor = average, avelimit = 10, fit_S12 = 1, fit_S11 =0)

        ro.measure()
        kappa_result[i] = ro.fit_params['kappa_a'].value
#        pl.savefig(save_filepath + 'kappas.png')
        pl.close()
        


    '''More bookkeeping'''
    
    end_time = list(str(datetime.datetime.now())[:19])
    end_time[13] = '-'
    end_time[16] = '-'
    
#    '''These are just showing you how good your fits were for this run'''
#    print('Average percent error on %.0f T1 measurements was %.03f:' %(int(N), np.average(t1_err/t1_result)))
#    print('Average percent error on %.0f T2 measurements was %.03f:' %(int(N), np.average(t2_err/t2_result)))
    
    '''Save the data for later analysis'''
    main_filepath = 'C:/Users/Wang_Lab/Documents/yingying/0418cooldown/field sweep//no_field'
    time_stamp = start_time + list(str(' to ')) + end_time
    save_filepath = main_filepath + ''.join(time_stamp) + '/'
    
    
    if not os.path.exists(save_filepath):
        os.makedirs(save_filepath)
        
    np.savetxt(save_filepath + 'results.txt',
               np.column_stack((m_list,time_of_m, kappa_result, kappa_err, Q_result)),
               header = 
               
               'field,time_of_field, kappa_result, kappa_err, Q_result')
    
    np.savetxt(save_filepath + 'notes.txt', [0],
               header = 
               'm_list = np.linspace(' + str(m_list[0]) +',' + str(m_list[-1]) + ',' + str(len(m_list)) + ')'  +
               ', num_averages = ' + str(average) )
    
    '''Plot the data'''
    pl.figure()
    pl.errorbar(m_list, kappa_result/1000000, yerr = kappa_err/1000000, fmt ='o', label='kappa_tot')
#    pl.xlabel('field(T)')
#    pl.xlabel('different measurement')
    pl.xlabel('drive power')
    pl.ylabel('linewidth(MHz)')
    pl.legend(loc='upper right')
    pl.savefig(save_filepath + 'kappas.png')
    pl.figure()
    pl.scatter(m_list, Q_result, label='total Q')
#    pl.xlabel('field(T)')
#    pl.xlabel('different measurement')
    pl.xlabel('drive power')
    pl.ylabel('Q')
    pl.legend(loc='upper right')
    pl.savefig(save_filepath + 'Qs.png')
    
#    magnet.do_set_field(0)
    bla

