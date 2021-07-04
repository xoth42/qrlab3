# Alazar acquisition daemon with two weight funcs and two IF periods (not currently implemented)
#
# This daemon provides 2 shared objects:
# - AlazarCard, to directly set channel parameters
# - AlazarDaemon, to manage buffers and perform the actual acquisition

import sys

import ctypes
import types
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['legend.fontsize'] = 8
import time
from lib.dll_support import alazar
AC = alazar.Constants
from lib.math import demod
from .instrument import Instrument
import logging
import gc
import os

import objectsharer as objsh

from instrumentserver.instrument_plugins.Alazar_Daemon import Alazar_Daemon

class AC2:
    MEAS_0 = 0
    MEAS_1 = 1
    MEAS_01 = 2

class Alazar_DoubleDaemon(Alazar_Daemon):

    def __init__(self, name, **kwargs):
        super(Alazar_DoubleDaemon, self).__init__(name, **kwargs)
        self.add_parameter('if_period1', type=int,
                           flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                           minval=2, maxval=1000, value=20,
                           help='Intermediate Frequency period')
        self.add_parameter('weight_func1', type=bytes,
                           flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                           help='''
                Weight function file, either a .npy (numpy file) or a txt file.
                The data should have length #IF periods. If real valued the same weight
                function is applied to both I and Q quadratures, if complex valued the
                real part is applied to I and the imaginary part to Q.
                ''')
        self.add_parameter('meas_select', type=int,
                           flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                           format_map={
                               AC2.MEAS_0: 'Demod/Weight 0',
                               AC2.MEAS_1: 'Demod/Weight 1',
                               AC2.MEAS_01: 'Demod/Weight 0 and 1',
                           }, value=AC2.MEAS_0)


    def set_demod(self, avg_periods=1, weight_func=1, weight_func1=1, bufsize=None):
        '''
        Sets up demodulators.
        <avg_periods> only applies to channel B (the reference), as we might
        want to use weight functions to the corrected shots.
        '''

        if bufsize is None:
            bufsize = self.get_nsamples() * self.get_nrecperbuf()

        def get_IQ_weights(fn):
            weight_func = self.load_weight_func(fn)
            # Default is no weighting function.
            Iweight = None
            Qweight = None
            if type(weight_func) is np.ndarray:
                if weight_func.dtype in (np.complex, np.complex64, np.complex128):
                    Iweight = np.real(weight_func)
                    Qweight = np.imag(weight_func)
                else:
                    Iweight = weight_func
                    Qweight = weight_func
            return Iweight, Qweight

        self._Iweight, self._Qweight = get_IQ_weights(self.get_weight_func())
        self._Iweight1, self._Qweight1 = get_IQ_weights(self.get_weight_func1())

        self._demodA = demod.DemodulatorComplex(bufsize, self.get_if_period(), avg_periods=1)
        self._demodB = demod.DemodulatorComplex(bufsize, self.get_if_period(), avg_periods=avg_periods)

