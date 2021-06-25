import matplotlib
matplotlib.interactive(True)
import mclient
reload(mclient)
import numpy as np
import matplotlib.pyplot as pl
from pulseseq import sequencer, pulselib
import matplotlib as mpl
from matplotlib import gridspec
#from t1t2_plotting import smart_T1_delays
import math as math
import datetime
import time
import os
#mpl.rcParams['figure.figsize']=[5,3.5]
#mpl.rcParams['axes.color_cycle'] = ['b', 'g', 'r', 'c', 'm', 'k']
VNA = mclient.instruments['VNA']
#Magnet = mclient.instruments['Magnet']

#Yoko = mclient.instruments['Yoko']
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

if 0: #sweep field and get 2D plot
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
    
    a = [0]
    a[0] = np.linspace(-0.01,0.01,41)
#    a[1] = np.linspace(0.1,0,101)
#    a[2] = np.linspace(0,-0.1,101)
#    a[3] = np.linspace(-0.1,0,101)
    for i in range(len(a)):
        
    #    a= np.log10(a)*10
    #    a[0] = -11
        ro = Magnet_sweep_VNA.Magnet_Sweep_VNA(fields = a[i], freqs = np.linspace(10.8e9, 10.814e9, 101),
                                                       average_factor =10, avelimit =10,if_bandwidth = 100, Sij =['S21'],fig_name ='field sweep',comment = 'demag test')
        #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
        ro.measure()
        pl.show()
    bla
    
if 0: #sweep power and get 2D plot

#    time.sleep(300)
    from scripts.single_cavity import power_sweep_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    VNA.set_power(-40)
#    drive_brick = mclient.instruments['SC_qubit']
#    drive_brick.do_set_power(0)
#    drive_brick.set_frequency(8.333e9)
#    drive_brick.set_rf_on(False)
    a = np.linspace(-40,10,6)
#    a = np.linspace(-10,10,21)
#    a = np.linspace(-85,5,10)
#    a = np.linspace(-80,-70,2)
#    a= np.log10(a)*10
#    a[0] = -11
    average_factor = np.ceil(np.power(10, -a/10 -2)) + 9
#    average_factor = np.zeros(len(a)) + 10
    print (np.sum(average_factor)*1.6 + len(a)*10)/3600
    ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, 
                                         freqs = np.linspace(10.7e9, 10.9e9, 1601),
#                                         freqs = np.linspace(7.018e9, 7.021e9, 51),
                                         average_factor = average_factor, avelimit =10,if_bandwidth = 1000, Sij =['S21'],
                                        fig_name ='S31 power sweep 0T ',comment = '', sweep_SC_qubit = False)
    
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()


    
#    a = np.linspace(-85,5,10)
##    a = np.linspace(-80,-70,2)
##    a= np.log10(a)*10
##    a[0] = -11
#    average_factor = np.ceil(np.power(10, -a/10 -4.5)) + 9
##    average_factor = np.zeros(len(a)) + 10
#    print (np.sum(average_factor)*2 + len(a)*10)/3600
#    ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, 
#                                         freqs = np.linspace(10.794e9, 10.8e9, 201),
##                                         freqs = np.linspace(7.018e9, 7.021e9, 51),
#                                         average_factor = average_factor, avelimit =10,if_bandwidth = 100, Sij =['S21'],
#                                        fig_name ='S31 cavity power sweep 0.03T ',comment = '', sweep_SC_qubit = False)
#    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
#    ro.measure()
#    pl.show() 
#
#
#    
#
#    a = np.linspace(-65,5,8)
##    a = np.linspace(-80,-70,2)
##    a= np.log10(a)*10
##    a[0] = -11
#    average_factor = np.ceil(np.power(10, -a/10 -3)) + 9
##    average_factor = np.zeros(len(a)) + 10
#    print (np.sum(average_factor)*1.6 + len(a)*10)/3600
#    ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, 
#                                         freqs = np.linspace(10.65e9, 10.85e9, 1601),
##                                         freqs = np.linspace(7.018e9, 7.021e9, 51),
#                                         average_factor = average_factor, avelimit =10,if_bandwidth = 1000, Sij =['S21'],
#                                        fig_name ='S31 cavity power sweep 0.03T ',comment = '', sweep_SC_qubit = False)
#    
#    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
#    ro.measure()
#    pl.show()    
    
    bla

