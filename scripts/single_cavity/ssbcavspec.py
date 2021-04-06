import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.detunings
    
    try: # This is a placeholder until stes is implemented w/ Alazar.
        fig.axes[0].errorbar(xs/1e6, ys, yerr=meas.get_errorbars(), fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)
    except:
        print('passed no errorbars')
    
    fig.axes[0].plot(xs/1e6, ys)
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()

class SSBCavSpec(Measurement1D):

    def __init__(self, qubit_info, cav_info, detunings, seq=None, postseq=None, extra_info=None, saveas=None, Qswitch_infoB=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.detunings = detunings
        self.extra_info = extra_info
        self.xs = detunings / 1e6       # For plot
        self.saveas = saveas
        self.QswB = Qswitch_infoB

        super(SSBCavSpec, self).__init__(len(detunings), residuals=False, infos=(qubit_info, cav_info,), **kwargs)
        self.data.create_dataset('detunings', data=detunings)

    def generate(self):
        s = Sequence()
        for i, df in enumerate(self.detunings):
            g = DetunedSum(self.cav_info.rotate_selective.base, self.cav_info.w_selective, chans=self.cav_info.sideband_channels)
            if df != 0:
                period = 1e9 / df
            else:
                period = 1e50
            g.add(self.cav_info.pi_amp_selective, period)

            s.append(Join([
                self.seq,
                g(),
                self.qubit_info.rotate_selective(np.pi, 0)
                ]))
            s.append(self.postseq)
            
            s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
            s.append(Delay(2000))
 
#            s.append(Combined([
##                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
 #                   Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ]))

#            s.append(Repeat(Delay(1000), 20))   # wait for alazar acquisition to finish
#            s.append(Combined([
#                Repeat(Constant(8000, 0.6, chan=self.QswB.sideband_channels[0]), 70),
#                Repeat(Constant(8000, 0.6, chan=self.QswB.sideband_channels[1]), 70),
#                Repeat(Constant(8000, 1, chan='1m1'), 70),     # Readout pump tone switch
#                Repeat(Constant(8000, 0.0001, chan=5), 70),         # Qubit/Readout master switch
#            ]))

        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        if self.saveas:
            plt.savefig(self.saveas)
