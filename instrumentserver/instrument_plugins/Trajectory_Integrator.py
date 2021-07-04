import sys
from .instrument import Instrument
import numpy as np
import os, types, ctypes
import logging
import time
from lib.math import integrator

class Trajectory_Integrator(Instrument):

    def __init__(self, name, **kwargs):
        Instrument.__init__(self, name, tags=['virtual'])

#        self.add_parameter('logical_channel', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='trajectory id')
#        self.add_parameter('channel', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='physical channel')
        self.add_parameter('c2r_method', type=bytes,
                           flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                           format_map={
                               'IQeIQg': 'IQeIQg',
                               'Amplitude': 'Amplitude',
                               'Phase': 'Phase',
                           }, value='IQeIQg',
                           set_func=lambda x: True)

        self.add_parameter('IQg', type=complex,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ point of g')
        self.add_parameter('IQe', type=complex,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ point of e')

        self.add_parameter('use_threshold', flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                type=bool, value=False,
                help='Whether to use_threshold')

        self.add_parameter('threshold_pt', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='projected threshold for g/e discrimination')

        self.add_parameter('weight_func', type=bytes,
                           flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                           help='path to weighting function',
                           value='')
        self.add_parameter('if_period', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='if_period',
                value=20,)
        self.add_parameter('if_length', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='length of integration in if periods',
                value=500,)

        self.add_parameter('length', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='length of integration',
                value=1000,)


        self.set(kwargs)

        # ensure if_length is automatically set
        self.set_length(self.get_length())

#        time.sleep(1.0)
#        self.load_weight_array()

    def do_set_length(self, length):
        self.set_if_length(length/self.get_if_period())
        if_len = length/self.get_if_period()

    def do_set_if_period(self, if_period):
        if_len = self.get_length() / if_period
        self.set_if_length(if_len)

#    def get_iflen(self):
#        return self.if_len

    def do_set_weight_func(self, weight_func):
        try:
            self.load_weight_array(path=weight_func)
        except:
            print('Loading failed')
            raise

    def load_weight_array(self, path=None):#, totlen=None):
        '''
        <totlen> is used to populate the end of the weight array with nans.
        Used when the data has an arbitrary length less than <totlen>
        '''
#        if_len = self.if_len
        if_len = self.get_if_length()

        if path is None:
            path = self.get_weight_func()
#        path = self.get_weight_func()
        logging.info('Loading weight array from: %s' % path)
        if path is None or path == '':
            self._Iweight = np.ones(if_len, dtype=np.float32)/if_len
#            self._Qweight = np.ones(if_len, dtype=np.float32)/if_len
            self._Qweight = np.zeros(if_len, dtype=np.float32)/if_len # 150519: if no weight is used, only use I's (see integrate)
            logging.warning('No weight func specified, reverting to flat window of length %d' % (if_len))
        else:
            ext = os.path.splitext(path)[1]
            if ext == '.npy':
                data = np.load(path)
            elif ext in ('.txt', '.gz', '.bz2'):
                data = np.loads(path)
            else:
                logging.warning('Unable to load file %s' % path)
                raise ValueError('Unable to load file %s' % path)

#            if len(data) != if_len:
#                raise ValueError('Weight func not of right length: %s vs %s' % (len(data), if_len))

            assert type(data) == np.ndarray
            assert data.dtype in (np.complex, np.complex64, np.complex128)

            self._Iweight = np.real(data)
            self._Qweight = np.imag(data)

    def get_IQweight(self):
        return self._Iweight, self._Qweight

    def integrate(self, IQA, Iweight=None, Qweight=None):
        if_len = self.get_if_length()

        if Iweight is None or Qweight is None:
            Iweight = self._Iweight
            Qweight = self._Qweight

#        if self.if_len != len(IQA[0,:self.if_len]):
        if if_len != len(IQA[0,:if_len]):
            raise ValueError('Trajector_Integrator got IQA of wrong length: expected if len = %d; got = %d' % (if_len, len(IQA[0,:if_len])))

#        IQ_weight = np.real(IQA) * Iweight[np.newaxis,:] + \
#                     np.imag(IQA) * Qweight[np.newaxis,:] + \
#                     1j * (np.imag(IQA) *Iweight[np.newaxis,:]) - \
#                     1j * (np.real(IQA) * Qweight[np.newaxis,:])

#        start_time = time.clock()
#        IQ_weight = np.real(IQA)[:,:if_len] * Iweight[np.newaxis,:] + \
#                     np.imag(IQA)[:,:if_len] * Qweight[np.newaxis,:] + \
#                     1j * (np.imag(IQA)[:,:if_len] *Iweight[np.newaxis,:]) - \
#                     1j * (np.real(IQA)[:,:if_len] * Qweight[np.newaxis,:])
        w = Iweight + 1j*Qweight
        IQ_vals = np.dot(IQA[:,:if_len], np.conj(w))
#        IQ_vals = np.einsum('ij,j', IQA[:,:if_len], np.conj(w))
#        logging.info('integrate.weightfunc: %0.3f ms' % (1e3*(time.clock() - start_time)))

#        start_time = time.clock()
#        IQ_vals = np.nansum(IQ_weight, axis=1, dtype=np.complex64)
#                    #use out arg for performance?
#        logging.info('integrate.iqvals: %0.3f ms' % (1e3*(time.clock() - start_time)))

        return IQ_vals

    def c2r(self, data, IQe=None, IQg=None):
        '''
        Complex to real
        '''

        method = self.get_c2r_method()

#        print 'Using method %s' % method
        if method == 'IQeIQg':
            if IQe is None:
                IQe = self.get_IQe()
            if IQg is None:
                IQg = self.get_IQg()

            theta = np.angle(IQe-IQg)
            return np.real(data*np.exp(-1j*theta))

        elif method == 'Amplitude':
            return np.abs(data).real

        elif method == 'Phase':
            return np.angle(data).real

        else:
            raise ValueError('Method: %s is unknown' % method)

    def remove_nans(self, data):
        return data[np.logical_not(np.isnan(data))]

    def process_data(self, IQA, **kwargs):
        '''
        Takes data in <IQA> and passes it through the integration with a
        weight function, converts the complex number to a real value according
        to <c2r>, and applies a weight function if requested.

        The data is returned as float32.
        '''
#        start_time = time.clock()
        IQ_pts = self.integrate(IQA, **kwargs)
#        logging.info('ti.integrate: %0.3f ms' % (1e3*(time.clock() - start_time)))
#        print 'Integrated IQ pts shape: %s' % IQ_pts.shape
#        print 'Integrated IQ pts: %s' % IQ_pts

#        start_time = time.clock()
        real_pts = self.c2r(IQ_pts,)
#        logging.info('ti.c2r: %0.3f ms' % (1e3*(time.clock() - start_time)))
#        print 'Real pts shape: %s' % real_pts.shape
#        print 'Real pts: %s' % real_pts

#        start_time = time.clock()
        if self.get_use_threshold():
            bool_pts = real_pts > self.get_threshold_pt()
#            logging.info('threshold: %0.3f ms' % (1e3*(time.clock() - start_time)))
            return bool_pts

        return real_pts

    def get_integrator(self):
        self.load_weight_array()
        Iweight, Qweight = self.get_IQweight()
        return integrator.Integrator(self.get_length(), self.get_if_period(),
                                     self.get_c2r_method(),
                                     Iweight=Iweight, Qweight=Qweight,
                                     IQe=self.get_IQe(), IQg=self.get_IQg(),
                                     threshold_pt=self.get_threshold_pt(),
                                     use_threshold=self.get_use_threshold())