#        self._demodA2 = demod.DemodulatorComplex(bufsize, self.get_if_period1(), avg_periods=1)
#        self._demodB2 = demod.DemodulatorComplex(bufsize, self.get_if_period1(), avg_periods=avg_periods)

        # Garbage collect old demodulators
        gc.collect()

    def get_IQ_rel(self, buf, cycles):
        '''
        Return relative IQ values for every shot (1 IQ / shot).
        This takes into account both weighting functions
        '''

        blen = len(buf)
        self._demodA.demodulate(buf[:blen/2])
        self._demodB.demodulate(buf[blen/2:])
        # add second demodulation stuff here!
        phase_corr = np.exp(-1j * np.angle(self._demodB.IQ))
        percycle = len(self._demodA.IQ) / cycles
        IQA = self._demodA.IQ.reshape((cycles, percycle))

        def calc_IQrel(IQA, Iweight, Qweight):
            IQ_rel = None
            # either using demod/weight 0 or both
            if Iweight is None: # No weighting function
                IQ_rel = np.average(IQA, 1) * phase_corr
            else: # Correct each trace, see numpy broadcasting
                IQ_rel = (IQA.T * phase_corr).T
                IQ_rel = self.apply_IQ_weight(IQ_rel, Iweight, Qweight)
                IQ_rel = np.sum(IQ_rel, axis=1)
            return IQ_rel

        IQ_rel = None
        IQ_rel1 = None
        if self.get_meas_select() != AC2.MEAS_1:
            IQ_rel = calc_IQrel(IQA, self._Iweight, self._Qweight)
        if self.get_meas_select() != AC2.MEAS_0:
            IQ_rel1 = calc_IQrel(IQA, self._Iweight1, self._Qweight1)

        # return the correct IQ values
        if self.get_meas_select() == AC2.MEAS_0:
            return IQ_rel
        elif self.get_meas_select() == AC2.MEAS_1:
            return IQ_rel1
        elif self.get_meas_select() == AC2.MEAS_01:
            return np.hstack(list(zip(IQ_rel, IQ_rel1)))
        else:
            raise Exception('get_IQ_rel does not understand <meas_select>')

    def take_experiment(self, acqtimeout=None, avg_buf=None):
        '''
            Data will be this form:
                [cycle[0].weight1, cycle[0].weight2, cycle[1].weight1, cycle[1].weight2, ...]
        '''
        num_demod = 1
        if self.get_meas_select() == AC2.MEAS_01:
            num_demod = 2
        return super(Alazar_DoubleDaemon, self).take_experiment(acqtimeout, avg_buf, num_demod)

    def setup_hist(self, N, hist_buf=None):
        '''
        Setup histogram measurement for <N> shots.
        <num_demods> is the number of demodulations for measurement record, usually 1.
            (Internally, setup_hist defines an array of the appropriate size)
        '''
        num_demod = 1
        if self.get_meas_select() == AC2.MEAS_01:
            num_demod = 2
        super(Alazar_DoubleDaemon, self).setup_hist(N, hist_buf, num_demod)

    def take_hist(self, acqtimeout=None):
        '''
            Data will be this form:
                [cycle[0].weight1, cycle[0].weight2, cycle[1].weight1, cycle[1].weight2, ...]
        '''
        num_demod = 1
        if self.get_meas_select() == AC2.MEAS_01:
            num_demod = 2
        return super(Alazar_DoubleDaemon, self).take_hist(acqtimeout, num_demod)

    def take_demod_shots(self):
        '''
            Update demod shots to update the I and Q weighting functions depending
            on which demod/weight engine is selected.

            Currently does not handle or understand when engine 0 and 1 is being used.
        '''

        if self.get_meas_select() == AC2.MEAS_0:
            Iweight = self._Iweight
            Qweight = self._Qweight
        elif self.get_meas_select() == AC2.MEAS_1:
            Iweight = self._Iweight1
            Qweight = self._Qweight1
        else:
            raise Exception('Alazar_DoubleDaemon.take_demod_shots does not support multiple demod/weight engines')
        return super(Alazar_DoubleDaemon, self).take_demod_shots(Iweight=Iweight, Qweight=Qweight)

#    def take_demod_shots(self, **kwargs):
#        '''
#        This is hacky.  we should fix it if it works.  do we need to modify
#        setup demod shots?  This also doesn't support meas_01
#        '''
#
#        if self.get_meas_select() == AC2.MEAS_1:
#            old_iweight, old_qweight = self._Iweight, self._Qweight
#            self._Iweight, self._Qweight = self._Iweight1, self._Qweight1
#            ret = super(Alazar_DoubleDaemon, self).take_demod_shots(**kwargs)
#            self._Iweight, self._Qweight = old_iweight, old_qweight
#            return ret
#
#        else:
#            return super(Alazar_DoubleDaemon, self).take_demod_shots(**kwargs)