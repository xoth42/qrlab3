"""
time domain of the decay for all 6 qubit bloch points

Jeff Gertler
"""


import numpy as np
from math import factorial
import matplotlib.pyplot as plt
#from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
import lmfit
import math
import time
import objectsharer as objsh
from scipy.linalg import fractional_matrix_power

def final_rotation(axis, kerr_correction, r):
    if axis is '-z':
        return [r(np.pi, X_AXIS)]
    elif axis is 'z':
        return []
    elif kerr_correction == 0:
        if axis is 'x':
            return [r(np.pi/2, -Y_AXIS)]
        elif axis is 'y':
            return [r(np.pi/2, X_AXIS)]
        elif axis is 'mx':
            return [r(np.pi/2, Y_AXIS)]
        elif axis is 'my':
            return [r(-np.pi/2, X_AXIS)]            
    elif kerr_correction == 1:
        if axis is 'x':
            return [r(-np.pi/2, -X_AXIS)] # Does this work?  -X_AXIS = X_AXIS = 0 !
        elif axis is 'y':
            return [r(np.pi/2, -Y_AXIS)]
        elif axis is 'mx':
            return [r(np.pi/2, X_AXIS)]
        elif axis is 'my':
            return [r(np.pi/2, Y_AXIS)]
    elif kerr_correction == 2:
        if axis is 'x':
            return [r(np.pi/2, Y_AXIS)]
        elif axis is 'y':
            return [r(-np.pi/2, -X_AXIS)]
        elif axis is 'mx':
            return [r(np.pi/2, -Y_AXIS)]
        elif axis is 'my':
            return [r(np.pi/2, X_AXIS)]    
    elif kerr_correction == 3:
        if axis is 'x':
            return [r(np.pi/2, X_AXIS)]
        elif axis is 'y':
            return [r(np.pi/2, Y_AXIS)]
        elif axis is 'mx':
            return [r(np.pi/2, -X_AXIS)]
        elif axis is 'my':
            return [r(np.pi/2, -Y_AXIS)]
    else: 
        return []

def density_matrix(x, y, z):
    I = np.array([[1,0],[0,1]])
    sigmax = np.array([[0,1],[1,0]])
    sigmay = np.array([[0,-1j],[1j,0]])
    sigmaz = np.array([[1,0],[0,-1]])
    return .5 * (I + x * sigmax + y * sigmay + z*sigmaz)

def fidelity(a, b):
    sqrta = fractional_matrix_power(a, .5)
    m = np.matmul(np.matmul(sqrta, b), sqrta)
    return np.power(np.trace(fractional_matrix_power(m, .5)), 2)

