# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:51:43 2019

@author: WangLab
"""

#import mclient
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

def analysis(currentdata, freqdata, realdata, imagdata, fig_name, Sij, fig=None):
    if fig is None:
        fig = plt.figure()
        
    currents =  currentdata[0,:] 
    field = np.zeros(len(currents))     
    for i in range(len(currents)):
        #Current-field relationship input below, for driving Yoko in current mode - BS, 3/20/19
        if currents[i] < 0.5:
            field[i] = currents[i]*529.37 + 0.49
        else:
            field[i] = -268.93 * (currents[i])**2 + 839.69*currents[i]-88.67
#        The statements below are for driving the Yoko in voltage mode
#        if currents[i] < 5:
#            field[i] = currents[i]*60
#        else:
#            field[i] = -2.709 * (currents[i])**2 + 86.171*currents[i]-63.13
    
#    field_a = field *(float(56)/float(60))  #1V is 60mT near the pole, and 56mT around the center
     

#    print X
#    print Y
    ampdata = np.zeros((len(realdata),len(currentdata[0,:]), len(freqdata[0,:])))
    ampdata_a = np.zeros((len(realdata),len(freqdata[0,:]), len(currentdata[0,:])))
    for k in range(len(realdata)):
        
#        ampdata = np.zeros((len(realdata),len(currentdata[0,:]), len(freqdata[0,:])))
    #    imag = np.zeros((len(self.currents),len(self.freqs)))
        for i in range(len(currents)):
            ampdata[k][i] = 20*np.log10(np.sqrt(realdata[k][i,:]**2 + imagdata[k][0,:]**2))
    #    print Z
        field_a, freqdata = np.meshgrid(field, freqdata[0,:])
        ampdata_a[k] = np.transpose(ampdata[k])
        freqGHz = freqdata/float(10**9)
    #    phase = np.transpose(phase)
        plt.figure(k)
        plt.pcolormesh(field_a, freqGHz, ampdata_a[k])
        plt.colorbar()
        plt.title('%s%s'%(fig_name,Sij[i]))
        plt.xlabel('Magnetic Field(mT)')
        plt.ylabel('Frequency(GHz)')


class Current_Sweep_YOKO(Measurement1D):

    def __init__(self, currents, freqs, average_factor,Sij, fig_name, **kwargs):
        self.currents = currents
#        print 'self.currents', self.currents
        self.freqs = freqs
        self.average_factor = average_factor
        self.Sij = Sij
        self.fig_name = fig_name
#        self.sleeptime_field = sleeptime_field
#        self.plot_type = plot_type
#
        super(Current_Sweep_YOKO, self).__init__(1, **kwargs)
        print self.data.get_fullname()
#        self.data.create_dataset('currents', data=self.currents)
#        self.currentdata = self.data.create_dataset('currents', shape=[1,len(self.currents)])
#        self.freqdata = self.data.create_dataset('freqs', shape=[1,len(self.freqs)])
##        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.currents),len(freqs)])
##        self.phasedata = self.data.create_dataset('phases', shape=[len(self.currents),len(freqs)])
#        print self.freqdata.get_fullname()
#        self.realdata = [0,0,0,0]
#        self.imagdata = [0,0,0,0]
#        for i, sij in enumerate(self.Sij):
#            
#            self.realdata[i] = self.data.create_dataset('real%s'%(sij), shape=[len(self.currents),len(freqs)])
#            self.imagdata[i]= self.data.create_dataset('imaginary%s'%(sij), shape=[len(self.currents),len(freqs)])
#        
        
    def measure(self):
        # Generate and load sequences
        VNA = self.instruments['VNA']
        Yoko = self.instruments['Yoko']


        VNA.set_start_freq(self.freqs[0])
        VNA.set_stop_freq(self.freqs[-1])
        VNA.set_points(len(self.freqs))
        Freqs = VNA.do_get_xaxis()
#        if not (Freqs == self.freqs).all():
#            print 'error in setting frequency'
#            break
#        self.freqdata[0,:] = Freqs
#        self.currentdata[0,:] = self.currents
        
        
        timelimit = 16 # breaks long time measurement to severals 16 seconds.
        avelimit = int(timelimit/VNA.get_sweep_time())
        if avelimit<1:
            avelimit = 1
        if avelimit >999:
            avelimit = 999
            
        if self.average_factor < avelimit:
            avelimit = self.average_factor
            
        VNA.set_average_factor(avelimit)
        
        for icurrent, current in enumerate(self.currents):
#            Yoko.do_set_current(current)
            time.sleep(0.5)
            ave = avelimit
            if self.average_factor > avelimit
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
                
                wait = VNA.opc(async=True) # wait for completion
        
    #            print 'ok7'
#                a=0
                try:
                    while not wait.is_valid():
#                        if a % 10 == 0:
#                            print 'async', a 
#                        a= a + 1
                        
    #                    time.sleep(0.1)
                        objsh.helper.backend.main_loop(100)
                except:
                    print 'error with async'
    #                VNA.set_interrupt(True)
    #        '''
        
    #            print 'ok8'
                for i, sij in enumerate(self.Sij):
                    VNA.set_s_param(sij)
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
#                VNA.set_trigger_source('internal')
        #        amps=ret[0]
        #        phases=ret[1]
        #        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))
        
#                    if count == 0:
#                        
#    #                    self.freqdata[0,:] = freqs
#                #        print freqs
#                #        print self.freqdata
#                        self.realdata[i][icurrent,:] = reals
#                        self.imagdata[i][icurrent,:] = imags
#            
#            
#                    else:
#                        reals =( reals *ave + self.realdata[i][icurrent,:] * count)/float(ave+count)
#                        imags =( imags *ave + self.imagdata[i][icurrent,:] * count)/float(ave+count)
#                        self.realdata[i][icurrent,:] = reals
#                        self.imagdata[i][icurrent,:] = imags
    
    
#                VNA.set_trigger_source('internal')
                count = count + ave
                print '%s averages done' %(count)
            
            print 'current = %.04fmA done ' % (current)


#        print 'self.ampdata\n', self.ampdata
#        self.analyze()

    def analyze(self):
        analysis(self.currentdata, self.freqdata, self.realdata, self.imagdata, self.fig_name,self.Sij, fig=None)
