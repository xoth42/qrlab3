
from lib.math.minimizer import Parameter, Minimizer
from mclient import instruments
import time
import numpy as np

def define_object(obj):
    '''Lets you pass objects either by their name or directly as mclient containers'''
    if type(obj) == str:
        return instruments[obj]
    else:
        return obj

#I believe thse can't be methods for lo_leakage_func to work on them directly.
#They could probably be absorbed with a lambda function, though.
def lo_leakage_func(params, awg, chans, spec, n_avg=1,delay=0.1, verbose=False):
    awg.set({
        'ch%s_offset'%chans[0]: params['vI'].value,
        'ch%s_offset'%chans[1]: params['vQ'].value,
    })
    time.sleep(delay)
    val = np.average([spec.get_power() for _ in range(n_avg)])
    if verbose:
        print('Measuring at (%.06f, %.06f): %.01f' % \
                (params['vI'].value, params['vQ'].value, val))
    return val

def osb_min_func(params, awg, chans, spec, n_avg=1, delay=0.1, chan_select='i', verbose=False):
    if chan_select == 'i':
        ch_tune, ch_base = chans
    elif chan_select == 'q':
        ch_base, ch_tune = chans
    ch_amp = awg.get('ch%s_amplitude'%ch_base)
    awg.set({
        'ch%s_skew'%ch_tune: params['skew'].value,
        'ch%s_amplitude'%ch_tune: (params['amplitude'].value * ch_amp)
    })
    time.sleep(delay)
    val = np.average([spec.get_power() for _ in range(n_avg)])
    if verbose:
        print('Measuring at (%.06f, %.06f): %.01f' % \
                (params['skew'].value, params['amplitude'].value, val))

    return val


