import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.detunings
    fig.axes[0].plot(xs/1e6, ys)
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()

class SSBSpec(Measurement1D):

    def __init__(self, qubit_info, detunings, seq=None, extra_info=None, saveas=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.detunings = detunings
        self.extra_info = extra_info
        self.xs = detunings / 1e6       # For plot
        self.saveas = saveas

        super(SSBSpec, self).__init__(len(detunings), residuals=False, **kwargs)
        self.data.create_dataset('detunings', data=detunings)

    def generate(self):
        s = Sequence()

        for i, df in enumerate(self.detunings):
            g = DetunedGaussians(self.qubit_info.sigma, chans=self.qubit_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add_gaussian(0, period, area=self.qubit_info.rotate.pi_area)

            s.append(Join([
                self.seq,
                g(),
                Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])]))

        s = Sequencer(s)
        seqs = s.render()
        if self.qubit_info.ssb:
            self.qubit_info.ssb.modulate(seqs)
        if self.extra_info and self.extra_info.ssb:
            self.extra_info.ssb.modulate(seqs)
#        s.plot_seqs(seqs)

        self.seqs = seqs
        return seqs

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        if self.saveas:
            plt.savefig(self.saveas)
