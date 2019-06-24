"""

fwm_info rotation_selective needs to be set to SQUARE
dynamically sets pi_amp in measurement, not from info objects

if we are pulsing the fwm and qubit then the fwm w must match the
qubit w_quasiselective

Jeff Gertler
"""



import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.detunings
    fig.axes[0].plot(-xs/1e6, ys, '.')
    fig.axes[0].set_xlabel('Detuning (MHz)')
    fig.axes[0].set_ylabel('Intensity (AU)')
    fig.canvas.draw()

class cat_pump_ssbspec(Measurement1D):

    def __init__(self, qubit_info, fwm_info, qubit1bob2_info, detunings, delay, ge_amp, fwm_amp, fwm_switch, 
                 pulsed = False, seq=None, postseq=None, bgcor=False, coplay_delay=0, **kwargs):
        self.qubit_info = qubit_info
        self.fwm_info = fwm_info
        self.qubit1bob2_info = qubit1bob2_info
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.detunings = -detunings
        self.xs = detunings / 1e6       # For plot
        self.delay = delay
        assert(delay%4==0)
        self.ge_amp = ge_amp
        self.fwm_amp = fwm_amp
        self.fwm_switch = fwm_switch
        self.pulsed = pulsed
        self.bgcor = bgcor
        self.coplay_delay=coplay_delay

        npoints = len(detunings)
        if bgcor:
            npoints += 1
        super(cat_pump_ssbspec, self).__init__(npoints, residuals=False, infos=(qubit_info, fwm_info, qubit1bob2_info), **kwargs)
        self.data.create_dataset('detunings', data=detunings)
        self.data.set_attrs(
            ge_amp=ge_amp,
            fwm_amp=fwm_amp,
            delay=delay
        )

    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate_quasilective
        rq1b2 = self.qubit1bob2_info.rotate_selective
        


        for i, df in enumerate(self.detunings):
#        for df in self.detunings:
            s.append(Join([self.seq,
                          Constant(500, 1, chan=self.fwm_switch),
                          ]))
            if self.pulsed: 
                g = DetunedSum(self.fwm_info.rotate.base, self.fwm_info.w, chans=self.fwm_info.sideband_channels)                
                if df != 0:
                    period = 1e9 / df
                else:
                    period = 1e50
                g.add(self.fwm_amp, period)
                
                pulse_length = int(self.fwm_info.w * 4)
                num_pulses = int(self.delay / pulse_length)
                temp_seq = Sequence()
                for i in range(num_pulses):
                    temp_seq.append(Combined([g(),             
                                              r(self.ge_amp*np.pi/self.qubit_info.pi_amp_quasilective, 0),
                                              Constant(pulse_length, 1, chan=self.fwm_switch),
                                              ]))
                s.append(Join(temp_seq))
                
            else:
                g = DetunedSum(self.fwm_info.rotate_selective.base, int(self.delay), chans=self.fwm_info.sideband_channels)
                if df != 0:
                    period = 1e9 / df
                else:
                    period = 1e50
                g.add(self.fwm_amp, period)
                
    
                s.append(Join([Combined([g(),
                                        Constant(int(self.delay), self.ge_amp, chan=self.qubit_info.sideband_channels[0]),
#                                        Constant(int(self.delay), self.ge_amp, chan=self.qubit_info.sideband_channels[1]),
                                        Constant(int(self.delay), 1, chan=self.fwm_switch),
                                        ])
                            ]))
            s.append(Delay(5e3))
            s.append(rq1b2(np.pi, X_AXIS))


            if self.postseq:
                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ]))
            s.append(Delay(2000))
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs
    

    def get_ys(self, data=None):
        ys = super(cat_pump_ssbspec, self).get_ys(data)
        if self.bgcor:
            return ys[1:] - ys[0]
        return ys

    def analyze(self, data=None, fig=None):
        analysis(self, data, fig)
        self.fig = fig