if 0: #sweep power and changing frequency
    from scripts.single_cavity import power_sweep_varies_freq_VNA
    
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    VNA.set_power(0)
    a = np.linspace(0,1,3)
    center_freq = 2* a + 7
    center_freq = center_freq * 1e9
#    a= np.log10(a)*10
    print (9000 * len(a) *1.6 + len(a)*10)/3600.0
    ro = power_sweep_varies_freq_VNA.Power_Sweep_Varies_freq_VNA(powers = a, center_freqs = center_freq, span = 2e9, VNA_points = 1601,
                                                   average_factor =9, avelimit =10,if_bandwidth = 1000, Sij =['S21'],fig_name ='0dB S31 sweep ',comment = 'fine sweep for -60dB S31')

    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla

if 0: #sweep brick frequency and get 2D plot

    from scripts.single_cavity import frequency_sweep_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    VNA.set_power(-38)
    drive_brick = mclient.instruments['SC_qubit']
    drive_brick.do_set_power(10)
    a = np.linspace(8.33e9, 8.338e9,9)
#    a= np.log10(a)*10
#    a[0] = -11
    average_factor = np.zeros(len(a)) + 10
#    average_factor [0] = 100
    print (np.sum(average_factor)*2 + len(a)*10)/3600
    ro = frequency_sweep_VNA.Freq_Sweep_VNA(drive_brick = drive_brick,sweep_freqs = a, freqs = np.linspace(10.8e9, 10.81e9, 201),
                                            average_factor = average_factor, avelimit =20,if_bandwidth = 100, Sij =['S21'],
                                            fig_name ='S32 drive freq sweep at -0.05T ',comment = '')
    #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
    ro.measure()
    pl.show()
    bla

if 0: #demag
    fields = [ -0.04, 0.03, -0.025, 0.02, -0.015, 0.01, -0.008, 0.006, -0.004, 0.0025, -0.001,0.0005,-0.00025, 0]
    fields = -np.asarray(fields)
    #Magnet.do_set_PSwitch(1)
    #time.sleep(35)
    #fields = np.linspace(0,-0.05,26)
    for field in fields:
        print(field)
        if abs(field)>0.01:
            Magnet.do_set_field(0)
            time.sleep(400)
    
        
    #    Magnet.do_set_PSwitch(1)
    #    time.sleep(35)
    #            
        Magnet.do_set_field(field)
        time.sleep(300)
    
