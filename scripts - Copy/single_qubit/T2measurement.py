import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import lmfit

ECHO_NONE       = 'NONE'
ECHO_HAHN       = 'HANN'
ECHO_CPMG       = 'CMPG'
ECHO_XY4        = 'XY4'
ECHO_XY8        = 'XY8'
ECHO_XY16       = 'XY16'

def t2_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amplitude
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    exp = np.exp(-(x / params['tau'].value))
    est = params['ofs'].value + params['amplitude'].value * exp * sine
    return data - est

def analysis(meas, data=None, fig=None):
    xs = meas.delays
    ys, fig = meas.get_ys_fig(data, fig)

    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])
    print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

    params = lmfit.Parameters()
    params.add('ofs', value=amp0)
    params.add('amplitude', value=amp0, min=0)
    params.add('tau', value=20000)
    params.add('freq', value=f0, min=0)
    params.add('phi0', value=0, min=-1.2*np.pi, max=1.2*np.pi)
    result = lmfit.minimize(t2_fit, params, args=(xs, ys))
    lmfit.report_fit(params)

    fig.axes[0].plot(xs/1e3, -t2_fit(params, xs, 0), label='Fit, tau=%.03f us, df=%.03f kHz'%(params['tau'].value/1000, params['freq'].value*1e6))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, t2_fit(params, xs, ys), marker='s')
    fig.canvas.draw()
    return params
    
class T2Measurement(Measurement1D):

    def __init__(self, qubit_info, delays, detune=0, echotype=ECHO_NONE, necho=1, **kwargs):
        self.qubit_info = qubit_info
        self.delays = delays
        self.xs = delays / 1e3        # For plotting purposes
        self.detune = detune
        self.echotype = echotype
        self.necho = necho

        super(T2Measurement, self).__init__(len(delays), **kwargs)
        self.data.create_dataset('delays', data=delays)
        self.data.set_attrs(
            detune=detune,
            echotype=echotype,
            necho=necho
        )

    def get_echo_pulse(self):
        r = self.qubit_info.rotate

        if self.echotype == ECHO_NONE:
            return None

        elif self.echotype == ECHO_HAHN:
            return r(np.pi, X_AXIS)

        elif self.echotype == ECHO_CPMG:
            return r(np.pi, Y_AXIS)

        elif self.echotype == ECHO_XY4:
            return Sequence([
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
            ])

        elif self.echotype == ECHO_XY8:
            return Sequence([
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),

                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
            ])

        elif self.echo == ECHO_XY16:
            return Sequence([
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),

                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),
                r(np.pi, Y_AXIS),
                r(np.pi, X_AXIS),

                r(-np.pi, X_AXIS),
                r(-np.pi, Y_AXIS),
                r(-np.pi, X_AXIS),
                r(-np.pi, Y_AXIS),

                r(-np.pi, Y_AXIS),
                r(-np.pi, X_AXIS),
                r(-np.pi, Y_AXIS),
                r(-np.pi, X_AXIS),
            ])

    def generate(self):
        s = Sequence()

        r = self.qubit_info.rotate
        e = self.get_echo_pulse()
        if e:
            elen = e.get_length()
            e = Pad(e, 250, PAD_BOTH)
            epadlen = e.get_length() - elen
        else:
            elen = 0

        for i, dt in enumerate(self.delays):
            s.append(Trigger(dt=250))
            s.append(Pad(r(np.pi/2, X_AXIS), 250, PAD_LEFT))

            # We want echos: <tau> (<echo> <2tau>)^n <tau>
            if e:
                tau = int(np.round(dt / (2 * self.necho) - epadlen/2))
                s.append(Delay(tau))
                for i in range(self.necho - 1):
                    s.append(e)
                    s.append(Delay(2*tau))
                s.append(e)
                s.append(Delay(tau))

            # Plain T2
            else:
                s.append(Delay(dt))

            # Measurement pulse
            angle = dt * 1e-9 * self.detune * 2 * np.pi
            s.append(Pad(r(np.pi/2, angle), 250, PAD_RIGHT))

            s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))

        s = Sequencer(s)
        seqs = s.render()
        if self.qubit_info.ssb is not None:
            self.qubit_info.ssb.modulate(seqs)
        return seqs

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)        
        return self.fit_params
