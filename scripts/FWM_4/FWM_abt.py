# -*- coding: utf-8 -*-
"""
Implentation of an ab^(dagger) term thru 4 wave mixing.
Requires initial state prepared in pre_seq, lets state
for 'delay' before performing q_func on 'which_cavity'

by Jeff Gertler
"""

import numpy as np
import matplotlib.pyplot as plt
from measurement import Measurement2D
#from lib.math import fit
from pulseseq.sequencer import *
from pulseseq.pulselib import *



def analysis(meas, data=None, fig=None):
    zs, fig = meas.get_ys_fig(data, fig)
    zs = zs.reshape(len(meas.xs), len(meas.ys))
    xs, ys = meas.get_plotxsys()
    ax = fig.axes[0]
    plt.sca(ax)
    pc = ax.pcolormesh(xs, ys, zs)
    fig.colorbar(pc)

    ax.set_xlim(xs.min()), xs.max()
    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel(r'$Re \{\alpha \}$')
    ax.set_ylabel(r'$Im \{\alpha \}$')
    fig.canvas.draw()
    
class FWM_abt(Measurement2D):

    def __init__(self, qubit_info, a_info, b_info, FWM_info, xvec, yvec, delay, which_cavity = 'b',
                 seq=None, postseq=None, saveas=None, **kwargs):
        self.qubit_info = qubit_info
        self.a_info = a_info
        self.b_info = b_info
        self.FWM_info = FWM_info
        self.which_cavity = which_cavity

        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.delay = delay
        self.saveas = saveas

        xs = xvec
        ys = yvec

        XS, YS = np.meshgrid(xs, ys)
        self.displacements = -(XS + 1j*YS)
        self.xs = xs
        self.ys = ys

        npoints = self.displacements.size
        super(FWM_abt, self).__init__(npoints, infos=(qubit_info, a_info, b_info, FWM_info), residuals=False, **kwargs)
        self.data.create_dataset('displacements', data=self.displacements, dtype=np.complex)
        self.data.set_attrs(
            delay=delay,
            which_cavity = which_cavity
        )
    
    
    
    
    def generate(self):
        '''
        If bg = True generate background measurement, i.e. no qubit pi pulse
        '''

        s = Sequence()

        r = self.qubit_info.rotate_selective
        if(self.which_cavity == 'a'):
            c = self.a_info.rotate
        elif(self.which_cavity == 'b'):
            c = self.b_info.rotate
            
        fwm = self.FWM_info.rotate
        

        for i, alpha in enumerate(self.displacements.flatten()):
            # generate the initial state
            s.append(self.seq)
            
            # Perform the abt                
#            s.append(Delay(self.delay))
            s.append(fwm(np.pi, X_AXIS))
            
            # Displace for the q_func
            s.append(c(np.abs(alpha), np.angle(alpha)))

            if self.postseq:
                s.append(self.postseq)
                
            s.append(Combined([
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
            ]))
            s.append(Delay(1000))

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs
        


    def get_ys(self, data=None):
        ys = super(FWM_abt, self).get_ys(data)
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)