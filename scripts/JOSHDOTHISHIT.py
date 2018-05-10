import mclient
from pulseseq.sequencer import sequencer
import time
import numpy as np
import logging
import awgloader


def generate(self, amp):
    s = Sequence()
    s.append(Trigger(250))
    s.append(self.cav_info.rotate(amp, 0))

    if self.Qswitchseq:
        s.append(self.Qswitchseq)
    s.append(self.qubit_info.rotate_selective(np.pi, 0))

    s.append(Combined([
        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
    ]))

    s = self.get_sequencer(s)
    seqs = s.render()
    if self.plot_seqs:
        s.plot_seqs(seqs)

    self.seqs = seqs
    return seqs



def get_awg_loader(self):
    '''
    Detect all AWGs and map channels:
    AWG1 gets channel 1-4, AWG2 5-8, etc.
    '''
    if self._awgloader:
        return self._awgloader

    if hasattr(config,'awg_fileload') and hasattr(config,'dot_awg_path'):
        fl = config.awg_fileload
        fp = config.dot_awg_path
    else:
        fl = False
        fp = None

    l = awgloader.AWGLoader(bulkload=config.awg_bulkload,
                            fileload=fl, dot_awg_path=fp)
    base = 1
    for i in range(1, 5):
        awg = self.instruments['AWG%d'%i]
        if awg:
            chanmap = {1:base, 2:base+1, 3:base+2, 4:base+3}
            logging.info('Adding AWG%d, channel map: %s', i, chanmap)
            l.add_awg(awg, chanmap)
            base += 4

    self._awgloader = l
    return l

def load(self, seqs, run=False, ntries=1):
    '''
    Load sequences <seqs> to awgs.
    awgs are located from the instruments list and should be named
    AWG1, AWG2, ... (up to 4 currently).
    '''
    
    start = time.clock()
    l = get_awg_loader()
    for i in range(ntries):
        try:
            l.load(seqs)
            break
        except Exception, e:
            logging.warning('Loading failed (%s), retrying', str(e))
            time.sleep(1)



dig = mclient.instruments['dig']
awg = mclient.instruments['AWG']
readout = mclient.instruments['brick2']
ref = mclient.instruments['brick5']


sequence = generate(1)


load(sequence)

'''

for f in freqs:

    rf.setfreq
    
    dig.setup shots
    
    dig.arm
    
    awg.run
    
    data =dig.takeshots

plot data
'''