if 0: #get repeated single trace from VNA, for long meaasurements
    repeat = 20
    powerlist = np.linspace(-25,-10,2)
    average_factor = 300
    print len(powerlist)*(5 + repeat*1.6*average_factor)/float(3600)
    fieldlist = [-0.05]
    for field in fieldlist:
        if float(Magnet.do_get_PSwitch()) == 1:
        
            Magnet.do_set_field(field)
            time.sleep(100)
    
            
            Magnet.do_set_PSwitch(0)
            time.sleep(320)
            try:
                while not float(Magnet.do_get_PSwitch()) == 0:
        
                    objsh.helper.backend.main_loop(100)
        
            except:
                print 'error in setting persistent mode'
            
        elif abs(float(Magnet.do_get_field()) - field) > 0.0002:
            print 'heat PSwitch first'
            exit
            
        
            
        field0 = Magnet.do_get_field()
        print 'field at %sT'%(float(field0))
            
        for ipower, power in enumerate(powerlist):
            drive_brick = mclient.instruments['SC_qubit']
            drive_brick.do_set_power(power)
            drive_brick.set_frequency(8.3336e9)
            if ipower == 0:
                drive_brick.set_rf_on(False)
            else:                
                drive_brick.set_rf_on(True)
            figname = '%sT overlay %sdB'%(field,power)
            time.sleep(10)    
            for i in range(repeat):
        #        Magnet.do_set_PSwitch(1)
        #        time.sleep(40)
        #        Magnet.do_set_PSwitch(0)
        #        time.sleep(350)
                from scripts.single_cavity import VNA_single_trace_V2
            #    print 'OK2'
                VNA.set_s_param('21')
                VNA.set_timeout(40000)
                VNA.do_enable_averaging(True)
                VNA.set_averaging_trigger(1)
                VNA.set_trigger_source('internal')
                VNA.set_power(-38)
    
                if i==0:
                    fig = None
                
                if fig is None:        
                    fig = pl.figure(figname)
                    label = '%sdB'%(power)
                    gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
                    fig.add_subplot(gs[0])
                    fig.add_subplot(gs[1])
            
                ro = VNA_single_trace_V2.SingleTrace(
            #            freqs = np.linspace(7.865e9, 7.875e9, 101), 
            #            freqs = np.linspace(8.032e9, 8.042e9, 101),
            #            freqs = np.linspace(8.123e9, 8.133e9, 101),
                        freqs = np.linspace(10.78e9, 10.83e9, 1601),
            #            freqs = np.linspace(7.394e9, 7.404e9, 101),
                        average_factor =average_factor, 
                        avelimit = 10, 
                        if_bandwidth = 1000, 
                        fit_S12 = 1, fit_S11 =0, title = '%sdB'%(power))
            
            
            
            
            
            #    print 'ok3'
                ro.measure()
            #    print 'ok4'
            #    a=ro.ampdata
            #    b= ro.freqdata
            #    print 'ok5'
                pl.show()
                pl.close()
                
                fig = pl.figure(figname)
                freqs = ro.freqdata[0,:]
                datas = ro.realdata[0,:] + 1j*ro.imagdata[0,:] 
                datas_scatter = np.average(datas)
                datasdB = 20*np.log10(datas)
        #        fig.axes[0].scatter(i,datasdB)
                fig.axes[0].plot(freqs/float(1e9), datasdB )
                
            
                pl.xlabel('freq(GHz)')
                pl.ylabel('dB')
                pl.legend()
                fig.axes[1].plot( datas.real, datas.imag,label = label)
            
                pl.xlabel('I')
                pl.ylabel('Q')
                fig.axes[1].set_aspect('equal', 'box')
                pl.legend()
        Magnet.do_set_PSwitch(1)
        time.sleep(35)
        
        try:
            while not float(Magnet.do_get_PSwitch()) == 1:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in getting out of persistent mode'  
        
    bla 

if 0: #qubit power sweep
    repeat = 1
    powerlist = np.linspace(-25,5,3)
    average_factor = 10
    for ipower, power in enumerate(powerlist):
        drive_brick = mclient.instruments['SC_qubit']
        drive_brick.do_set_power(power)
        drive_brick.set_frequency(8.3336e9)
        if ipower == 0:
            drive_brick.set_rf_on(False)
        else:                
            drive_brick.set_rf_on(True)
        figname = 'overlay %sdB'%(power)
        time.sleep(10)    
        for i in range(repeat):
    #        Magnet.do_set_PSwitch(1)
    #        time.sleep(40)
    #        Magnet.do_set_PSwitch(0)
    #        time.sleep(350)
            from scripts.single_cavity import VNA_single_trace_V2
        #    print 'OK2'
            VNA.set_s_param('21')
            VNA.set_timeout(40000)
            VNA.do_enable_averaging(True)
            VNA.set_averaging_trigger(1)
            VNA.set_trigger_source('internal')
            VNA.set_power(-38)
    
            if i==0:
                fig = None
            
            if fig is None:        
                fig = pl.figure(figname)
                label = '%sdB'%(power)
                gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
                fig.add_subplot(gs[0])
                fig.add_subplot(gs[1])
        
            ro = VNA_single_trace_V2.SingleTrace(
        #            freqs = np.linspace(7.865e9, 7.875e9, 101), 
        #            freqs = np.linspace(8.032e9, 8.042e9, 101),
        #            freqs = np.linspace(8.123e9, 8.133e9, 101),
                    freqs = np.linspace(10.8e9, 10.81e9, 1601),
        #            freqs = np.linspace(7.394e9, 7.404e9, 101),
                    average_factor =average_factor, 
                    avelimit = 10, 
                    if_bandwidth = 1000, 
                    fit_S12 = 1, fit_S11 =0, title = '%sdB'%(power))
        
        
        
        
        
        #    print 'ok3'
            ro.measure()
        #    print 'ok4'
        #    a=ro.ampdata
        #    b= ro.freqdata
        #    print 'ok5'
            pl.show()
            if repeat >2:
                pl.close()
            
            fig = pl.figure(figname)
            freqs = ro.freqdata[0,:]
            datas = ro.realdata[0,:] + 1j*ro.imagdata[0,:] 
            datas_scatter = np.average(datas)
            datasdB = 20*np.log10(datas)
    #        fig.axes[0].scatter(i,datasdB)
            fig.axes[0].plot(freqs/float(1e9), datasdB )
            
        
            pl.xlabel('freq(GHz)')
            pl.ylabel('dB')
            pl.legend()
            fig.axes[1].plot( datas.real, datas.imag,label = label)
        
            pl.xlabel('I')
            pl.ylabel('Q')
            fig.axes[1].set_aspect('equal', 'box')
            pl.legend()



    
