import numpy as np
import matplotlib.pyplot as plt
from measurement import Measurement2D
#from lib.math import fit
from pulseseq.sequencer import *
from pulseseq.pulselib import *

def analysis(meas, data=None, fig=None):
    zs, fig = meas.get_ys_fig(data, fig)
    zs = zs.reshape(len(meas.ys), len(meas.xs))
    xs, ys = meas.get_plotxsys()
    ax = fig.axes[0]
    plt.sca(ax)
    
    
    pc = ax.pcolormesh(xs, ys, zs, cmap=plt.get_cmap('RdBu'))
    fig.colorbar(pc)

    ax.set_xlim(xs.min(), xs.max())
    ax.set_ylim(ys.min(), ys.max())
#    if meas.zmin is not None and meas.zmax is not None:  (was trying to force set data range for color bar)
#        ax.set_zlim(meas.zmin, meas.zmax())
    ax.set_xlabel(meas.comb1.info.insname + ' detuning (mhz)')
    ax.set_ylabel(meas.comb2.info.insname + ' detuning (mhz)')
    fig.canvas.draw()

class poly_fwm_ssbspec2d(Measurement2D):

    def __init__(self, qubit_info, comb1, comb2, comb1_freqs, comb2_freqs, delay_t,
                 post_delay = 1e3, seq=None, postseq=None, bgcor=False, **kwargs):
        self.qubit_info = qubit_info
        self.comb1 = comb1
        self.comb2 = comb2
        self.comb1_freqs = comb1_freqs
        self.comb2_freqs = comb2_freqs
        self.delay_t = delay_t
        self.post_delay = post_delay
        self.bgcor = bgcor
        
        xs = comb1_freqs
        ys = comb2_freqs

        self.xs = xs/1e6
        self.ys = ys/1e6
 
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq       

        npoints = len(comb1_freqs) * len(comb2_freqs)
        if bgcor: npoints *= 2
        
        infos = [comb.info for comb in [comb1, comb2]]
#        self.temp_infos = []
#        for comb in [comb1, comb2]:
#            infos += comb.get_temp_infos()

        super(poly_fwm_ssbspec2d, self).__init__(npoints, residuals=False, infos=[qubit_info] + infos, **kwargs)
        self.data.set_attrs(
            delay_t=delay_t,
        )
        
    def generate(self):
        s = Sequence()
        
        r = self.qubit_info.rotate_selective
        
        for i, df2 in enumerate(self.comb2_freqs):
            for j, df1 in enumerate(self.comb1_freqs):
                for i_bg in range(2):
                    if i_bg == 1 and not self.bgcor:
                        continue
                    s.append(self.seq)
                    poly_seq = []
                    poly_seq += self.comb1.get_poly_seq(self.delay_t - self.comb1.sigma*4, df1)
                    poly_seq += self.comb2.get_poly_seq(self.delay_t - self.comb2.sigma*4, df2)
                            
                    s.append(Combined(poly_seq))
                    s.append(Delay(self.post_delay))
                    if i_bg == 0:
                        s.append(r(np.pi, X_AXIS))
            
                    if self.postseq:
                        s.append(self.postseq)
                        
                    s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
                    s.append(Delay(2000))

                    
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

        
    def get_ys(self, data=None):
        ys = super(poly_fwm_ssbspec2d, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)