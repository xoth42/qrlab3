import numpy as np
from math import factorial
import matplotlib.pyplot as plt
from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from pulseseq import OCTlib
import lmfit
import math



def analysis(meas, data=None, fig=None): 
    xs = meas.delays
    ys, fig = meas.get_ys_fig(data, fig)

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)




class poly_delay_test(Measurement1D):

    def __init__(self, qubit_info, cav_info1, cav_info2, disp, delays, comb_list = None, 
                 t_ge=0, t_gf=0, detune=0, seq=None, post_delay = 0, postseq=None,
                 mod=1, double_freq=False, bgcor=False, meas_type='wigner', **kwargs):
        self.qubit_info = qubit_info
        self.cav_info1 = cav_info1
        self.cav_info2 = cav_info2
        self.disp = disp
        self.delays = delays
        self.ax1 = ax1
        self.ax2 = ax2
        self.comb_list = comb_list
        self.detune = detune
        self.double_freq=double_freq
        self.bgcor = bgcor
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.postseq = postseq
        self.post_delay = post_delay
        self.xs = self.delays/1e3
        self.t_ge = t_ge
        self.t_gf = t_gf
        self.mod = mod
        self.meas_type = meas_type
        
        infos = [qubit_info, cav_info1, cav_info2]
        if comb_list is not None:
            infos += [comb.info for comb in comb_list]

        npoints = len(self.delays)
        if bgcor:
            npoints *= 2
        super(CavT2_Joint, self).__init__(npoints, infos=infos, **kwargs)
        self.data.create_dataset('delays', data=self.delays)
        if comb_list is not None:
            self.data.set_attrs(
                disp=disp,
                fwm_amps = comb_list[0].amps,
                stark_shift = comb_list[0].stark_shift
            )

    def generate(self): # NEW OCT 01 encoding/decoding

        
        s = Sequence()
        ge = self.qubit_info.rotate
        c1 = self.cav_info1.rotate
        c2 = self.cav_info2.rotate
        for i, delay in enumerate(self.delays):
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue

                temp_seq = self.seq[:]
                if delay > 0:
                    if self.comb_list is not None:
                        poly_seq = []
                        for comb in self.comb_list:
                            poly_seq += comb.get_poly_seq(delay - comb.sigma*4, 0)
                        temp_seq += [Combined(poly_seq)]
                    else:
                        temp_seq += [Delay(delay)]
                        
                temp_seq += [Delay(self.post_delay)]
                
                alpha, beta = self.calc_ab(delay) 
#                alpha = self.disp[0] + 1j * self.disp[1]
#                beta = self.disp[2] + 1j* self.disp[3]
                
                temp_seq += [Combined([c1(np.abs(alpha), np.angle(alpha)), 
                                       c2(np.abs(beta),  np.angle(beta))])]
                
                

    
                
                if i_bg == 0:
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    if self.t_ge > 0:
                        temp_seq += [Delay(self.t_ge)]
                    if self.t_gf > 0:
                        temp_seq += [ef(np.pi, X_AXIS)]
                        temp_seq += [Delay(self.t_gf)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                else:
#                    s.append(ge(np.pi/2, Y_AXIS))
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    if self.t_ge > 0:
                        temp_seq += [Delay(self.t_ge)]
                    if self.t_gf > 0:
                        temp_seq += [ef(np.pi, X_AXIS)]
                        temp_seq += [Delay(self.t_gf)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(-np.pi/2, X_AXIS)]


                if self.postseq:
                    temp_seq += [self.postseq]

                temp_seq += [self.readout_driver.do_get_sequence(self.readout_qubit_info)]
                temp_seq += [Delay(2000)]
                s.append(Join(temp_seq))

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs

    
    def calc_ab(self, delay):
        dphi = 2 * np.pi * self.detune * delay * 1e-9 / self.mod
        
        disp_temp = self.disp[:]
        #not positive this is correct.
        d1 = self.disp[self.ax1]
        d2 = self.disp[self.ax2]
        r = np.sqrt(d1**2 + d2**2)
        phi0 = np.arctan(d2/d1)
        
        
        disp_temp[self.ax1] = r * np.cos(phi0 + dphi)
        disp_temp[self.ax2] = r * np.sin(phi0 + dphi)
        
        alpha = disp_temp[0] + 1j * disp_temp[1]
        beta = disp_temp[2] + 1j* disp_temp[3]
        
        return alpha, beta


    def get_ys(self, data=None):
        ys = super(CavT2_Joint, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return self.fit_params
