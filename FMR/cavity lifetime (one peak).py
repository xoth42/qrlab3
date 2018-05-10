import matplotlib.pyplot as plt
import numpy as np
import time
import lmfit
import mclient
import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array
alz = mclient.instruments['alazar']
#Yoko = mclient.instruments['Yoko']
magnet = mclient.instruments['Magnet']
brick3 = mclient.instruments['brick3']
sc2=mclient.instruments['sc2']
def peakdet(x,v, delta):
    maxtab = []        
    mintab = []        
                
    v = asarray(v)                
    if len(v) != len(x):                
        sys.exit('Input vectors v and x must have same length')                
    if not isscalar(delta):                
        sys.exit('Input argument delta must be a scalar')                
    if delta <= 0:                
        sys.exit('Input argument delta must be positive')               
    mn, mx = Inf, -Inf                
    mnpos, mxpos = NaN, NaN                
    lookformax = True                
    for i in arange(len(v)):                
        this = v[i]                
        if this > mx:                
                mx = this                
                mxpos = x[i]                
        if this < mn:                
            mn = this
            mnpos = x[i]                
        if lookformax:                
            if this < mx-delta:                
                maxtab.append((mxpos, mx))               
                mn = this
                mnpos = x[i]                
                lookformax = False                
        else:                
            if this > mn+delta:
                mintab.append((mnpos, mn))                
                mx = this                
                mxpos = x[i]                
                lookformax = True                
    return array(maxtab), array(mintab)
                
for mag in [0]:

    filename = '03202018_0.5mm_-10dB_100mV_range'
    sen = 100 #sensitivity in finding peaks
#    Yoko.do_set_voltage(mag/float(40))
    #Yoko.do_set_voltage(0)
    magnet.magnet.do_set_field(mag)
    if 1:#freq_sweep
#        Yoko.do_set_voltage(mag/float(40))
        start_freq = 8.52e9
        stop_freq = 8.56e9
        num=101
        Amp = []
        I = []
        Q = []
        A = []
        freq_range = np.linspace(start_freq, stop_freq, num)
        brick3.do_set_pulse_on(False)
        time.sleep(2)
        brick3.do_set_frequency(start_freq)
        sc2.do_set_frequency(start_freq+50e6)
        alz.setup_shots(1)
        time.sleep(1)
        buf = alz.take_demod_shots()
        data = buf
        ave = np.average(np.abs(buf))
        Amp.append(ave)
        aveI = np.average(np.real(buf))
        I.append(aveI)
        aveQ = np.average(np.imag(buf))
        Q.append(aveQ)
        A.append(np.sqrt(aveI**2 + aveQ**2))
            
            
        for freq in freq_range[1:num]:
            brick3.do_set_frequency(freq)
            sc2.do_set_frequency(freq+50e6)
            alz.setup_shots(1)
            time.sleep(1)
            buf = alz.take_demod_shots()
            data = np.concatenate([data,buf])
            ave = np.average(np.abs(buf))
            Amp.append(ave)
            aveI = np.average(np.real(buf))
            I.append(aveI)
            aveQ = np.average(np.imag(buf))
            Q.append(aveQ)
            A.append(np.sqrt(aveI**2 + aveQ**2))
            
            
#        Yoko.do_set_voltage(0)    
        plt.figure()
        plt.plot(freq_range, Amp,label=' magnetic field = %s mT \n Amp'%( mag))
        plt.plot(freq_range, I, label = 'I')
        plt.plot(freq_range, Q, label = 'Q')
        plt.plot(freq_range, A, label = 'A from I and Q')
        
        
        if 1: # if we are only measuring one peak
            maxtab = freq_range[np.argmax(A)]
        else:
            maxtab, mintab = peakdet(freq_range,A,sen)
            if len(maxtab) == 0:
                print 'no peak!'
            elif len(maxtab)!=1:               
                plt.scatter(array(maxtab)[:,0], array(maxtab)[:,1], color='blue')        
    #            plt.scatter(array(mintab)[:,0], array(mintab)[:,1], color='red')
    #            for freq in maxtab[:,0]:
    #                i = 1
    #                plt.scatter(freq, 0, lable = 'freq%s = %s GHz'%(i,freq/1e9))
    #                i += 1
                plt.legend()
                print maxtab
            else:
                plt.scatter(array(maxtab)[0][0], array(maxtab)[0][1], color='blue', label='freq = %s GHz'%(maxtab[0][0]/1e9))        
    #            plt.scatter(array(mintab)[0][0], array(mintab)[0][1], color='red')
                print maxtab[0][0]        

            plt.legend()
        
        data1 = np.concatenate([data.real,data.imag])
        np.savetxt(r'alazar_sweep_fridge_%s_%s mT_%s GHz-%s GHz_%s.txt'%(filename,mag,start_freq/float(1e9),stop_freq/float(1e9),num) ,data1, delimiter=",") # saves data
