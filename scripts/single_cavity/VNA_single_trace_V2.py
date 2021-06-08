import matplotlib
matplotlib.interactive(True)
from measurement import Measurement1D
import matplotlib.pyplot as plt
import numpy as np
#from pulseseq.sequencer import *
#from pulseseq.pulselib import *
#from lib.math import fit
import objectsharer as objsh
import time
import lmfit
from matplotlib import gridspec

import os
import config
import time

#
#plot type 0: amp and phase
#plot type 1: real and imag

limit_for_off = 1

def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(-1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
#    est = np.conjugate(est)
    if np.max(np.abs(y)) < limit_for_off:
        est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
#    
#def S11(params, x, y): #original
#
#    est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
#    return y - abs(est)
##    if np.max(np.abs(y)) < limit_for_off:
##        est = est + params['roff'] + 1j*params['ioff']
##    est = est * np.exp(1j*params['phi'])
##    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
#    

def S11(params, x, y): #ebru modifying temporarily to match with maryland expression

    est = (+1 - params['kappa_1'] / (1j*(x-params['omega_c'])+params['kappa_a']/2))*params['A']
    return y - abs(est)
#    if np.max(np.abs(y)) < limit_for_off:
#        est = est + params['roff'] + 1j*params['ioff']
#    est = est * np.exp(1j*params['phi'])
#    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
        
def analysis(freqdata, realdata, imagdata, fit_S12, fit_S11, figname, title = '', fig=None):
    fn = None
    if fig is None:
        fig = plt.figure()
        gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
        fig.add_subplot(gs[0])
        add_title = fig.add_subplot(gs[1])
        add_title.set_title(title) 
    freqs = freqdata[0,:]
    datas = realdata[0,:] + 1j*imagdata[0,:] 
    datasdB = 20*np.log10(np.abs(datas))
    if fit_S12:
        params = lmfit.Parameters()



        params.add('kappa_prod', value= (np.max(np.abs(datas))*0.5e6)**2.001, min = 0)#,vary = False)
        params.add('omega_c', value=freqs[np.argmax(np.abs(datas))]*1.00002,min = freqs[np.argmax(np.abs(datas))]*0.998, max = freqs[np.argmax(np.abs(datas))] * 1.002)#,vary = False)
        params.add('kappa_a', value=5e6, min = 0)#, max = 4e6)#,vary = False)



        if np.max(np.abs(datas)) < limit_for_off:
            params.add('roff',value = np.real(datas[0]))#,vary = False)
            params.add('ioff',value = np.imag(datas[0]))#, vary = False)
        params.add('phi',value = 1, max = 1.5*np.pi, min = -1.5*np.pi)#,vary = False)
                
    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
        result = lmfit.minimize(S21, params, args=(freqs, datas))
        lmfit.report_fit(result.params)
        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)

        fitdata = np.sqrt(result.params['kappa_prod'].value)/(-1j*(freqs-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )

        if np.max(np.abs(datas)) < limit_for_off:
            fitdata = fitdata + result.params['roff'].value + 1j*result.params['ioff'].value
        fitdata = fitdata * np.exp(1j*result.params['phi'].value)
        fitdatadB = 20*np.log10(np.abs(fitdata))
#    ampdata = 20*np.log10(np.sqrt(realdata[0,:]**2 + imagdata[0,:]**2))
    if fit_S11:
        params = lmfit.Parameters()
        params.add('kappa_1', value=1e+05)
        params.add('omega_c', value=freqs[np.argmin(np.abs(datas))]*1.0001)
        params.add('kappa_a', value=3.0022e+06)
        params.add('A', value=1)
#        params.add('phi',value = 1.5, max = np.pi, min = -np.pi)#,vary = False)
#        if np.max(np.abs(datas)) < limit_for_off:
#            params.add('roff',value = 1e-5)#,vary = False)
#            params.add('ioff',value = 1e-5)#, vary = False)

                
    #    datas = realdata[0,:]+ 1j*imagdata[0,:]    
        result = lmfit.minimize(S11, params, args=(freqs, abs(datas)))
        lmfit.report_fit(result.params)
        print ('total Q: ',result.params['omega_c'].value/result.params['kappa_a'].value)
        print ('coupling Q: ',result.params['omega_c'].value/result.params['kappa_1'].value)
        fitdata = (-1 - result.params['kappa_1'].value / (-1j*(freqs-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value
# * np.exp(1j*result.params['phi'].value)

        fitdatadB = 20*np.log10(np.abs(fitdata))



    fig.axes[0].plot(freqs/float(1e9), datasdB )
#    fig.axes[0].set_title(figname)
    plt.suptitle(figname)
#    plt.title(title)
    if fit_S12 or fit_S11:
        fig.axes[0].plot(freqs/float(1e9), fitdatadB,'--' )
    plt.xlabel('freq(GHz)')
    plt.ylabel('dB')
    

       
#    if plot_type == 1:



    fig.axes[1].plot( datas.real, datas.imag)
#    fig.axes[1].plot( datas.real[0:100], datas.imag[0:100])
    if fit_S12:

        fig.axes[1].plot(fitdata.real,fitdata.imag, '--',label = 'total Q = %s\n kappa_tot = %s\n freq = %sGHz'%(result.params['omega_c'].value/result.params['kappa_a'].value,result.params['kappa_a'].value/1e6, result.params['omega_c'].value/1e9))

    if fit_S11:
        fig.axes[1].plot(fitdata.real,fitdata.imag, '--',label = 'total Q = %s\n couplingQ = %s\n freq = %sGHz'%(result.params['omega_c'].value/result.params['kappa_a'].value, result.params['omega_c'].value/result.params['kappa_1'].value,result.params['omega_c'].value/1e9))
    plt.xlabel('I')
    plt.ylabel('Q') 
    plt.legend()       
#    print datas.real, fitdata.real
    if fn is None:
        fn = os.path.join(config.datadir, 'images/%s_VNA_trace.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
    fdir = os.path.split(fn)[0]
    if not os.path.isdir(fdir):
        os.makedirs(fdir)
    kwargs = dict()
    fig.savefig(fn, **kwargs)
    if fit_S11 or fit_S12:
        return result.params
class SingleTrace(Measurement1D):

    def __init__(self,freqs, average_factor, avelimit, if_bandwidth, fit_S12, fit_S11,title, **kwargs):
        self.freqs =freqs
#        self.meas_info = meas_info
#        self.device_info = device_info
#        plot_type = SPEC
        self.average_factor = average_factor
        self.avelimit = avelimit
        self.if_bandwidth = if_bandwidth
        self.fit_S12 = fit_S12
        self.fit_S11 = fit_S11
        self.title = title
        self.fig = None

        self.fit_params = None


#        self.plot_type = plot_type

        super(SingleTrace, self).__init__(1, **kwargs)
        
        self.figname = self.data.get_fullname()
#        self.data.create_dataset('freqs', data = self.freqs)
        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
        self.realdata = self.data.create_dataset('real', shape=[1,len(self.freqs)])
        self.imagdata = self.data.create_dataset('imaginary', shape=[1,len(self.freqs)])




    def measure(self):
        # Generate and load sequences
#        print 'ok6'
        VNA = self.instruments['VNA']

        VNA.set_start_freq(self.freqs[0])
        VNA.set_stop_freq(self.freqs[-1])
        VNA.set_points(len(self.freqs))
        
#        timelimit = 16 # breaks long time measurement to severals 16 seconds.
#        avelimit = int(timelimit/VNA.get_sweep_time())
#        avelimit = 2
#        if avelimit<1:
#            avelimit = 1
#        if avelimit >999:
#            avelimit = 999
        VNA.set_if_bandwidth(self.if_bandwidth)    
        ave = self.avelimit
        VNA.set_average_factor(ave)
        count = 0
        self.save_settings()
        while count < self.average_factor:
            ave = self.avelimit
            
            if (self.average_factor-count) < self.avelimit:
                ave = self.average_factor-count
                VNA.set_average_factor(ave)
            
            reals = []
            imags = []
    
    
#            VNA.set_trigger_source('internal')
#            VNA.set_average_factor(40)

            VNA.set_trigger_source('BUS')
#            VNA.write('INIT:CONT ON')
    
#            VNA.set_averaging_trigger(1)
            VNA.trigger()
            
            wait = VNA.opc(async=True) # wait for completion
    
#            print 'ok7'
            a=0
            try:
                while not wait.is_valid():
#                    if a % 10 == 0:
#                        print 'async', a 
#                    a= a + 1
                    
#                    time.sleep(0.1)
                    objsh.helper.backend.main_loop(100)
                    VNA.set_format('MLOG')
            except:
                print 'error with async'
#                VNA.set_interrupt(True)
#        '''
    
#            print 'ok8'
            prev_fmt = VNA.get_format()
            freqs = VNA.do_get_xaxis()
            VNA.set_format('REAL')
            ret = VNA.do_get_yaxes()
            reals = ret[0]
#            reals = np.zeros(len(freqs))
            VNA.set_format('IMAG')
            ret = VNA.do_get_yaxes()
            imags = ret[0]
#            imags = np.zeros(len(freqs))
            VNA.set_format(prev_fmt)
            
    #        ret = VNA.do_get_data()
            VNA.set_trigger_source('internal')
    #        amps=ret[0]
    #        phases=ret[1]
    #        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))
    
            if count == 0:
                
                self.freqdata[0,:] = freqs
        #        print freqs
        #        print self.freqdata
                self.realdata[0,:] = reals
                self.imagdata[0,:] = imags
                datas = reals + 1j*imags
                self.fig = plt.figure()
#                print 'during plotting'
#                self.fig.add_subplot(111)
                gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
                self.fig.add_subplot(gs[0])
                self.fig.add_subplot(gs[1])
                self.fig.axes[0].plot(freqs/1e9, 20*np.log10(np.abs(datas)))
                self.fig.axes[1].plot(reals, imags)


                self.fig.axes[1].set_aspect('equal', 'box')

#                plt.show()
                self.fig.canvas.draw()

    
            else:
                reals =( reals *ave + self.realdata[0,:] * count)/float(ave+count)
                imags =( imags *ave + self.imagdata[0,:] * count)/float(ave+count)
                self.realdata[0,:] = reals
                self.imagdata[0,:] = imags
                datas = reals + 1j*imags
                self.fig.clear()
#                print 'during plotting'
#                self.fig.add_subplot(111)
                gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
                self.fig.add_subplot(gs[0])
                self.fig.add_subplot(gs[1])
                self.fig.axes[0].plot(freqs/1e9, 20*np.log10(np.abs(datas)))
                self.fig.axes[1].plot(reals, imags)


                self.fig.axes[1].set_aspect('equal', 'box')


#                self.fig.axes[0].plot(freqs/1e9, 20*np.log10(np.abs(datas)))
#                plt.show()
                self.fig.canvas.draw()


            
            count = count + ave
            print '%s averages done' %(count)
        self.analyze()

        
    def analyze(self):
#        fig = plt.figure()
        


        self.fit_params = analysis(self.freqdata, self.realdata, self.imagdata, self.fit_S12, self.fit_S11,figname = self.figname, title = self.title,fig=self.fig)

        
        

class SingleTraceNoAsync(Measurement1D):

    def __init__(self, freqs, fit_S12, fit_S11, **kwargs):
        self.freqs =freqs

        self.fit_S12 = fit_S12
        self.fit_S11 = fit_S11
        self.fig = None

        self.fit_params = None

#        self.plot_type = plot_type

        super(SingleTraceNoAsync, self).__init__(1, **kwargs)
        self.figname = self.data.get_fullname()
#        self.data.create_dataset('freqs', data = self.freqs)
        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
        self.realdata = self.data.create_dataset('real', shape=[1,len(self.freqs)])
        self.imagdata = self.data.create_dataset('imaginary', shape=[1,len(self.freqs)])




    def measure(self):
        # Generate and load sequences
#        print 'ok6'
        VNA = self.instruments['VNA']

        prev_fmt = VNA.get_format()
        freqs = VNA.do_get_xaxis()
        VNA.set_format('REAL')
        ret = VNA.do_get_yaxes()
        reals = ret[0]
#            reals = np.zeros(len(freqs))
        VNA.set_format('IMAG')
        ret = VNA.do_get_yaxes()
        imags = ret[0]
#            imags = np.zeros(len(freqs))
        VNA.set_format(prev_fmt)
        
#        ret = VNA.do_get_data()
        VNA.set_trigger_source('internal')
#        amps=ret[0]
#        phases=ret[1]
#        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))

            
        self.freqdata[0,:] = freqs
#        print freqs
#        print self.freqdata
        self.realdata[0,:] = reals
        self.imagdata[0,:] = imags
        datas = reals + 1j*imags
        self.fig = plt.figure()
#        print 'during plotting'
#                self.fig.add_subplot(111)
        gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
        self.fig.add_subplot(gs[0])
        self.fig.add_subplot(gs[1])
        self.fig.axes[0].plot(freqs/1e9, 20*np.log10(np.abs(datas)))
        self.fig.axes[1].plot(reals, imags)


        self.fig.axes[1].set_aspect('equal', 'box')


#                plt.show()
        self.fig.canvas.draw()

    

        self.analyze()

        
    def analyze(self):
#        fig = plt.figure()
        

        self.fit_params = analysis(self.freqdata, self.realdata, self.imagdata, self.fit_S12, self.fit_S11, figname = self.figname, fig=self.fig)