if 0: #get single trace from VNA, for long meaasurements
            

    from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
    VNA.set_s_param('21')
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    power = -75
    VNA.set_power(power)
    average_factor = 300
    print (average_factor *2 )/3600.0

#    drive_brick = mclient.instruments['SC_qubit']
#    drive_brick.do_set_power(10)
#    drive_brick.set_frequency(8.3336e9)
#
#    drive_brick.set_rf_on(True)
#    time.sleep(1)

    ro = VNA_single_trace_V2.SingleTrace(
#            freqs = np.linspace(7.865e9, 7.875e9, 101), 
#            freqs = np.linspace(8.032e9, 8.042e9, 101),
#            freqs = np.linspace(8.123e9, 8.133e9, 101),
#            freqs = np.linspace(10.7e9, 11e9, 1601),
            freqs = np.linspace(10.371e9,10.376e9, 201),
#            freqs = np.linspace(10.794e9, 10.8e9, 101),
            average_factor =average_factor, 
            avelimit = 20, 
            if_bandwidth = 100, 
            fit_S12 = 1, fit_S11 =0, title = '%sdB'%(power))

#    print 'ok3'
    ro.measure()
#    
#    power = -85
#    VNA.set_power(power)
#    average_factor = 8000
#    print (average_factor *2 )/3600.0
#    
#    ro = VNA_single_trace_V2.SingleTrace(
##            freqs = np.linspace(7.865e9, 7.875e9, 101), 
##            freqs = np.linspace(8.032e9, 8.042e9, 101),
##            freqs = np.linspace(8.123e9, 8.133e9, 101),
#            freqs = np.linspace(10.89e9, 10.91e9, 201),
##            freqs = np.linspace(7.018e9, 7.021e9, 101),
#            average_factor =average_factor, 
#            avelimit = 20, 
#            if_bandwidth = 100, 
#            fit_S12 = 1, fit_S11 =0, title = '%sdB'%(power))
#    ro.measure()
#
#    power = -70
#    VNA.set_power(power)
#    average_factor = 1000
#    print (average_factor *2 )/3600.0
#
#    ro = VNA_single_trace_V2.SingleTrace(
##            freqs = np.linspace(7.865e9, 7.875e9, 101), 
##            freqs = np.linspace(8.032e9, 8.042e9, 101),
##            freqs = np.linspace(8.123e9, 8.133e9, 101),
#            freqs = np.linspace(10.89e9, 10.91e9, 201),
##            freqs = np.linspace(7.018e9, 7.021e9, 101),
#            average_factor =average_factor, 
#            avelimit = 20, 
#            if_bandwidth = 100, 
#            fit_S12 = 1, fit_S11 =0, title = '%sdB'%(power))
#
##    print 'ok3'
#    ro.measure()
       
    bla 

