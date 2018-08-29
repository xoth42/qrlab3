from measurement import Measurement1D
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
import numpy as np

SPEC   = 0
POWER  = 1

def analysis(powers, freqs, ampdata, phasedata=None, plot_type=POWER, ax=None):
    if ax is None:
        ax = plt.figure().add_subplot(111)
    ax2 = ax.twinx()

    if plot_type == SPEC:
        for ipower, power in enumerate(powers):
            ax.plot(freqs/1e6, ampdata[ipower,:], label='Power %.02f dB'%power)
            ax2.plot(freqs/1e6, ampdata[ipower,:], label='Power %.02f dB'%power)

        fs = freqs
        amps = ampdata[0,:]
        f = fit.Lorentzian(fs, amps)
        h0 = np.max(amps)
        w0 = 2e6
        pos = fs[np.argmax(amps)]
        p0 = [np.min(amps), w0*h0, pos, w0]
        p = f.fit(p0)
        txt = 'Center = %.03f MHz' % (p[2]/1e6,)
        print 'Fit gave: %s' % (txt,)
#        plt.plot(fs/1e6, f.func(p, fs), label=txt)

        plt.legend()
        plt.ylabel('Intensity [AU]')
        plt.xlabel('Frequency [MHz]')

    if plot_type == POWER:
#        ax1 = f.add_subplot(2,1,1)
#        ax2 = f.add_subplot(2,1,2)
        for ifreq, freq in enumerate(freqs):
            ax.plot(powers, ampdata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
            ax2.plot(powers, phasedata[:,ifreq], label='RF @ %.03f MHz'%(freq/1e6,))
        ax.legend()
        ax2.legend()
        ax.set_ylabel('Intensity [AU]')
        ax2.set_ylabel('Angle [deg]')
        ax.set_xlabel('Power [dB]')
        ax2.set_xlabel('Power [dB]')

class ROCavSpectroscopy_keysight(Measurement1D):

    def __init__(self, qubit_info, powers, freqs, plot_type=None, qubit_pulse=False, seq=None,  **kwargs):
        self.qubit_info = qubit_info
        self.freqs = freqs
        self.powers = powers
        self.qubit_pulse = qubit_pulse 
        if seq is None:
            seq = Trigger(250)
        self.seq = seq


        if plot_type is None:
            if len(powers) > len(freqs):
                plot_type = POWER
            else:
                plot_type = SPEC
        self.plot_type = plot_type

        super(ROCavSpectroscopy_keysight, self).__init__(1, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('powers', data=powers)
        self.data.create_dataset('freqs', data=freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=(len(powers),len(freqs)))
        self.phasedata = self.data.create_dataset('phases', shape=(len(powers),len(freqs)))


    def generate(self):
        s = Sequence(self.seq)


#        s.append(self.seq)
#        if self.qubit_pulse:
#            s.append(self.qubit_info.rotate(np.pi, 0))
#            s.append(Join([
#                self.seq,
#                self.qubit_info.rotate(np.pi, 0),
#            ]))
#        else:
#            s.append(Combined([
#                Constant(1, 0, chan=self.qubit_info.channels[1]),
#                Constant(1, 0, chan=self.qubit_info.channels[0])
#            ]))
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
        ]))
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=int(self.readout_info.acq_chan)),
#            Constant(self.readout_info.pulse_len, 1, chan=int(self.readout_info.readout_chan_I)),
#            Constant(self.readout_info.pulse_len, 1, chan=int(self.readout_info.readout_chan_Q)),
#        ]))

    
        s.append(Delay(1000))

        sequencer = self.get_sequencer(s)
        seqs = sequencer.render()
        return seqs


   # def dig_load(self, seqs, run=False, ntries=1):
        #A rewrite of the load function in measurement to deal with the new 
        #keysight AWGs.
    def measure(self):
        # Generate and load sequences
        dig = self.instruments['dig']
       # alz.set_interrupt(False)

        seqs = self.generate()
        self.load(seqs)
        self.start_awgs()

        for ipower, power in enumerate(self.powers):
            self.readout_info.rfsource1.set_power(power)
            print 'Power = %s' % (power, )
            time.sleep(2)

            amps = []
            phases = []

            for ifreq, freq in enumerate(self.freqs):
                self.readout_info.rfsource1.set_frequency(freq)
                self.readout_info.rfsource2.set_frequency(freq+50e6)
                time.sleep(0.1)

                ''' the parameter to setup avg shots shouldn't be naverages.
                    naverages is already used inside of the driver. the N parameter passed
                    tells the digitizer how many different points there will be in a measument.
                    The total number of acquisitions is N*naverages.
                '''
                dig.setup_avg_shot()
                dig.arm()
                dig.start_hvi()
                ret = dig.take_avg_shot()
                dig.stop_hvi()
                dig.release_buf()
#                print('inside keysight measurment. ret:')
#                print(ret)
#                try:
#                    while not ret.is_valid():
#                        objsh.helper.backend.main_loop(100)
#                except Exception, e:
##                    alz.set_interrupt(True)
#                    print 'Error: %s' % (str(e), )
#                    return

                IQ = np.average(ret)
                amps.append(np.abs(IQ))
                phases.append(np.angle(IQ, deg=True))
                print 'F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True))

            self.ampdata[ipower,:] = amps
            self.phasedata[ipower,:] = phases

        self.analyze()
    

    """
    def measure(self):
        # Generate and load sequences
        alz = self.instruments['alazar']
        alz.set_interrupt(False)

        seqs = self.generate()
        self.load(seqs)
        self.start_awgs()

        for ipower, power in enumerate(self.powers):
            self.readout_info.rfsource1.set_power(power)
            print 'Power = %s' % (power, )
            time.sleep(2)

            amps = []
            phases = []

            for ifreq, freq in enumerate(self.freqs):
                self.readout_info.rfsource1.set_frequency(freq)
                self.readout_info.rfsource2.set_frequency(freq+50e6)
                time.sleep(1)

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
                print 'I,Q = %.03f, %.03f' % (np.real(IQ), np.imag(IQ))

            self.ampdata[ipower,:] = amps
            self.phasedata[ipower,:] = phases
            

        self.analyze()
    """


    def analyze(self, data=None, ax=None):
        pax = ax if (ax is not None) else plt.figure().add_subplot(111)
        ampdata = data if (data is not None) else self.ampdata
        analysis(self.powers, self.freqs, ampdata, self.phasedata, self.plot_type, ax=pax)
