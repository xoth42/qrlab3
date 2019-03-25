import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import mclient

qubit_info = mclient.get_qubit_info('qubit1ge')


class Testexp(Measurement1D):

    def __init__(self, qubit_info, amps, update=False, seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, postseq=None, selective=False, **kwargs):
        self.qubit_info = qubit_info
        self.amps = amps
        self.xs = amps
        self.update_ins = update
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis

        super(Testexp, self).__init__(len(amps), infos=qubit_info, **kwargs)
        self.data.create_dataset('amps', data=amps)

    def generate(self):
        s = Sequence()

        for i, amp in enumerate(self.amps):
            s.append(self.seq)
            if self.selective==1:
                s.append(Repeat(self.qubit_info.rotate_selective(0, self.r_axis, amp=amp), self.repeat_pulse))
            elif self.selective==0.5:
                s.append(Repeat(self.qubit_info.rotate_quasilective(0, self.r_axis, amp=amp), self.repeat_pulse))
            else:
                s.append(Repeat(self.qubit_info.rotate(0, self.r_axis, amp=amp), self.repeat_pulse))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Delay(20))
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))

        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

expt = Testexp(qubit_info, np.linspace(0, 1, 11), plot_seqs=True,
                       update=False)
seqs = expt.generate()

