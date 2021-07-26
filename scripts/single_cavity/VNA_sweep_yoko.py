# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:51:43 2019

@author: WangLab
"""


from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
import numpy as np
#
#SPEC   = 0
#POWER  = 1

def analysis(voltdata, freqdata, realdata, imagdata, fig_name, fig=None):
    if fig is None:
        fig = plt.figure()
        
    volts =  voltdata[0,:] 
    field = np.zeros(len(volts))     
    for i in range(len(volts)):
        if volts[i] < 5:
            field[i] = volts[i]*60
        else:
            field[i] = -2.709 * (volts[i])**2 + 86.171*volts[i]-63.13
    
    field_a = field *(float(56)/float(60))  #1V is 60mA near the pole, and 56mA around the center
     

#    print X
#    print Y
    ampdata = np.zeros((len(voltdata[0,:]), len(freqdata[0,:])))
#    imag = np.zeros((len(self.currents),len(self.freqs)))
    for i in range(len(volts)):
        ampdata[i] = 20*np.log10(np.sqrt(realdata[i,:]**2 + imagdata[0,:]**2))
#    print Z
    field_a, freqdata = np.meshgrid(field_a, freqdata[0,:])
    ampdata_a = np.transpose(ampdata)
    freqGHz = freqdata/float(10**9)
#    phase = np.transpose(phase)
    plt.figure()
    plt.pcolormesh(field_a, freqGHz, ampdata_a)
    plt.colorbar()
    plt.title(fig_name)
    plt.xlabel('Magnetic Field(mT)')
    plt.ylabel('Frequency(GHz)')


class Sweep_YOKO(Measurement1D):

    def __init__(self, volts, freqs, average_factor,fig_name, **kwargs):
        self.volts = volts
#        print 'self.volts', self.volts
        self.freqs = freqs
        self.average_factor = average_factor
        self.fig_name = fig_name
#        self.sleeptime_field = sleeptime_field
#        self.plot_type = plot_type

        super(Sweep_YOKO, self).__init__(1, **kwargs)
#        self.data.create_dataset('volts', data=self.volts)
        self.voltdata = self.data.create_dataset('volts', shape=[1,len(self.volts)])
        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
#        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.volts),len(freqs)])
#        self.phasedata = self.data.create_dataset('phases', shape=[len(self.volts),len(freqs)])
        self.realdata = self.data.create_dataset('real', shape=[len(self.volts),len(freqs)])
        self.imagdata = self.data.create_dataset('imaginary', shape=[len(self.volts),len(freqs)])


    def measure(self):
        # Generate and load sequences
        VNA = self.instruments['VNA']
        Yoko = self.instruments['Yoko']


        VNA.set_start_freq(self.freqs[0])
        VNA.set_stop_freq(self.freqs[-1])
        VNA.set_points(len(self.freqs))
        Freqs = VNA.do_get_xaxis()
        if not (Freqs == self.freqs).all():
            print('error in setting frequency')
#            break
        self.freqdata[0,:] = Freqs
        self.voltdata[0,:] = self.volts
        
        
        timelimit = 300 # breaks long time measurement to severals 300 seconds.
        avelimit = int(timelimit/VNA.get_sweep_time())
        if avelimit<1:
            avelimit = 1
        if avelimit >999:
            avelimit = 999
        
        for ivolt, volt in enumerate(self.volts):
            Yoko.do_set_voltage(volt)
            time.sleep(1)
            ave = avelimit
            VNA.set_average_factor(ave)
            count = 0
    
            while count < self.average_factor:
                ave = avelimit
                
                if (self.average_factor-count) < avelimit:
                    ave = self.average_factor-count
                    VNA.set_average_factor(ave)
                
                reals = []
                imags = []
        
        
    #            VNA.set_trigger_source('internal')
    #            VNA.set_average_factor(40)
    
                VNA.set_trigger_source('BUS')
                VNA.write('INIT:CONT ON')
        
                VNA.set_averaging_trigger(1)
                VNA.trigger()
                
                wait = VNA.opc(async_=True) # wait for completion
        
    #            print 'ok7'
                a=0
                try:
                    while not wait.is_valid():
                        if a % 10 == 0:
                            print('async', a) 
                        a= a + 1
                        
    #                    time.sleep(0.1)
                        objsh.helper.backend.main_loop(100)
                except:
                    print('error with async')
    #                VNA.set_interrupt(True)
    #        '''
        
    #            print 'ok8'
                prev_fmt = VNA.get_format()
                freqs = VNA.do_get_xaxis()
                VNA.set_format('REAL')
                ret = VNA.do_get_yaxes()
                reals = ret[0]
                VNA.set_format('IMAG')
                ret = VNA.do_get_yaxes()
                imags = ret[0]
                VNA.set_format(prev_fmt)
                
        #        ret = VNA.do_get_data()
                VNA.set_trigger_source('internal')
        #        amps=ret[0]
        #        phases=ret[1]
        #        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))
        
                if count == 0:
                    
#                    self.freqdata[0,:] = freqs
            #        print freqs
            #        print self.freqdata
                    self.realdata[ivolt,:] = reals
                    self.imagdata[ivolt,:] = imags
        
        
                else:
                    reals =( reals *ave + self.realdata[ivolt,:] * count)/float(ave+count)
                    imags =( imags *ave + self.imagdata[ivolt,:] * count)/float(ave+count)
                    self.realdata[ivolt,:] = reals
                    self.imagdata[ivolt,:] = imags
    
    
                
                count = count + ave
                print('%s averages done' %(count))
            
            print('volt = %.03fV done ' % (volt))


#        print 'self.ampdata\n', self.ampdata
        self.analyze()

    def analyze(self):
        analysis(self.voltdata, self.freqdata, self.realdata, self.imagdata, self.fig_name,fig=None)
