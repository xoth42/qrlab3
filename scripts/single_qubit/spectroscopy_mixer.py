# -*- coding: utf-8 -*-
"""
Created on Thu Jun 03 12:03:10 2021

@author: Wang_Lab
"""

from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import time
import objectsharer as objsh
import os
import config

SPEC   = 0
POWER  = 1

class Spectroscopy_Mixer(Measurement1D):
    '''
    Perform qubit spectroscopy.

    The frequency of <qubit_rfsource> will be swept over <q_freqs> and
    different read-out powers <ro_powers> will be set on readout_info.rfsource1.

    The spectroscopy pulse has length <plen> ns.

    If <seq> is specified it is played at the start (should start with a trigger)
    If <postseq> is specified it is played at the end, right before the read-out
    pulse.
    '''

    def __init__(self, qubit_rfsource, qubit_info, mixer_info1, mixer_info2, q_freqs, ro_powers,
                 plen, amp=1, seq=None, postseq=None,
                 pow_delay=1, freq_delay=0.1, plot_type=None,
                 **kwargs):
        self.qubit_rfsource = qubit_rfsource
        self.qubit_info = qubit_info
        self.mixer_info1 = mixer_info1
        self.mixer_info2 = mixer_info2
#        self.ef_info = ef_info
        self.ro_powers = ro_powers
        self.q_freqs = q_freqs
        self.plen = plen
        self.amp = amp
        self.pow_delay = pow_delay
        self.freq_delay = freq_delay
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        if plot_type is None:
            if len(ro_powers) > len(q_freqs):
                plot_type = POWER
            else:
                plot_type = SPEC
        self.plot_type = plot_type

        super(Spectroscopy_Mixer, self).__init__(1, infos=(qubit_info,mixer_info1,mixer_info2), **kwargs)
        self.data.create_dataset('powers', data=ro_powers)
        self.data.create_dataset('freqs', data=q_freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(ro_powers),len(q_freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(ro_powers),len(q_freqs)]) 

    def generate(self):
#        ro = self.readout_driver.do_get_sequence(self.readout_qubit_info)
        ro =Combined([
            Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
#            Join([Constant(self.readout_info.pulse_len + 100, 1, chan=self.readout_info.readout_chan),Delay(200)]),
            Join([self.mixer_info1.rotate(np.pi, 0),Delay(200)]),
            Join([self.mixer_info2.rotate(np.pi, 0),Delay(200)])])
        s = Sequence(self.seq)
        chs = self.qubit_info.sideband_channels

        s.append(Combined([
            Constant(self.plen, self.amp, chan=chs[0]),
            Constant(self.plen, self.amp, chan=chs[1]),
        ])) 
#        s.append(Constant(self.plen, 1, chan='3m1'))        
#        s.append(Delay(100))
#
#        if self.postseq:
#            s.append(self.postseq)
#            
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#        ])) 

##Ebru    THIS NEEDS TO BE CHANGED BACK TO NORMAL
#        s = Sequence(self.seq)
#        r = self.qubit_info.rotate
#        r_ef = self.ef_info.rotate
#        s.append(r(np.pi, 0))
#        s.append(r_ef(np.pi, 0))        
#        s.append(Constant(self.plen, 1, chan='3m1'))  
        
        
#        s.append(Delay(100))
        if self.postseq:
            s.append(self.postseq)
            
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#        ])) 
        s.append(ro)
 


##Ebru
    
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=int(self.readout_info.acq_chan)),
#            Constant(self.readout_info.pulse_len, 1, chan=int(self.readout_info.readout_chan_I)),
#            Constant(self.readout_info.pulse_len, 1, chan=int(self.readout_info.readout_chan_Q)),
#        ]))
        s.append(Delay(2000))          #ebru:added the delay
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def measure(self):
        dig = self.instruments['dig']

        # Generate and load sequences
        seqs = self.generate()
        self.stop_awgs()
        self.load(seqs)
        self.start_awgs()

        for ipower, power in enumerate(self.ro_powers):
#            self.readout_info.rfsource.set_power(power)
            print('Power = %s' % (power, ))
            time.sleep(self.pow_delay)

            amps = []
            phases = []
            for freq in self.q_freqs:
                self.qubit_rfsource.set_frequency(freq)
                time.sleep(self.freq_delay)
                
                dig.setup_avg_shot()
                dig.arm()
                dig.start_hvi()
                ret = dig.take_avg_shot()
                #Yingying to add a main loop, suggesting to help with the spectroscopy crash
                
                try:
                    while not ret.is_valid():
                        objsh.helper.backend.main_loop(100)
                except:
                    dig.set_interrupt(True)

                dig.release_buf()


                IQ = np.average(ret)
                amps.append(np.abs(IQ))
                phases.append(np.angle(IQ, deg=True))
                print('F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True)))

            self.ampdata[ipower,:] = amps

            self.phasedata[ipower,:] = phases

        self.analyze()

    def analyze(self):
        f = plt.figure()

        if self.plot_type == SPEC:
            ax1 = f.add_subplot(2,1,1)
            ax2 = f.add_subplot(2,1,2)
            for ipower, power in enumerate(self.ro_powers):
                ax1.plot(self.q_freqs/1e6, self.ampdata[ipower,:], label='Amps, Power %.01f dB'%power)
                ax2.plot(self.q_freqs/1e6, self.phasedata[ipower,:], label='Phase, Power %.01f dB'%power)
            fs = self.q_freqs
            amps = self.ampdata[0,:]
#            phases = self.phasedata[0,:]
            f = fit.Lorentzian(fs, amps)
#            f = fit.Lorentzian(fs, phases)
            h0 = np.max(amps)/2.0
            w0 = 2e6
            pos = fs[np.argmax(amps)]
            p0 = [np.max(amps), w0*h0, pos, w0]
            p = f.fit(p0)
            txt = 'Center = %.03f MHz' % (p[2]/1e6,)
            print('Fit gave: %s' % (txt,))
            ax1.plot(fs/1e6, f.func(p, fs), label=txt)

            ax1.legend()
            ax2.legend()
            ax1.set_ylabel('Intensity [AU]')
            ax2.set_xlabel('Frequency [MHz]')

        if self.plot_type == POWER:
            ax1 = f.add_subplot(2,1,1)
            ax2 = f.add_subplot(2,1,2)
            for ifreq, freq in enumerate(self.q_freqs):
                ax1.plot(self.ro_powers, self.ampdata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
                ax2.plot(self.ro_powers, self.phasedata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
            ax1.legend()
            ax2.legend()
            ax1.set_ylabel('Intensity [AU]')
            ax2.set_ylabel('Angle [deg]')
            ax1.set_xlabel('Power [dB]')
            ax2.set_xlabel('Power [dB]')
#        plt.savefig('out/' + str(int(self.q_freqs[0]/1e6)) + '.png')
        ## Yingying add it to save the figure        
        fn = os.path.join(config.datadir, 'images/%s_qubitspec.png'%(time.strftime('%Y%m%d/%H%M%S', time.localtime())))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        plt.savefig(fn, **kwargs)
