import numpy as np
from math import factorial
import matplotlib.pyplot as plt
from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
import lmfit
import math
import time
import objectsharer as objsh



class FWM_f0g1_alazar(Measurement1D):

    def __init__(self, qubit_info, ef_info, fwm_gen, delay, 
                 freqs, power, fwm_channel, seq=None, postseq=None, 
                 extra_info=None, bgcor=False, qubit_rfsource=None, **kwargs):
        
        self.qubit_rfsource = qubit_rfsource
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        self.fwm_gen = fwm_gen
        self.delay = delay
        self.freqs = freqs
        self.power = power
        self.fwm_channel = fwm_channel
        self.bgcor = bgcor
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.xs = self.freqs

        npoints = len(self.freqs)
        if bgcor:
            npoints *= 2
        super(FWM_f0g1_alazar, self).__init__(npoints, infos=(qubit_info, ef_info), **kwargs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(freqs)])

        self.data.create_dataset('freqs', data=self.freqs)
        self.data.set_attrs(
            power=power,
            delay=delay
        )

    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate
        r_ef = self.ef_info.rotate
        

        s.append(self.seq)
        
#        s.append(r(np.pi, 0))
#        
#        s.append(r_ef(np.pi, 0))
        s.append(Constant(int(self.delay), 1, chan=self.fwm_channel))
        s.append(Delay(250))
#        s.append(r(np.pi, 0))        
        
#        s.append(r_ef(np.pi,0))
#        s.append(r(np.pi,0))
#        s.append(r_ef(np.pi/2,0)) #fluxonium
        
#        s.append(Combined([
#            Constant(int(self.delay), 1, chan=self.fwm_channel),
#            Constant(int(self.delay), self.amp, chan=self.ef_info.sideband_channels[0]),
#            Constant(int(self.delay), self.amp, chan=self.ef_info.sideband_channels[1])
#        ]))
    
#        s.append(Delay(2e3))
        

        if self.postseq:
            s.append(self.postseq)
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    
    def measure(self):
        alz = self.instruments['alazar']
        alz.set_interrupt(False)
        try:
            dig = self.instruments['dig']
            dig.start_hvi()
        except:
            print('no digitizer object for trigger')
 
        # Generate and load sequences

        seqs = self.generate()
        self.load(seqs)
        self.start_awgs()
        
        amps = []
        phases1 = []
        phases2 =[]
        phases=[]
        self.fwm_gen.set_power(self.power)

        for freq in self.freqs:
            self.fwm_gen.set_frequency(freq)
            time.sleep(0.2)

            alz.setup_avg_shot(alz.get_naverages())
            ret = alz.take_avg_shot(async=True)
            try:
                while not ret.is_valid():
                    objsh.helper.backend.main_loop(100)
            except Exception as e:
                alz.set_interrupt(True)
                print('Error: %s' % (str(e), ))
                return

            IQ = np.average(ret.get())
            amps.append(np.abs(IQ))
            phases1.append(np.angle(IQ, deg=True))
            print('F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True)))


            self.qubit_rfsource.set_rf_on(0)
            time.sleep(0.2)

            alz.setup_avg_shot(alz.get_naverages())
            ret = alz.take_avg_shot(async=True)
            try:
                while not ret.is_valid():
                    objsh.helper.backend.main_loop(100)
            except Exception as e:
                alz.set_interrupt(True)
                print('Error: %s' % (str(e), ))
                return

            IQ = np.average(ret.get())

            phases2.append(np.angle(IQ, deg=True))
            print('brick off F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True)))
                                
            self.qubit_rfsource.set_rf_on(1)

        self.ampdata[:] = amps

        m=len(amps)
        for i in range(m):
            phases.append(phases1[i] - phases2[i])

        self.phasedata[:] = phases
        self.analyze()

    def get_ys(self, data=None):
        return self.ampdata

    def analyze(self):
        f = plt.figure()

        ax1 = f.add_subplot(2,1,1)
        ax2 = f.add_subplot(2,1,2)
        ax1.plot(self.freqs, self.ampdata[:])
        ax2.plot(self.freqs, self.phasedata[:])
        ax1.set_ylabel('Intensity [AU]')
        ax2.set_ylabel('Angle [deg]')
        ax1.set_xlabel('freq ')
        ax2.set_xlabel('freq')