#        np.column_stack([data.real,data.imag])
#==============================================================================
#         plt.figure()
#         x= range(240)
#         plt.plot(x,np.abs(buf)[0])
#==============================================================================
    if 0:    # fitting the modulated data
        start_fitting = 1140
        sleeptime =1
        n=1000# number of average traces
#        Yoko.do_set_voltage(mag/float(40))       
        brick3.do_set_pulse_on(True)
#        Yoko.do_set_voltage(mag/float(40))
        
        def dem_decay(params, x, data):
            est = params['ofs'] + params['amplitude'] * np.exp(-(x - start_fitting) /( 2*params['tau'].value))
            return data - est

#        freq_list = [8.512e9]
#        for freq in freq_list:
    
#        start_freq = 8.423e9
#        stop_freq = 8.428e9
#        num = 1          
#        freq_list = np.linspace(start_freq, stop_freq, num)
#
#        for freq in freq_list:


    
        for freq in maxtab[:,0]:

            
            brick3.do_set_frequency(freq)
            sc2.do_set_frequency(freq+50e6)
            time.sleep(sleeptime)
    
            alz.setup_shots(1)
            buf = alz.take_demod_shots()
            data_decay = buf

    
            amp = np.abs(buf)
            amp = amp[0]
            amp = amp/float(n)
            I = np.real(buf)
            I = I[0]
            I = I / float(n)
            Q = np.imag(buf)
            Q = Q[0]
            Q = Q / float(n)
    
            for i in range(n-1):
#                time.sleep(0.002)
                alz.setup_shots(1)
                buf_new = alz.take_demod_shots()
                data_decay = np.concatenate([data_decay, buf_new])
    
                amp_new = np.abs(buf_new)
                amp_new = amp_new[0]
                
                amp = amp + amp_new/float(n)
                
                
                I_new = np.real(buf_new)
                I_new = I_new[0]
                
                I = I + I_new/float(n)
                Q_new = np.imag(buf_new)
                Q_new = Q_new[0]
                
                Q = Q + Q_new/float(n)
    #            print i
            np.savetxt
            data_decay1 = np.concatenate([data_decay.real,data_decay.imag])
            np.savetxt(r'decay_graph_%s_%s mT_%s GHz_%s.txt'%(filename,mag,freq/float(1e9),n) ,data_decay1, delimiter=",") # saves data   
    
            plt.figure()
            plt.subplot(211)
            plt.title('Demodulated data')
            timex = 20*np.array(range(240))
    #        timex = timex[:,None].T
    #        plt.subplot(211)
    #        plt.plot(timex[0], np.real(buf[0]), label='Iraw')
    #        plt.plot(timex[0], np.imag(buf[0]), label='Qraw ')
#            plt.plot(timex, amp, marker = 's',label='number of averages = %s \n magnetic field = %s mT \n frequency = %s GHz \n sleep time = %s s'%(n, mag, freq/1e9, sleeptime))
            plt.plot(timex, I, label = 'I')
            plt.plot(timex, Q, label = 'Q')
            A = np.sqrt(I**2 +Q**2)
            plt.plot(timex, A, marker = 's', label = 'A from I and Q\n number of averages = %s \n magnetic field = %s mT \n frequency = %s GHz \n'%(n, mag, freq/1e9))            
            
            
            plt.xlabel('time ns')

