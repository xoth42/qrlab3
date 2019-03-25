from measurement import Measurement1D
import matplotlib.pyplot as plt
import numpy as np
#from pulseseq.sequencer import *
#from pulseseq.pulselib import *
#from lib.math import fit
import objectsharer as objsh
import time
#
#plot type 0: amp and phase
#plot type 1: real and imag
def analysis(freqs, realdata, imagdata, fig=None):
    if fig is None:
        fig = plt.figure()

#    if plot_type == 0:

    ampdata = 20*np.log10(np.sqrt(realdata[0,:]**2 + imagdata[0,:]**2))
    plt.plot(freqs[0,:]/float(1e9), ampdata )
    plt.xlabel('freq(GHz)')
    plt.ylabel('dB')
    
#    if plot_type == 1:
    plt.figure()
    plt.plot( realdata[0,:], imagdata[0,:])
    plt.xlabel('I')
    plt.ylabel('Q')        


class SingleTrace(Measurement1D):

    def __init__(self,freqs, average_factor, avelimit, **kwargs):
        self.freqs =freqs
#        self.meas_info = meas_info
#        self.device_info = device_info
#        plot_type = SPEC
        self.average_factor = average_factor
        self.avelimit = avelimit
#        self.plot_type = plot_type

        super(SingleTrace, self).__init__(1, **kwargs)
#        self.data.create_dataset('freqs', data = self.freqs)
        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
        self.realdata = self.data.create_dataset('real', shape=[1,len(self.freqs)])
        self.imagdata = self.data.create_dataset('imaginary', shape=[1,len(self.freqs)])




    def measure(self):
        # Generate and load sequences
        print 'ok6'
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
            
        ave = self.avelimit
        VNA.set_average_factor(ave)
        count = 0

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
                    VNA.set_format('REAL')
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
    
    
            else:
                reals =( reals *ave + self.realdata[0,:] * count)/float(ave+count)
                imags =( imags *ave + self.imagdata[0,:] * count)/float(ave+count)
                self.realdata[0,:] = reals
                self.imagdata[0,:] = imags


            
            count = count + ave
            print '%s averages done' %(count)
        self.analyze()

        
    def analyze(self):
#        fig = plt.figure()
        
        analysis(self.freqdata, self.realdata, self.imagdata, fig=None)
