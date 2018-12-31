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



class FWM_spec(Measurement1D):

    def __init__(self, qubit_info, cav_info, fwm_info, fwm_gen, disp, delay, 
                 freqs, amp, fwm_channel, seq=None, postseq=None, 
                 extra_info=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.fwm_info = fwm_info
        self.fwm_gen = fwm_gen
        self.disp = disp
        self.delay = delay
        self.freqs = freqs
        self.amp = amp
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
        super(FWM_spec, self).__init__(npoints, infos=(qubit_info, cav_info, fwm_info), **kwargs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(freqs)])

        self.data.create_dataset('freqs', data=self.freqs)
        self.data.set_attrs(
            disp=disp,
            delay=delay
        )

    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate_selective
        c = self.cav_info.rotate
        

        s.append(self.seq)
        
        s.append(c(np.abs(self.disp), np.angle(self.disp)))
                
        s.append(Combined([
            Constant(int(self.delay-100e3), 1, chan=self.fwm_channel),
            Constant(int(self.delay-100e3), self.amp, chan=self.fwm_info.sideband_channels[0]),
            Constant(int(self.delay-100e3), self.amp, chan=self.fwm_info.sideband_channels[1]),
        ]))

        s.append(Delay(100e3))
        
        s.append(r(np.pi, X_AXIS))

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
        # Generate and load sequences
        dig = self.instruments['dig']

        fwmgen = mclient.instruments['fwmgen']

        seqs = self.generate()
        self.load(seqs)
        self.start_awgs()

        amps = []
        phases = []
        for freq in self.freqs:
#                self.cav_source.set_rf1_freq(freq) #JEFF Wrong syntax
            self.fwm_gen.set_frequency(freq)
#                self.cav_source.set_rf_on(True)
            time.sleep(0.2)


            dig.setup_avg_shot()
            dig.arm()
            dig.start_hvi()
            ret = dig.take_avg_shot(async=True)
            dig.release_buf()
            
            try:
                while not ret.is_valid():
                    objsh.helper.backend.main_loop(100)
            except Exception, e:
                dig.set_interrupt(True)
                print 'Error: %s' % (str(e), )
                return

            IQ = np.average(ret.get())
            IQ_std = np.std(ret.get())
            
            amps.append(np.abs(IQ))
            phases.append(np.angle(IQ, deg=True))
            print 'F = %.03f MHz --> amp = %.1f, angle = %.01f' % (freq / 1e6, np.abs(IQ), 
                                                                   np.angle(IQ, deg=True))
        
        if self.bgcor:
            self.fwm_gen.set_rf_on(False)
            time.sleep(.2)
            
            naverages = dig.get_naverages()
            dig.set_naverages(naverages*10)
            dig.setup_avg_shot()
            dig.arm()
            dig.start_hvi()
            ret = dig.take_avg_shot(async=True)
            dig.release_buf()
            dig.set_naverages(naverages)
            
            try:
                while not ret.is_valid():
                    objsh.helper.backend.main_loop(100)
            except Exception, e:
                dig.set_interrupt(True)
                print 'Error: %s' % (str(e), )
                return
            
            IQ_bg = np.average(ret.get())
            print('background amp', np.abs(IQ_bg))
            print('background phase', np.angle(IQ_bg, deg=True))

            self.ampdata[:] = amps - np.abs(IQ_bg)
            self.phasedata[:] = phases - np.angle(IQ_bg, deg=True)
        else:
            self.ampdata[:] = amps
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

