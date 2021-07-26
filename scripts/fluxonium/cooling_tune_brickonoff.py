from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
import numpy as np
from lib.math import fit
import time
import objectsharer as objsh
import mclient
SPEC   = 0
POWER  = 1

class Cooling_tune_brickonoff(Measurement1D):
    '''
    Perform qubit spectroscopy and account for the phase drift over time. 

    The frequency of <qubit_rfsource> will be swept over <q_freqs> and
    different read-out powers <ro_powers> will be set on readout_info.rfsource1.

    The spectroscopy pulse has length <plen> ns.

    If <seq> is specified it is played at the start (should start with a trigger)
    If <postseq> is specified it is played at the end, right before the read-out
    pulse.
    '''

    def __init__(self, cool_rfsource, qubit_rfsource, qubit_info, cool_freqs, cool_powers, cool_channel, seq=None, postseq=None,
                 pow_delay=0.5, freq_delay=0.2, plot_type=None,
                 **kwargs):
        self.cool_rfsource = cool_rfsource
        self.qubit_rfsource = qubit_rfsource
        self.qubit_info = qubit_info
        self.cool_powers = cool_powers
        self.cool_freqs = cool_freqs
        self.pow_delay = pow_delay
        self.freq_delay = freq_delay
        self.cool_channel = cool_channel
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq

        if plot_type is None:
            if len(cool_powers) > len(cool_freqs):
                plot_type = POWER
            else:
                plot_type = SPEC
        self.plot_type = plot_type

        super(Cooling_tune_brickonoff, self).__init__(1, infos=qubit_info, **kwargs)
        self.data.create_dataset('powers', data=cool_powers)
        self.data.create_dataset('freqs', data=cool_freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(cool_powers),len(cool_freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(cool_powers),len(cool_freqs)])

#    def generate(self):
#        s = Sequence(self.seq)
#        chs = self.qubit_info.sideband_channels
#        s.append(Constant(self.plen, self.amp, chan=chs[0]))
#        if self.postseq:
#            s.append(self.postseq)
#
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#        ]))
#        s = self.get_sequencer(s)
#        seqs = s.render()
#        return seqs
    
    def generate(self):
        s = Sequence(self.seq)
        s.append(Constant(int(4e3),1,chan=self.cool_channel))
        s.append(Delay(150))
        s.append(self.qubit_info.rotate(np.pi,0))
        s.append(Delay(5))
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

        for ipower, power in enumerate(self.cool_powers):
            self.cool_rfsource.set_power(power)
            print('Cooling power P = %.03f dBm' % (power)) 
            time.sleep(self.pow_delay)

            amps = []
            phases1 = []
            phases2 =[]
            phases=[]
            for freq in self.cool_freqs:
                self.cool_rfsource.set_frequency(freq)
                self.qubit_rfsource.set_rf_on(0)
                time.sleep(self.freq_delay)

                alz.setup_avg_shot(alz.get_naverages())
                ret = alz.take_avg_shot(async_=True)
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
                print('qubit off F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True)))
                

                self.qubit_rfsource.set_rf_on(1)
                time.sleep(self.freq_delay)

                alz.setup_avg_shot(alz.get_naverages())
                ret = alz.take_avg_shot(async_=True)
                try:
                    while not ret.is_valid():
                        objsh.helper.backend.main_loop(100)
                except Exception as e:
                    alz.set_interrupt(True)
                    print('Error: %s' % (str(e), ))
                    return

                IQ = np.average(ret.get())

                phases2.append(np.angle(IQ, deg=True))
                print('qubit on F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True)))

            m=len(amps)
            for i in range(m):
                phases.append(phases1[i] - phases2[i])
                
            self.ampdata[ipower,:] = amps
            self.phasedata[ipower,:] = phases                

        self.analyze()

    def analyze(self):
        f = plt.figure()

        if self.plot_type == SPEC:
            ax1 = f.add_subplot(2,1,1)
            ax2 = f.add_subplot(2,1,2)
            for ipower, power in enumerate(self.cool_powers):
                ax1.plot(self.cool_freqs/1e6, self.ampdata[ipower,:], label='Amps, Power %.01f dB'%power)
                ax2.plot(self.cool_freqs/1e6, self.phasedata[ipower,:], label='Phase, Power %.01f dB'%power)

            fs = self.cool_freqs
            amps = self.ampdata[0,:]
            f = fit.Lorentzian(fs, amps)
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
            for ifreq, freq in enumerate(self.cool_freqs):
                ax1.plot(self.ro_powers, self.ampdata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
                ax2.plot(self.ro_powers, self.phasedata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
            ax1.legend()
            ax2.legend()
            ax1.set_ylabel('Intensity [AU]')
            ax2.set_ylabel('Angle [deg]')
            ax1.set_xlabel('Power [dB]')
            ax2.set_xlabel('Power [dB]')
