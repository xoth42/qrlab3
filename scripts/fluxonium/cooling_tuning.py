# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 23:25:51 2020

@author: wanglab
"""

from measurement import Measurement2D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import time
import objectsharer as objsh

SPEC   = 0
POWER  = 1
  
    
class Coolingspec(Measurement2D):

    def __init__(self, cool_rfsource, qubit_info, cool_freqs, cool_powers,
                 seq=None, postseq=None,
                 pow_delay=1, freq_delay=0.1, plot_type=None,
                 **kwargs):
        self.cool_rfsource =cool_rfsource
        self.qubit_info = qubit_info
        self.cool_powers = cool_powers
        self.cool_freqs = cool_freqs
        self.pow_delay = pow_delay
        self.freq_delay = freq_delay
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.xs=cool_freqs
        self.ys=cool_powers

        if plot_type is None:
            if len(cool_powers) > len(q_freqs):
                plot_type = POWER
            else:
                plot_type = SPEC
        self.plot_type = plot_type

        XS, YS = np.meshgrid(self.xs, self.ys)
        self.two_axes = (-XS + 1j*YS)

        npoints = self.two_axes.size


        super(Coolingspec, self).__init__(npoints, infos=qubit_info, **kwargs)
        self.data.create_dataset('two_axes', data=self.two_axes, dtype=np.complex)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(cool_powers),len(cool_freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(cool_powers),len(cool_freqs)])


    

        
    def generate(self):
        #Ebru - I will switch back to normal after trying
        s = Sequence()
        chs = self.qubit_info.sideband_channels   
        r = self.qubit_info.rotate
#
#        s.append(r(np.pi, X_AXIS))                
#        s.append(Constant(self.plen,1, chan='3m1'))
#        s.append(Delay(80))       
#
        s.append(self.seq)    
            
        if self.postseq:
            s.append(self.postseq)

        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))
    
        s.append(Delay(5000))

        s.append(self.seq)    
        s.append(r(np.pi, X_AXIS))                
           
        if self.postseq:
            s.append(self.postseq)

        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))
        s.append(Delay(5000))
   
        s.append(Delay(500))        
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

        for ipower, power in enumerate(self.cool_powers):
            self.cool_rfsource.set_power(power)
            time.sleep(self.pow_delay)

            amps = []
            phases = []
            for freq in self.cool_freqs:
                self.cool_rfsource.set_frequency(freq)
                time.sleep(self.freq_delay)

                alz.setup_avg_shot(alz.get_naverages())
                ret = alz.take_avg_shot(async=True)
                try:
                    while not ret.is_valid():
                        objsh.helper.backend.main_loop(100)
                except Exception, e:
                    alz.set_interrupt(True)
                    print 'Error: %s' % (str(e), )
                    return

                IQ = np.average(ret.get())
                amps.append(np.abs(IQ))
                phases.append(np.angle(IQ, deg=True))
                print 'F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True))

            self.ampdata[ipower,:] = amps[(2*ipower)+1]-amps[(2*ipower)]
            self.phasedata[ipower,:] = phases[(2*ipower)+1]-amps[(2*ipower)]

        self.analyze()

    def analyze(self):
        
        zs = self.phasedata
        zs = zs.reshape(len(meas.xs), len(meas.ys))
        xs, ys = meas.get_plotxsys()
        ax = fig.axes[0]
        plt.sca(ax)
        pc = ax.pcolormesh(xs, ys, zs)#, cmap=plt.get_cmap('RdBu'))
        fig.colorbar(pc)
    
        ax.set_xlim(xs.min()), xs.max()
        ax.set_ylim(ys.min(), ys.max())
        ax.set_xlabel('times')
        ax.set_ylabel('amp')
        fig.canvas.draw() 