class Mixer_Calibration(object):
    '''ex,
        anc_cal = mixer_cal('ancilla', 5411.600e6,'vspec','AWG1',verbose=False,
                        load_previous_vals=False,
                        base_amplitude =2)

        cal = anc_cal

        cal.tune_lo(mode='coarse')
        cal.tune_osb()
        cal.load_test_waveform()
    '''

    def __init__(self, qubit_info, frequency,spec,awg,verbose=False,
                 load_previous_vals=True,base_amplitude=1):
        '''Frequency here should be the actual qubit frequency.  We'll find
        whether or not you want to use the upper or lower sideband from the
        qubit info's modulation parameters'''
        self.qubit_info = define_object(qubit_info)
        self.spec = define_object(spec)
        self.awg = define_object(awg)

        self.verbose = verbose

        self.chans = [int(x) for x in self.qubit_info.get_channels().split(',')]
        self.if_freq = self.qubit_info.get_deltaf()

        if self.if_freq > 0: #positive IF implies you want to use the Upper SB
            self.shift_phase = np.pi
        else:
            self.shift_phase = 0


        self.lo_frequency = frequency - self.if_freq
        self.osb_freq = frequency - 2*self.if_freq

        if load_previous_vals:
            self.opt_offset_I = self.awg.get('ch%s_offset'%self.chans[0])
            self.opt_offset_Q = self.awg.get('ch%s_offset'%self.chans[1])
            base_amplitude = self.awg.get('ch%s_amplitude'%self.chans[1])
            self.opt_amp_factor = self.awg.get('ch%s_amplitude'%self.chans[0])/base_amplitude
            self.opt_skew_ps = 0#should grab backwards from phase setting
        else:
            self.opt_offset_I = 0
            self.opt_offset_Q = 0
            self.opt_amp_factor = 1
            self.opt_skew_ps = 0

        self.awg.set({
                'ch%s_amplitude'%self.chans[0]: base_amplitude,
                'ch%s_amplitude'%self.chans[1]: base_amplitude})


        self.awg.set({
            'ch%s_skew'%self.chans[0]: 0,
            'ch%s_skew'%self.chans[1]: 0
        })

    def prep_instruments(self, freq=None):
        self.awg.delete_all_waveforms()
        self.awg.get_id() #Sometimes AWGs are slow.  If it responds it's ready.
        self.awg.sideband_modulate(period=1e9/np.abs(self.if_freq), chans=self.chans,
                                   amp=1.0, dphi=self.shift_phase) #the pi is evil.
        self.spec.set_frequency(freq)
        self.spec.set_rf_on(1)
        time.sleep(1)

    def tune_lo(self, verbose=None, plot=True,mode='coarse'):
        print('tuning LO leakage..') # Should be more informative.
        print('')

        if type(mode) == tuple or type(mode) == list:
            vrange,n_it,n_avg = mode
        elif mode == 'coarse':
            vrange = 0.6    # +/- half that.
            n_it = 5        #number of sweeps
            n_avg = 1       #number of averages samples per point
        elif mode == 'fine':
            vrange = 0.1
            n_it = 2
            n_avg = 3

        if verbose:
            self.verbose = verbose
        self.prep_instruments(self.lo_frequency)

        m = Minimizer(lo_leakage_func, args=(self.awg, self.chans, self.spec),
                      kwargs={'verbose':self.verbose, 'n_avg':n_avg}, n_it=n_it, n_eval=21,
                      verbose=self.verbose, plot=plot)
        m.add_parameter(Parameter('vI', value=self.opt_offset_I, vrange=vrange, minstep=0.001))
        m.add_parameter(Parameter('vQ', value=self.opt_offset_Q, vrange=vrange, minstep=0.001))
        m.minimize()

        self.spec.set_rf_on(0)
        self.opt_offset_I = m.params['vI'].value
        self.opt_offset_Q = m.params['vQ'].value
        print('Optimal offsets: %0.03f,%0.03f' % (m.params['vI'].value,m.params['vQ'].value))

        #The minimizer command automatically leaves it in its best values.

    def tune_osb(self, verbose=None, plot=True,mode='coarse'):
        print('tuning OSB leakage..') # Should be more informative.
        print('')

        if type(mode) == tuple or type(mode) == list:
            amp_range,skew_range,n_it,n_avg = mode
        elif mode == 'coarse':
            amp_range = 0.2
            skew_range = 1000 #in picoseconds
            n_it = 3        #number of sweeps
            n_avg = 1       #number of averages samples per point

        self.prep_instruments(self.osb_freq)

        m = Minimizer(osb_min_func, args=(self.awg, self.chans, self.spec),
                      kwargs={'verbose':self.verbose, 'n_avg':n_avg}, n_it=n_it, n_eval=21,
                      verbose=self.verbose, plot=plot)
        m.add_parameter(Parameter('skew', value=self.opt_skew_ps, vrange=skew_range))
        m.add_parameter(Parameter('amplitude', value=self.opt_amp_factor, vrange=amp_range))
        params = m.minimize()

        print('Amplitude imbalance: %0.4f' % params['amplitude'].value)
        print('Skew imbalance (ps): %0.4f' % params['skew'].value)
        self.opt_skew_in_rads = (2 * np.pi * np.abs(self.if_freq) * params['skew'].value *1e-12)
        self.opt_skew_in_rads += self.shift_phase-np.pi
                        #Should be abs IF here - Jacob
        print('skew imbalance (rad): %0.4f' % (self.opt_skew_in_rads))

        ch_tune = self.chans[0]
        self.awg.set({
            'ch%s_skew'%ch_tune: 0
        })

        self.qubit_info.set_sideband_phase(self.opt_skew_in_rads)
        self.spec.set_rf_on(0)

        self.opt_skew_pq = params['skew'].value
        self.opt_amp_factor = params['amplitude'].value

        self.awg.set({
            'ch%s_skew'%self.chans[0]: 0,
            'ch%s_skew'%self.chans[1]: 0,
            })
    def load_test_waveform(self):

        self.awg.delete_all_waveforms()
        self.awg.get_id() #Sometimes AWGs are slow.  If it responds it's ready.
        self.awg.sideband_modulate(period=1e9/np.abs(self.if_freq), chans=self.chans,
                                   amp=1.0, dphi = (self.qubit_info.get_sideband_phase()+np.pi))