#==============================================================================
#         def decay(params, x, data, start_fitting):
#             if x < start_fitting:
#                 est = 0
#             elif x < params['start_decay'].value:
#                 est = params['Alpha0']
#             else:
#                 est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
#             return data - est
#             
#         params = lmfit.Parameters()
#         params.add('ofs', value=np.min(amp))
#         params.add('amplitude', value=np.max(amp))
#         params.add('tau', value=40, min=5.0)
#         params.add('start_decay',value=1200, min=start_fitting)
#         result = lmfit.minimize(decay, params, timex, amp, start_fitting)
# #        lmfit.report_fit(params)
# #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
#         lmfit.report_fit(result.params)
# 
# #        fig.axes[0].plot(timex/1e3, -exp_decay(result.params, timex, 0), label='Fit, tau = %.03f us'%(result.params['tau'].value/1000.))
# #        fig.axes[0].legend(loc=0)
# #        fig.axes[0].set_ylabel('Intensity [AU]')
# #        fig.axes[0].set_xlabel('Time [us]')
# #        fig.axes[1].plot(timex, exp_decay(result.params, xs, ys), marker='s')
#==============================================================================

                
            params = lmfit.Parameters()
            params.add('ofs', value=np.min(amp))
            params.add('amplitude', value=np.max(amp))
            params.add('tau', value=40, min=5.0)
            xs = timex[start_fitting/20:240]
            ys = A[start_fitting/20:240]
            result = lmfit.minimize(dem_decay, params, args=(xs, ys))
    #        lmfit.report_fit(params)
    #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
            lmfit.report_fit(result.params)
            plt.plot(xs,ys-dem_decay(result.params, xs,ys), label='Fit, tau = %.03f ns'%(result.params['tau'].value))
            plt.legend()
            plt.subplot(212)
            plt.plot(I,Q)
            plt.xlabel('I')
            plt.ylabel('Q')
            plt.legend()
#Yoko.do_set_voltage(0)
        
if 0:    #fitting the raw data
        start_fitting = 1160
        mag = 300
        freq = 8.4228e9
        Yoko.do_set_voltage(mag/float(40))
        brick3.do_set_pulse_on(False)
        brick3.do_set_frequency(freq)
        sc2.do_set_frequency(freq+50e6)
        time.sleep(1)
        
        n=1# number of average traces
        alz.setup_shots(1)
        buf = alz.take_raw_shots()
        buf = buf/float(n)
        for i in range(n-1):
            time.sleep(0.002)
            alz.setup_shots(1)
            buf_new = alz.take_raw_shots()
            buf = buf + buf_new/float(n)
#            print i
#==============================================================================
#         buf = alz.take_raw_shots()
#         buf = float(buf)
#         for i in range(n-1):
#             time.sleep(0.002)
#             alz.setup_shots(1)
#             buf_new = alz.take_raw_shots()
#             buf = buf + float(buf_new)
# #            print i  
#         
#         buf = buf/float(n)
#==============================================================================
        buf = buf[:4800]
        

        plt.figure()
        plt.title('raw data')
        timex = np.array(range(4800))

        plt.plot(timex, buf, label='number of averages = %s \n magnetic field = %s mT \n frequency = %s GHz'%(n, mag, freq/1e9))
        plt.xlabel('time ns')
        plt.legend()
        
        Yoko.do_set_voltage(0)
        
        def raw_decay(params, x, data):
            est = params['ofs'] + params['amplitude'] * np.exp(-(x - start_fitting) / (2*params['tau'].value)) * np.sin(params['freq']*x + params['phase'])
            return data - est
            
        params = lmfit.Parameters()
        params.add('ofs', value=np.min(buf))
        params.add('amplitude', value=np.max(buf))
        params.add('tau', value=40, min=0)
        params.add('freq', value=2*np.pi*0.05)
        params.add('phase', value=0)
        xs = timex[start_fitting:4800]
        ys = buf[start_fitting:4800]
        result = lmfit.minimize(raw_decay, params, args=(xs, ys))
#        lmfit.report_fit(params)
#        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
        lmfit.report_fit(result.params)
        plt.plot(xs,ys-raw_decay(result.params, xs,ys),marker = 's', label='Fit, tau = %.03f ns'%(result.params['tau'].value))
        plt.legend()