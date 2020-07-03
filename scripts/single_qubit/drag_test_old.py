import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import lmfit
#import lmfit

def linear_fit(params, x, data):
    est = params['m']*x + params['n']
    return (data-est)

def linear_fit2(params, x):
    est = params['m']*x + params['n']
    return est




#Ebru: I added linear fit to make it easier to pin down the crossing point
    

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs
    drag_y = meas.get_ys()
    drag_y1, drag_y2 = np.split(drag_y, 2)      #Splitting the measurement result in two to fit them separately
    xs1, xs2 = np.split(xs,2)

    
    params = lmfit.Parameters()
    params.add('m', value=0)
    params.add('n', value=0)
    result1 = lmfit.minimize(linear_fit, params, args=(xs1,drag_y1))
    result2 = lmfit.minimize(linear_fit, params, args=(xs2,drag_y2))
    
    lmfit.report_fit(result1.params)
    lmfit.report_fit(result2.params)
    plt.figure()
    plt.plot(xs1, linear_fit2(result1.params, xs1), color='r')
    plt.plot(xs2, linear_fit2(result2.params, xs2), color='b')
    plt.plot(xs1, drag_y1, color='r')
    plt.plot(xs2, drag_y2, color='b')


class drag_test(Measurement1D):

    def __init__(self, qubit_info, coeffs, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        if seq is None:
            seq = Trigger(250)
        self.coeffs = coeffs
        self.xs = np.concatenate((coeffs, coeffs))
        self.seq = seq
        self.postseq = postseq

        super(drag_test, self).__init__(len(coeffs)*2, infos=(qubit_info,), **kwargs)
        self.data.create_dataset('drag_coefficients', data=coeffs)
#        self.data.set_attrs()


    def generate(self):
        s = Sequence()
        r = self.qubit_info.rotate

        for i, coeff in enumerate(self.coeffs):
            print(self.coeffs[i])
            s.append(self.seq)
#            s.append(r(np.pi/2, X_AXIS, drag=coeff))     #This is AllXY#10
#            s.append(Delay(40))
#            s.append(r(np.pi, Y_AXIS, drag=coeff))
            s.append(r(np.pi, X_AXIS, drag=coeff))  #This is AllXY#12 (counting from 1)
            s.append(Delay(20))
            s.append(r(np.pi/2, Y_AXIS, drag=coeff))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))
        for i, coeff in enumerate(self.coeffs):
            print(self.coeffs[i])
            s.append(self.seq)
            s.append(r(np.pi/2, Y_AXIS, drag=coeff))      #This is AllXY#11
            s.append(Delay(20))
            s.append(r(np.pi, X_AXIS, drag=coeff))
#            s.append(r(np.pi, Y_AXIS, drag=coeff))   #This is AllXY#13
#            s.append(Delay(40))
#            s.append(r(np.pi/2, X_AXIS, drag=coeff))
            if self.postseq is not None:
                s.append(self.postseq)
            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
            s.append(Delay(2000))
        s = self.get_sequencer(s)
        seqs = s.render()

        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)
        return #self.fit_params['tau'].value
