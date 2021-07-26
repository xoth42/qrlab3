# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 18:45:22 2019

@author: WangLab
"""

from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
#
#SPEC   = 0
#POWER  = 1




class ColorPlot_YOKO(Measurement1D):

    def __init__(self, currents, freqs, sleeptime_field, **kwargs):
        self.currents = currents
        print('self.currents', self.currents)
        self.freqs = freqs
        self.sleeptime_field = sleeptime_field
#        self.plot_type = plot_type

        super(ColorPlot_YOKO, self).__init__(1, **kwargs)
        self.data.create_dataset('currents', data=currents)
        self.data.create_dataset('freqs', data=freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(currents),len(freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(currents),len(freqs)])
        


    def measure(self):
        # Generate and load sequences
        VNA = self.instruments['VNA']
        Yoko = self.instruments['Yoko']


        VNA.set_start_freq(self.freqs[0])
        VNA.set_stop_freq(self.freqs[-1])
        VNA.set_points(len(self.freqs))
        freqs = VNA.do_get_xaxis()
        if not (freqs == self.freqs).all():
            print('error in setting frequency')
#            break
        
        for icurrent, current in enumerate(self.currents):
            Yoko.do_set_current(current)
            time.sleep(self.sleeptime_field)
            
            amps = []
            phases = []
    
    
            VNA.set_trigger_source('BUS')
            VNA.write('INIT:CONT ON')
    
            VNA.set_averaging_trigger(1)
            VNA.trigger()
#            ret = VNA.opc(async_=True) # wait for completion
        
        #        ret = VNA.do_get_data()
        
        
            try:
                while not VNA.opc.is_valid():
                    objsh.helper.backend.main_loop(100)
            except:
                print('error with async')
    #            VNA.set_interrupt(True)
    

            ret = VNA.do_get_data()
            VNA.set_trigger_source('internal')
    #        IQ = np.average(ret.get())
            amps=ret[0]
            phases=ret[1]
    #        print 'F = %.03f GHz --> amp = %.1f, angle = %.01f' % (freq / 1e9, np.abs(IQ), np.angle(IQ, deg=True))
            print('current = %.03f mA' % (current))

            self.ampdata[icurrent,:] = amps
            self.phasedata[icurrent,:] = phases

        print('self.ampdata\n', self.ampdata)
        self.analyze()

    def analyze(self):
        X, Y = np.meshgrid(self.currents, self.freqs)
#        print 'self.volts again', self.volts
        print(X)
        print(Y)
        Z = np.zeros((len(self.currents),len(self.freqs)))
        phase = np.zeros((len(self.currents),len(self.freqs)))
        for i in range(len(self.currents)):
            Z[i] = np.array(self.ampdata[i,:])
            phase[i] = np.array(self.phasedata[i,:])
        print(Z)
        Z = np.transpose(Z)
        phase = np.transpose(phase)
        plt.figure()
        plt.pcolormesh(X, Y, Z)
        plt.colorbar()
        plt.xlabel('Magnetic Field Voltage')
        plt.ylabel('Frequency')