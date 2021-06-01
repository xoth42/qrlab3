import numpy as np
import matplotlib.pyplot as plt
from measurement import Measurement1D
#from lib.math import fit
from pulseseq.sequencer import *
from pulseseq.pulselib import *

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs

    fig.axes[0].plot(xs, ys, 'ks', ms=3, linestyle='-', markerfacecolor='red' )
    try: # This is a placeholder until stes is implemented w/ Alazar.
        fig.axes[0].errorbar(xs, ys, yerr=meas.get_errorbars(), fmt='.', 
                         markersize = 0, ecolor='grey', linewidth=1)
    except:
        print('passed no errorbars')  

class JointTest(Measurement1D):

    def __init__(self, qubit_info, ef_info, ge_times,
                 seq=None, delay=0, saveas=None, bgcor=False,
                 zmin=None, zmax=None, **kwargs):
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        self.ge_times = ge_times
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.delay = delay
        self.saveas = saveas
        self.bgcor = bgcor
        self.zmin=zmin
        self.zmax=zmax
        
        self.xs = ge_times
        
 
        npoints = len(ge_times)
        if bgcor:
            npoints *= 2
        super(JointTest, self).__init__(npoints, infos=(qubit_info), residuals=False, **kwargs)
        self.data.create_dataset('ge_times', data=self.ge_times, dtype=np.float)

        self.data.set_attrs(
            delay=delay,
            bgcor=bgcor
        )

    def generate(self):
        '''
        If bg = True generate background measurement, i.e. without qubit pi pulse
        '''

        s = Sequence()

        ge = self.qubit_info.rotate
        ef = self.ef_info.rotate
        for t_ge in self.ge_times:
            for i_bg in range(2):
                    
                if i_bg == 1 and not self.bgcor:
                    continue
                
                temp_seq = self.seq[:]

                if i_bg == 0:
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    if t_ge > 0:
                        temp_seq += [Delay(t_ge)]
#                    if self.t_gf > 0:
#                        temp_seq += [ef(np.pi, X_AXIS)]
#                        temp_seq += [Delay(self.t_gf)]
#                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                else:
#                    s.append(ge(np.pi/2, Y_AXIS))
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    if t_ge > 0:
                        temp_seq += [Delay(t_ge)]
#                    if self.t_gf > 0:
#                        temp_seq += [ef(np.pi, X_AXIS)]
#                        temp_seq += [Delay(self.t_gf)]
#                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(-np.pi/2, X_AXIS)]

                if self.delay:
                    temp_seq += [Delay(self.delay)]
                
                s.append(Join(temp_seq))
#                temp_seq += [Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ])]
                s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
                s.append(Delay(2000))
                

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs


    def get_ys(self, data=None):
        ys = super(JointTest, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys
    
    
    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
