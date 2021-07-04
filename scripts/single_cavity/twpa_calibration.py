from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import objectsharer as objsh
import time
import numpy as np




#np.append(twpa_powers, 2* twpa_powers[-1] - twpa_powers[-2])
#np.append(twpa_freqs, 2* twpa_freqs[-1] - twpa_freqs[-2])
#x, y = np.meshgrid(np.append(twpa_powers, 2* twpa_powers[-1] - twpa_powers[-2]),
#                   np.append(twpa_freqs, 2* twpa_freqs[-1] - twpa_freqs[-2]))
#pl.pcolormesh(x, y, data.T)
#pl.xlabel('twpa powers')
#pl.ylabel('twpa frequencies')
#
#print(np.max(data), twpa_powers[np.unravel_index(data.argmax(), data.shape)[0]],
#                    twpa_freqs[np.unravel_index(data.argmax(), data.shape)[1]])


def analysis(twpa_powers, twpa_freqs, ampdata, ax=None):
    if ax is None:
        ax = plt.figure().add_subplot(111)
    data = ampdata[:]
    x, y = np.meshgrid(np.append(twpa_powers, 2* twpa_powers[-1] - twpa_powers[-2]),
                   np.append(twpa_freqs, 2* twpa_freqs[-1] - twpa_freqs[-2]))
    ax.pcolormesh(x, y, data.T)
    ax.set_xlabel('twpa powers')
    ax.set_ylabel('twpa frequencies')
    
    print(('max power', twpa_powers[np.unravel_index(data.argmax(), data.shape)[0]],
          'max_freq',  twpa_freqs[np.unravel_index(data.argmax(), data.shape)[1]]))
    
    

class twpa_calibration(Measurement1D):

    def __init__(self, qubit_info, power, freq, twpa_powers, twpa_freqs, twpa_pump, plot_type=None, qubit_pulse=False, seq=None,  **kwargs):
        self.qubit_info = qubit_info
        self.freq = freq
        self.power = power
        self.twpa_powers = twpa_powers
        self.twpa_freqs = twpa_freqs
        self.twpa_pump = twpa_pump
        self.qubit_pulse = qubit_pulse
        if seq is None:
            seq = Trigger(250)
        self.seq = seq



        self.plot_type = plot_type

        super(twpa_calibration, self).__init__(1, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('twpa_powers', data=twpa_powers)
        self.data.create_dataset('twpa_freqs', data=twpa_freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=(len(twpa_powers),len(twpa_freqs)))


    def generate(self):
        s = Sequence(self.seq)

#        s.append(self.seq)
        if self.qubit_pulse:
            s.append(self.qubit_info.rotate(np.pi, 0))
#            s.append(Join([
#                self.seq,
#                self.qubit_info.rotate(np.pi, 0),
#            ]))
#        else:
#            s.append(Combined([
#                Constant(1, 0, chan=self.qubit_info.channels[1]),
#                Constant(1, 0, chan=self.qubit_info.channels[0])
#            ]))
#        s.append(Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan))
#        s.append(Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan))
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
        ]))
    
        s.append(Delay(1000))


        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs



    def measure(self):
        # Generate and load sequences
        alz = self.instruments['alazar']
        alz.set_interrupt(False)
        try:
            dig = self.instruments['dig']
            dig.start_hvi()
        except:
            print('no digitizer object for trigger')

        self.readout_info.rfsource1.set_power(self.power)
        self.readout_info.rfsource1.set_frequency(self.freq)
        self.readout_info.rfsource2.set_frequency(self.freq+50e6)

        seqs = self.generate()
        self.load(seqs)
        self.start_awgs()


        for i_twpa_power, twpa_power in enumerate(self.twpa_powers):
            self.twpa_pump.set_power(twpa_power)
            print('twpa_power = %s' % (twpa_power, ))
            time.sleep(2)
            for i_twpa_freq, twpa_freq in enumerate(self.twpa_freqs):
                self.twpa_pump.set_frequency(twpa_freq)
                time.sleep(2)
                    
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
                print('F = %.03f MHz --> re = %.01f, amp = %.1f, angle = %.01f' % (twpa_freq / 1e6, np.real(IQ), np.abs(IQ), np.angle(IQ, deg=True)))
                print('I,Q = %.03f, %.03f' % (np.real(IQ), np.imag(IQ)))

 
                self.ampdata[i_twpa_power,i_twpa_freq] = np.abs(IQ)
                    
        
        self.analyze()

    def analyze(self, data=None, ax=None):
        analysis(self.twpa_powers, self.twpa_freqs, self.ampdata)