def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    
    xs = meas.delays
    num_delays = len(xs)
    XSv = ys[0*num_delays : 1*num_delays]
    YSv = ys[1*num_delays : 2*num_delays]
    ZSv = ys[2*num_delays : 3*num_delays]
    mXSv = ys[3*num_delays : 4*num_delays]
    mYSv = ys[4*num_delays : 5*num_delays]
    mZSv = ys[5*num_delays : 6*num_delays]    
    
    equators = (XSv+YSv+ZSv+mXSv+mYSv+mZSv) / 6.0
    print equators
    
    pf = np.polyfit(meas.delays, equators, 1)
    eq_values = pf[0]*meas.delays + pf[1]
    e_values = meas.e_value * np.ones(num_delays)
    g_values = eq_values*2 - meas.e_value
    print g_values
    
    XS = (g_values - XSv) / (g_values - e_values) * 2 - 1
    YS = (g_values - YSv) / (g_values - e_values) * 2 - 1
    ZS = (g_values - ZSv) / (g_values - e_values) * 2 - 1
    mXS = (g_values - mXSv) / (g_values - e_values) * 2 - 1
    mYS = (g_values - mYSv) / (g_values - e_values) * 2 - 1
    mZS = (g_values - mZSv) / (g_values - e_values) * 2 - 1
    fig.axes[0].plot(meas.delays/1e3, XS, label = 'sigmaX')
    fig.axes[0].plot(meas.delays/1e3, YS, label = 'sigmaY')
    fig.axes[0].plot(meas.delays/1e3, ZS, label = 'sigmaZ')
    fig.axes[0].plot(meas.delays/1e3, mXS, label = '-sigmaX')
    fig.axes[0].plot(meas.delays/1e3, mYS, label = '-sigmaY')
    fig.axes[0].plot(meas.delays/1e3, mZS, label = '-sigmaZ')
    
    f = np.zeros_like(XS)
    
    rXS = (XS-mXS)/2.
    rYS = (YS-mYS)/2.
    rZS = (ZS-mZS)/2.    
    
    if meas.target_state is 'purity':
        for i in range(len(rXS)):
            f[i] = np.sqrt(rXS[i]**2 + rYS[i]**2 + rZS[i]**2)
            fig.axes[1].set_ylim(0, 1)

    else:
        for i in range(len(rXS)):
            f[i] = fidelity(density_matrix(meas.target_state[0], meas.target_state[1], meas.target_state[2]),
                            density_matrix(rXS[i], rYS[i], rZS[i]))
            fig.axes[1].set_ylim(0.4, 1)
            
    fig.axes[1].plot(meas.delays/1e3, f, '^')

    params = lmfit.Parameters()
    if meas.background_fidelity:
        params.add('ofs', value=meas.background_fidelity, vary=False)
    else:
        params.add('ofs', value=np.min(f))
    params.add('amplitude', value=np.max(f))
    params.add('tau', value=meas.delays[-1]/2.0, min=50.0)
    result = lmfit.minimize(exp_decay, params, args=(meas.delays, f))
    lmfit.report_fit(result.params)

    fig.axes[1].plot(meas.delays/1e3, -exp_decay(result.params, meas.delays, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
    
    
    if meas.t2_check is not None:
        equators = (ys[6*num_delays : 7*num_delays] + ys[7*num_delays : 8*num_delays])*0.5
        print equators
        
#        pf = np.polyfit(meas.delays, equators, 1)
        eq_value = np.mean(equators)#pf[0]*meas.delays + pf[1]
        e_value = meas.e_value #* np.ones(num_delays)
        g_value = eq_value*2 - meas.e_value
        print g_value
#        pf = np.polyfit(meas.delays, equators, 2)
#        eq_values = pf[0]*meas.delays**2 + pf[1]*meas.delays + pf[2]                
#        e_values = meas.e_value
#        g_values = eq_values*2 - meas.e_value
    
#        proj_plus = ys[6*num_delays : 7*num_delays]
#        proj_minus = ys[7*num_delays : 8*num_delays]
        proj_minus = (g_value - ys[6*num_delays : 7*num_delays]) / (g_value - e_value) * 2 - 1 
        proj_plus = (g_value - ys[7*num_delays : 8*num_delays]) / (g_value - e_value) * 2 - 1
        proj = (proj_plus-proj_minus)/2.0
        fig.axes[1].plot(meas.delays/1e3, proj, 's')
    
        fig.axes[0].plot(meas.delays/1e3, proj_plus, label = 'cavT2 plus')
        fig.axes[0].plot(meas.delays/1e3, proj_minus, label = 'cavT2 minus')
        
        params = lmfit.Parameters()
        params.add('ofs', value=0.0, vary=False)
        params.add('amplitude', value=np.max(proj))
        params.add('tau', value=meas.delays[-1]/2.0, min=50.0)
        result = lmfit.minimize(exp_decay, params, args=(meas.delays, proj))
        lmfit.report_fit(result.params)
        fig.axes[1].plot(meas.delays/1e3, -exp_decay(result.params, meas.delays, 0), 
                        label='t2 Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
        
    fig.axes[0].set_ylim(-1, 1)
    fig.axes[0].legend()
    fig.axes[1].legend(loc=0)

    return None

def analysis_jeff(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    
    xs = meas.delays
    num_delays = len(xs)
    
    equators = (ys[2*num_delays : 3*num_delays] + ys[3*num_delays : 4*num_delays])*0.5
    print equators       
    e_values = meas.e_value * np.ones(num_delays)
    g_values = equators*2 - e_values
    print g_values
    
    XS = (g_values - ys[0*num_delays : (1)*num_delays]) / (g_values - e_values) * 2 - 1
    YS = (g_values - ys[1*num_delays : (2)*num_delays]) / (g_values - e_values) * 2 - 1
    ZS = (g_values - ys[2*num_delays : (3)*num_delays]) / (g_values - e_values) * 2 - 1
    mZS = (g_values - ys[3*num_delays : (4)*num_delays]) / (g_values - e_values) * 2 - 1
    fig.axes[0].plot(meas.delays/1e3, XS, label = 'sigmaX')
    fig.axes[0].plot(meas.delays/1e3, YS, label = 'sigmaY')
    fig.axes[0].plot(meas.delays/1e3, ZS, label = 'sigmaZ')
    fig.axes[0].plot(meas.delays/1e3, mZS, label = '-sigmaZ')
    fig.axes[0].set_ylim(-1, 1)
    fig.axes[0].legend()
    f = np.zeros_like(XS)
    if meas.target_state is 'purity':
        for i in range(len(XS)):
            f[i] = np.sqrt(XS[i]**2 + YS[i]**2 + ZS[i]**2)
            fig.axes[1].set_ylim(0, 1)

    else:
        for i in range(len(XS)):
            f[i] = fidelity(density_matrix(meas.target_state[0], meas.target_state[1], meas.target_state[2]),
                            density_matrix(XS[i], YS[i], ZS[i]))
            fig.axes[1].set_ylim(0.4, 1)

            
    fig.axes[1].plot(meas.delays/1e3, f)

    params = lmfit.Parameters()
    if meas.background_fidelity:
        params.add('ofs', value=meas.background_fidelity, vary=False)
    else:
        params.add('ofs', value=np.min(f))
    params.add('amplitude', value=np.max(f))
    params.add('tau', value=meas.delays[-1]/2.0, min=50.0)
    result = lmfit.minimize(exp_decay, params, args=(meas.delays, f))
    lmfit.report_fit(result.params)

    fig.axes[1].plot(meas.delays/1e3, -exp_decay(result.params, meas.delays, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
    fig.axes[1].legend(loc=0)

    return None


def analysis_chen(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    
    xs = meas.delays
    num_delays = len(xs)
    
    if meas.measure_ge:
        meas.g_value = ys[4*num_delays: 5*num_delays].mean()
        meas.e_value = ys[5*num_delays: 6*num_delays].mean()
        print "g_value=", meas.g_value, "e_value=", meas.e_value, "\n" 
    
    if meas.target_state is None:
        for i, axis in enumerate(['x', 'y', 'z']):
            YS =  ys[i*num_delays : (i+1)*num_delays]
            if meas.g_value is not None:
                YS = (meas.g_value - YS) / (meas.g_value - meas.e_value) * 2 - 1
    
            plt.plot(xs/1e3, YS, ms=3, label = axis)
            
            Xs = xs[:num_delays]
            YS = YS[:num_delays]
            params = lmfit.Parameters()
            params.add('ofs', value=np.min(YS))
            params.add('amplitude', value=np.max(YS))
            params.add('tau', value=Xs[-1]/2.0, min=50.0)
            result = lmfit.minimize(exp_decay, params, args=(Xs, YS))
    #        lmfit.report_fit(params)
    #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
            lmfit.report_fit(result.params)
    
            plt.plot(Xs/1e3, -exp_decay(result.params, Xs, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
        plt.legend(loc=0)
        plt.ylabel('Intensity [AU]')
        plt.xlabel('Time [us]')
        return result.params
    
    else:
        '''We perform a second order polynomial fit to smooth our extracted equator voltage (in the presence of possible spurious photons) vs delay time.
        We assume |e> state voltage does not change much with spurious photons, but |g> state does.'''
        equators = (ys[2*num_delays : 3*num_delays] + ys[3*num_delays : 4*num_delays])*0.5
        print equators
        pf = np.polyfit(meas.delays, equators, 2)
        eq_values = pf[0]*meas.delays**2 + pf[1]*meas.delays + pf[2]                
        e_values = meas.e_value
        g_values = eq_values*2 - meas.e_value
        print g_values
        
        XS = (g_values - ys[0*num_delays : (1)*num_delays]) / (g_values - e_values) * 2 - 1
        YS = (g_values - ys[1*num_delays : (2)*num_delays]) / (g_values - e_values) * 2 - 1
        ZS = (g_values - ys[2*num_delays : (3)*num_delays]) / (g_values - e_values) * 2 - 1
        mZS = (g_values - ys[3*num_delays : (4)*num_delays]) / (g_values - e_values) * 2 - 1
        fig.axes[0].plot(meas.delays/1e3, XS, label = 'sigmaX')
        fig.axes[0].plot(meas.delays/1e3, YS, label = 'sigmaY')
        fig.axes[0].plot(meas.delays/1e3, ZS, label = 'sigmaZ')
        fig.axes[0].plot(meas.delays/1e3, mZS, label = '-sigmaZ')
        fig.axes[0].set_ylim(-1, 1)
        fig.axes[0].legend()
        f = np.zeros_like(XS)
        for i in range(len(XS)):
            f[i] = fidelity(density_matrix(meas.target_state[0], meas.target_state[1], meas.target_state[2]),
                            density_matrix(XS[i], YS[i], ZS[i]))
        fig.axes[1].plot(meas.delays/1e3, f)

        params = lmfit.Parameters()
        if meas.background_fidelity:
            params.add('ofs', value=meas.background_fidelity, vary=False)
        else:
            params.add('ofs', value=np.min(f))
        params.add('amplitude', value=np.max(f))
        params.add('tau', value=meas.delays[-1]/2.0, min=50.0)
        result = lmfit.minimize(exp_decay, params, args=(meas.delays, f))
        lmfit.report_fit(result.params)

        fig.axes[1].plot(meas.delays/1e3, -exp_decay(result.params, meas.delays, 0), label='Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))
        fig.axes[1].legend(loc=0)
        fig.axes[1].set_ylim(0.4, 1)
        
        if meas.t2_check is not None:
            equators = (ys[4*num_delays : 5*num_delays] + ys[5*num_delays : 6*num_delays])*0.5
            pf = np.polyfit(meas.delays, equators, 2)
            eq_values = pf[0]*meas.delays**2 + pf[1]*meas.delays + pf[2]                
            e_values = meas.e_value
            g_values = eq_values*2 - meas.e_value

            proj = ys[4*num_delays : 5*num_delays] / (g_values - e_values) * 2 - 1
            fig.axes[1].plot(meas.delays/1e3, proj)

            fig.axes[0].plot(meas.delays/1e3, proj, label = 't2 plus')
            fig.axes[0].plot(meas.delays/1e3, ys[5*num_delays : 6*num_delays] / (g_values - e_values) * 2 - 1, label = 't2 minus')
            
            params = lmfit.Parameters()
            params.add('ofs', value=np.min(f))
            params.add('amplitude', value=np.max(f))
            params.add('tau', value=meas.delays[-1]/2.0, min=50.0)
            result = lmfit.minimize(exp_decay, params, args=(meas.delays, proj))
            lmfit.report_fit(result.params)
            fig.axes[1].plot(meas.delays/1e3, -exp_decay(result.params, meas.delays, 0), 
                            label='t2 Fit, tau = %.03f us +/- %.03f us '%(result.params['tau'].value/1000.0, result.params['tau'].stderr/1000.0))

            

        return None


class time_bloch(Measurement1D):

    def __init__(self, qubit_info, delays, g_value=None, e_value=None,
                 seq=None, postseq=None, target_state=None, 
                 background_fidelity=None, comb_list=None, measure_ge=False,
                 kerr_correction=None, rotations = None, 
                 secondary_decode = False, t2_check = None,
                 **kwargs):
        self.qubit_info = qubit_info
        self.delays = delays
        self.target_state = target_state
        self.g_value = g_value
        self.e_value = e_value
        if seq is None:
            seq = [Trigger(200)]
        self.seq = seq
        self.postseq = postseq
        self.comb_list = comb_list
        self.background_fidelity = background_fidelity
        if kerr_correction is None:
            kerr_correction = [0] * len(delays)
        self.kerr_correction = kerr_correction
        self.rotations = rotations
        self.secondary_decode = secondary_decode
        self.t2_check = t2_check
        
        self.measure_ge = measure_ge
        if self.measure_ge:    
            n_rep = 8
        else:
            n_rep = 6
            
        if t2_check is not None:
            n_rep += 2
            

        xs_single = self.delays/1e3
        self.xs = np.tile(xs_single, n_rep)
        npoints = len(self.delays) * n_rep
        
        infos = [qubit_info]
        if comb_list is not None:
            infos += [comb.info for comb in comb_list]
        super(time_bloch, self).__init__(npoints, infos= infos, **kwargs)
        
        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(delays)])
        self.data.create_dataset('delays', data=self.delays)
        if comb_list is not None:
            self.data.set_attrs(
                                fwm_amps = comb_list[0].amps,
                                ge_amps = comb_list[1].amps,
                                stark_shift = comb_list[0].stark_shift
                                )
    
    def generate(self):
        r = self.qubit_info.rotate
        s = Sequence()
        for axis in ['x', 'y', 'z', 'mx', 'my', 'mz']:
            for i, dt in enumerate(self.delays):
                s_temp = self.seq[:]
                
                if dt > 0:
                    if self.comb_list is None:
                        s_temp += [Delay(dt)]
                    else:
                        poly_seq = []
                        for c in self.comb_list:
                            poly_seq += c.get_poly_seq(dt - c.sigma*4, 0)
                        s_temp += [Combined(poly_seq)]
                                        
                if self.postseq:
                    if self.rotations is not None:
                        s_temp += [self.postseq(phase = self.rotations[i], secondary = (self.secondary_decode and i%2==1))]
                    else:
#                        s_temp += [self.postseq(secondary = (self.secondary_decode and i%2==1))]
                        s_temp += [self.postseq()]
                
                '''Somehow the final_rotation function no longer works, returns an error of Nonetype object not iterable'''
#                print(axis, dt, self.kerr_correction[i], final_rotation(axis, self.kerr_correction[i], r))
#                s_temp += final_rotation(axis, self.kerr_correction[i], r)   
                        
                if axis is 'mz':
                    final_rotation_nokerr= [r(np.pi, X_AXIS)]
                elif axis is 'z':
                    final_rotation_nokerr= [Delay(20)]
                elif axis is 'x':
                    final_rotation_nokerr= [r(-np.pi/2, Y_AXIS)]
                elif axis is 'y':
                    final_rotation_nokerr= [r(np.pi/2, X_AXIS)]
                elif axis is 'mx':
                    final_rotation_nokerr= [r(np.pi/2, Y_AXIS)]
                elif axis is 'my':
                    final_rotation_nokerr= [r(-np.pi/2, X_AXIS)] # We were using r(np.pi/2, -X_AXIS), which didn't work because X_AXIS=0, beware!         
                        
                s_temp += final_rotation_nokerr
                    
                s_temp += [Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])]
                s_temp += [Delay(2000)]
                s.append(Join(s_temp))
                
        print('before t2check', self.t2_check is not None)
        if self.t2_check is not None:
            for angle in [-np.pi/2, np.pi/2]:
                for i, dt in enumerate(self.delays):
                    s_temp = [Trigger(200), r(np.pi/2, np.pi/2), self.t2_check()]
#                    s_temp = [Trigger(200), r(0, 0), self.t2_check()]
                    if dt > 0:
                        s_temp += [Delay(dt)]
                        
                    s_temp += [self.t2_check(), r(np.pi/2, angle)]
#                    s_temp += [self.t2_check()]
                    
                    s_temp += [Combined([
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                        Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                    ])]
                    s_temp += [Delay(2000)]
                    s.append(Join(s_temp))
                
                
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs


    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