if 1: #get single trace from VNA, withoout waiting, just take screenshot and fit it.
    from scripts.single_cavity import VNA_single_trace_V2
#    print 'OK2'
    freqs = VNA.do_get_xaxis()
    ro = VNA_single_trace_V2.SingleTraceNoAsync(freqs, fit_S12 = 1 , fit_S11 =0)
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

if 0: #sweep for different frequency range, with and without qubit drive
    from scripts.single_cavity import power_sweep_VNA
    VNA.set_timeout(40000)
    VNA.do_enable_averaging(True)
    VNA.set_averaging_trigger(1)
    VNA.set_trigger_source('internal')
    VNA.set_power(-30)
    drive_brick = mclient.instruments['SC_qubit']
    drive_brick.do_set_power(0)
    drive_brick.set_frequency(8.334e9)


    fieldlist = np.linspace(0,-.05,6)
    PS_Switch_freqs = np.linspace(10.78e9,10.83e9 , 1601)
    for field in fieldlist:
        if float(Magnet.do_get_PSwitch()) == 1:
        
            Magnet.do_set_field(field)
            time.sleep(100)
    
            
            Magnet.do_set_PSwitch(0)    
            from scripts.single_cavity import VNA_single_trace_V2
            ro = VNA_single_trace_V2.SingleTrace(freqs = PS_Switch_freqs, 
                                             average_factor =200, avelimit = 10, if_bandwidth = 1000, fit_S12 = 1, fit_S11 =0)
            ro.measure()
            pl.show()
            pl.close()
            try:
                while not float(Magnet.do_get_PSwitch()) == 0:
        
                    objsh.helper.backend.main_loop(100)
        
            except:
                print 'error in setting persistent mode'
            
        elif abs(float(Magnet.do_get_field()) - field) > 0.0002:
            print 'heat PSwitch first'
            exit
            
        
            
        field0 = Magnet.do_get_field()
        print 'field at %sT'%(float(field0))
        

    
    
        freqs_list = [np.linspace(10.7e9,10.78e9,101), np.linspace(10.78e9,10.83e9,1601),np.linspace(10.83e9,10.9e9,101)]
                     
        
        
        for freqs in freqs_list:
            drive_brick.set_rf_on(True)
            a = np.linspace(-30,0,4)
        #    a= np.log10(a)*10
        #    a[0] = -11
            average_factor = np.ceil(np.power(10, -a/10 +0.6 )) + 9
        #    average_factor [0] = 100
            print (np.sum(average_factor)*1.8 + len(a)*10)/3600
            ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, freqs = freqs,
                                                 average_factor = average_factor, avelimit =40,if_bandwidth = 1000, Sij =['S21'],
                                                 fig_name ='S21 sweep %sT with qubit drive'%(field),comment = '')
            
            #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
            ro.measure()
            pl.show()
            
            drive_brick.set_rf_on(False)
            
            ro = power_sweep_VNA.Power_Sweep_VNA(powers = a, freqs = freqs,average_factor = average_factor, avelimit =40,
                                                 if_bandwidth = 1000, Sij =['S21'],fig_name ='S21 sweep %sT without qubit drive'%(field),comment = '')
            
            #we can take all 4 S params data at the same time when VNA is calibrated, if not, we can only take the data with same output ports at the same time. 
            ro.measure()
            pl.show()
    #    if not field == fieldlist[-1]:
        
        
        
        Magnet.do_set_PSwitch(1)
        from scripts.single_cavity import VNA_single_trace_V2
        ro = VNA_single_trace_V2.SingleTrace(freqs = PS_Switch_freqs, 
                                         average_factor =20, avelimit = 10, if_bandwidth = 1000, fit_S12 = 0, fit_S11 =0)
        ro.measure()
        pl.show()
        pl.close()
        
        try:
            while not float(Magnet.do_get_PSwitch()) == 1:
    
                objsh.helper.backend.main_loop(100)
    
        except:
            print 'error in getting out of persistent mode'        
    
    bla