from measurement import Measurement1D
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from lib.math import fit
import time
import objectsharer as objsh
import os
import config
import numpy as np

SPEC   = 0
POWER  = 1

class roic_roomtemp_testing(Measurement1D):
    '''
    Perform qubit spectroscopy.

    The frequency of <qubit_rfsource> will be swept over <q_freqs> and
    different read-out powers <ro_powers> will be set on readout_info.rfsource1.

    The spectroscopy pulse has length <plen> ns.

    If <seq> is specified it is played at the start (should start with a trigger)
    If <postseq> is specified it is played at the end, right before the read-out
    pulse.
    '''

    def __init__(self, qubit_rfsource, qubit_info, qubit2_info, q_freqs, ro_powers,
                 plen_RF, plen_LO, amp_RF=1, amp_LO=1, phase=0, seq=None, postseq=None,
                 pow_delay=1, freq_delay=0.1, plot_type=None,
                 **kwargs):
        self.qubit_rfsource = qubit_rfsource
        self.qubit_info = qubit_info
        self.qubit2_info = qubit2_info
        self.ro_powers = ro_powers
        self.q_freqs = q_freqs
        self.plen_RF = plen_RF
        self.plen_LO = plen_LO
        self.amp_RF = amp_RF
        self.amp_LO = amp_LO
        self.phase = phase
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

        super(roic_roomtemp_testing, self).__init__(1, infos=(qubit_info, qubit2_info,), **kwargs)
        self.data.create_dataset('powers', data=ro_powers)
        self.data.create_dataset('freqs', data=q_freqs)
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(ro_powers),len(q_freqs)])
        self.phasedata = self.data.create_dataset('phases', shape=[len(ro_powers),len(q_freqs)]) 

    def generate(self):
        s = Sequence(self.seq)
        chs = self.qubit_info.sideband_channels
#        chs2 = self.qubit2_info.sideband_channels

#        pre_LO = Combined([
#                Constant(self.plen_LO, self.amp_LO, chan=chs2[0]),
#                Constant(self.plen_LO, self.amp_LO, chan=chs2[1])
#        ])
        
        
        RF = Combined([
            Constant(self.plen_RF, self.amp_RF * np.cos(self.phase), chan=chs[0]),
            Constant(self.plen_RF, self.amp_RF * np.sin(self.phase), chan=chs[1]),
#            Constant(self.plen_RF, self.amp_LO, chan=chs2[0]),
#            Constant(self.plen_RF, self.amp_LO, chan=chs2[1]),
            Constant(self.plen_RF, 1, chan='1m1'),
            Constant(self.plen_RF, 1, chan='5m1')
        ])
    
#        LO = Constant(self.plen_LO/2, self.amp_LO, chan=chs2[0])
        
        s.append(RF)
#        s.append(self.readout_driver.do_get_sequence())
        
#        s.append(Join([pre_LO, RF]))

        if self.postseq:
            s.append(self.postseq)
                      

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def measure(self, threshold=100):
        dig = self.instruments['dig']
        self.threshold = threshold

        # Generate and load sequences
        seqs = self.generate()
        self.stop_awgs()
        self.load(seqs)
        self.start_awgs()

        for ipower, power in enumerate(self.ro_powers):
            self.readout_info.rfsource1.set_power(power)
            print 'Power = %s' % (power, )
            time.sleep(self.pow_delay)

            I_traces = []
            Q_traces = []
            count = 0
            for freq in self.q_freqs:
                self.qubit_rfsource.set_frequency(freq)
                time.sleep(self.freq_delay)
                
                dig.setup_raw_shot_ROIC(I_chan=3, Q_chan=4)
                dig.arm()
                dig.start_hvi()
#                ret = dig.take_avg_shot()
                I, Q = dig.take_raw_shot_ROIC(I_chan=3, Q_chan=4)
                #Yingying to add a main loop, suggesting to help with the spectroscopy crash
                
                try:
                    while not I.is_valid():
                        objsh.helper.backend.main_loop(100)
                except:
                    dig.set_interrupt(True)

                dig.release_buf()


#                IQ = np.average(ret)
#                amps.append(np.abs(IQ))
#                phases.append(np.angle(IQ, deg=True))
                count += 1
                print(count)
                   
                I_traces.append(I)
                Q_traces.append(Q)
                
            self.I_data = I_traces

            self.Q_data = Q_traces
                

        self.analyze()

    def analyze(self):
        threshold_list = []; Itrig=0; Qtrig=0
        roic_stats = []
        for i in range(len(self.q_freqs)):
            if np.max(self.I_data[i]) > self.threshold:
                Itrig = 1
            else:
                Itrig = 0
            if np.max(self.Q_data[i]) > self.threshold:
                Qtrig = 1
            else:
                Qtrig = 0
            
            threshold_list.append([Itrig,Qtrig])
        probs = (np.sum(threshold_list, axis=0)/float(len(self.q_freqs))).tolist()
        iprobs = probs[0]
        qprobs = probs[1]
        temp = [self.phase*180/np.pi,iprobs,qprobs]
        print(temp)
        roic_stats.append(temp)
        
        
        plt.figure()
        for i in range(len(self.q_freqs)):
            plt.plot(self.I_data[i], label='I_data')
            plt.plot(self.Q_data[i], label='Q_data')
        plt.legend()
     
