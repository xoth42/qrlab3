# -*- coding: utf-8 -*-
"""
Driver for the fancy signal hound.
By Josh, 5/29/18
joshuacarey@umass.edu
"""
from instrument import Instrument
import ctypes
import types
import numpy

DLL_path = 'C:\\qrlab\\instrumentserver\\instrument_plugins\\sm_api.dll'
DLL_LIB = ctypes.windll.LoadLibrary(DLL_path)
modes = {
    'swept': 1,
    'realtime': 2,
    'IQ': 3,
    'audio': 4}
speeds = {
    'fast': 2,
    'normal': 1,
    'auto': 0}
SmDetector = {
    'average': 0,
    'minmax': 1}

SmWindowType = {
    'smWindowFlatTop': 0,
    'smWindowNutall': 2,
    'smWindowBlackman': 3,
    'smWindowHamming': 4,
    'smWindowGaussian6dB': 5,
    'smWindowRect': 6
}


class APIFunction():
    def __init__(self, func_name, args_list, restype):
        self.func_name = func_name
        self.func_name.argtypes = args_list
        self.func_name.restype = restype

    def __call__(self, *args):
        return_code = self.func_name(*args)
        if return_code != 0:
            self.error_report(return_code)

    def error_report(self, return_code):
        print "ALERT: There was an event with the SM200A:"
        print"In function: " + str(self.func_name.__name__)
        print "Returned: " + str(return_code)
        DLL_LIB.smGetErrorString.restype = ctypes.c_char_p
        print"info: " + DLL_LIB.smGetErrorString(return_code)


class SignalHoundSM200A(Instrument):
    def __init__(self, name, **kwargs):
        super(SignalHoundSM200A, self).__init__(name)
        self.return_codes = {}
        self.handle = ctypes.pointer(ctypes.c_int())
        self.open_devices = APIFunction(
            DLL_LIB.smOpenDevice, [
                ctypes.POINTER(
                    ctypes.c_int)], ctypes.c_int)
        self.open_devices(self.handle)
        self._handle_ = self.handle.contents
        self.speed_selection = kwargs['speed']
        self.parameters = kwargs

        # Configure the mode for the data taking.
        self.add_parameter(
            'vbw',
            type=types.FloatType,
            flags=Instrument.FLAG_GETSET,
            doc='Video bandwidth',
            set_func=lambda x: True,
            value=300e3,
            units='Hz')
        self.add_parameter(
            'speed',
            type=types.StringType,
            flags=Instrument.FLAG_GETSET,
            doc='Sweep speed for swept mode',
            set_func=lambda x: True,
            value='normal')

        self.add_parameter(
            'ref',
            types=types.FloatType,
            flags=Instrument.FLAG_GETSET,
            doc='reference level',
            set_func=lambda x: True,
            value=3.14)
        self.add_parameter(
            'rbw',
            type=types.IntType,
            flags=Instrument.FLAG_GETSET,
            doc="resolution bandwidth",
            set_func=lambda x: True,
            value=100000,
            units="Hz")
        self.add_parameter(
            'mode',
            type=types.StringType,
            flags=Instrument.FLAG_GETSET,
            doc="Sweeping mode",
            set_func=lambda x: True,
            value='')
        self.add_parameter(
            'external_reference',
            type=types.BooleanType,
            flags=Instrument.FLAG_GETSET,
            doc="Use external 10 MHz reference port",
            set_func=lambda x: True,
            value=False)
        self.add_parameter(
            'center',
            type=types.FloatType,
            flags=Instrument.FLAG_GETSET,
            doc='Center frequency for sweep.',
            set_func=lambda x: True,
            units='Hz',
            value=1e7)
        self.add_parameter(
            'span',
            type=types.FloatType,
            flags=Instrument.FLAG_GETSET,
            doc="Span for frequency sweep",
            set_func=lambda x: True,
            units='Hz',
            value=1e4)
        self.add_parameter(
            'spur',
            type=types.BooleanType,
            flags=Instrument.FLAG_GETSET,
            doc='Software spur rejection',
            set_func=lambda x: True,
            value=True)

    def sweep(self, center = 0, span = 0):
        sweep_speed = APIFunction(DLL_LIB.smSetSweepSpeed,
                                  [ctypes.c_int, ctypes.c_int], ctypes.c_int)
        sweep_speed(self._handle_, speeds[self.speed_selection])
        if center == 0 and span == 0:
            _center_ = self.parameters['center']
            _span_ = self.parameters['span']
        else:
            _center_ = center
            _span_ = span
            
        
        
        start_stop = APIFunction(
            DLL_LIB.smSetSweepCenterSpan, [
                ctypes.c_int, ctypes.c_double, ctypes.c_double], ctypes.c_int)
        start_stop(
            self._handle_,
            _center_,
            _span_)
        coupling = APIFunction(DLL_LIB.smSetSweepCoupling, [ctypes.c_int,
                                                            ctypes.c_double,
                                                            ctypes.c_double,
                                                            ctypes.c_double],
                               ctypes.c_int)
        # Mot really sure what this parameter should be...
        sweep_time = 0.1
        coupling(
            self._handle_,
            self.parameters['rbw'],
            self.parameters['vbw'],
            sweep_time)
        detector = APIFunction(DLL_LIB.smSetSweepDetector, [ctypes.c_int,
                                                            ctypes.c_int,
                                                            ctypes.c_int],
                               ctypes.c_int)
        detector(self._handle_, SmDetector['average'], 2)
        scale = APIFunction(DLL_LIB.smSetSweepScale, [ctypes.c_int,
                                                      ctypes.c_int],
                            ctypes.c_int)
        scale(self._handle_, 0)

        window = APIFunction(DLL_LIB.smSetSweepWindow, [ctypes.c_int,
                                                        ctypes.c_int],
                             ctypes.c_int)
        window(self._handle_, SmWindowType['smWindowHamming'])

        spur_reject = APIFunction(DLL_LIB.smSetSweepSpurReject,
                                  [ctypes.c_int, ctypes.c_bool], ctypes.c_int)
        spur_reject(self._handle_, self.parameters['spur'])
        ref_ = APIFunction(
            DLL_LIB.smSetRefLevel, [
                ctypes.c_int, ctypes.c_double], ctypes.c_int)
        ref_(self._handle_, self.parameters['ref'])

        configure = APIFunction(
            DLL_LIB.smConfigure, [
                ctypes.c_int, ctypes.c_int], ctypes.c_int)
        configure(self._handle_, modes['swept'])
        sweep_parameters = APIFunction(DLL_LIB.smGetSweepParameters,
                                       [ctypes.c_int, ctypes.POINTER(
                                           ctypes.c_double), ctypes.POINTER(
                                           ctypes.c_double), ctypes.POINTER(
                                           ctypes.c_double), ctypes.POINTER(
                                           ctypes.c_double), ctypes.POINTER(
                                           ctypes.c_int)],
                                       ctypes.c_int)

        actual_rbw = ctypes.pointer(ctypes.c_double())
        actual_vbw = ctypes.pointer(ctypes.c_double())
        startfreq = ctypes.pointer(ctypes.c_double())
        binsize = ctypes.pointer(ctypes.c_double())
        sweep_size = ctypes.pointer(ctypes.c_int())
        sweep_parameters(self._handle_, actual_rbw, actual_vbw, startfreq,
                         binsize,
                         sweep_size)

        sweep_min = numpy.zeros(
            sweep_size.contents.value).astype(
            numpy.float32)
        sweep_max = numpy.zeros(
            sweep_size.contents.value).astype(
            numpy.float32)
        get_sweep = APIFunction(DLL_LIB.smGetSweep, [ctypes.c_int,
                                                     numpy.ctypeslib.ndpointer(
                                                         numpy.float32, ndim=1,
                                                         flags='C'),
                                                     numpy.ctypeslib.ndpointer(
                                                         numpy.float32, ndim=1,
                                                         flags='C'),
                                                     ctypes.c_int],
                                ctypes.c_int)
        get_sweep(self._handle_, sweep_min, sweep_max,
                  ctypes.c_int(0))
        freqs = [
            (startfreq.contents.value + 
             (i *
              binsize.contents.value)) for i in range(
                0,
                sweep_size.contents.value)]

        return freqs, sweep_max

    def realtime_frame(self, center = 0, span = 0):
        cent_span = APIFunction(DLL_LIB.smSetRealTimeCenterSpan,
                                [ctypes.c_int, ctypes.c_double,
                                 ctypes.c_double], ctypes.c_int)
        if center == 0 and span == 0:
            _center_ = self.parameters['center']
            _span_ = self.parameters['span']
        else:
            _center_ = center
            _span_ = span
        cent_span(self._handle_, _center_, _span_)

        rbw = APIFunction(DLL_LIB.smSetRealTimeRBW, [ctypes.c_int,
                                                     ctypes.c_double],
                          ctypes.c_int)
        rbw(self._handle_, self.parameters['rbw'])
        scale = APIFunction(DLL_LIB.smSetRealTimeScale, [ctypes.c_int,
                                                         ctypes.c_int,
                                                         ctypes.c_double,
                                                         ctypes.c_double],
                            ctypes.c_int)
        # A common height for the frames is 100 dB.
        scale(self._handle_, 0, self.parameters['ref'], 100)
        window = APIFunction(DLL_LIB.smSetRealTimeWindow, [ctypes.c_int,
                                                           ctypes.c_int],
                             ctypes.c_int)
        window(self._handle_, SmWindowType['smWindowHamming'])

        configure = APIFunction(
            DLL_LIB.smConfigure, [
                ctypes.c_int, ctypes.c_int], ctypes.c_int)
        configure(self._handle_, modes['realtime'])
        params = APIFunction(
            DLL_LIB.smGetRealTimeParameters, [
                ctypes.c_int, ctypes.POINTER(
                    ctypes.c_double), ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(
                        ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(
                            ctypes.c_int), ctypes.POINTER(
                                ctypes.c_int), ctypes.POINTER(
                                    ctypes.c_double)], ctypes.c_int)
        actual_rbw = ctypes.pointer(ctypes.c_double())
        sweep_size = ctypes.pointer(ctypes.c_int())
        startfreq = ctypes.pointer(ctypes.c_double())
        binsize = ctypes.pointer(ctypes.c_double())
        width = ctypes.pointer(ctypes.c_int())
        height = ctypes.pointer(ctypes.c_int())
        poi = ctypes.pointer(ctypes.c_double())

        # Get all of the params
        params(self._handle_, actual_rbw, sweep_size, startfreq, binsize,
               width, height, poi)
#        large_array = numpy.ctypeslib.ndpointer(numpy.float32, ndim=1,flags='C')
        get_frame = APIFunction(
            DLL_LIB.smGetRealTimeFrame, [
                ctypes.c_int, numpy.ctypeslib.ndpointer(
                    numpy.float32, ndim=1, flags='C'), numpy.ctypeslib.ndpointer(
                    numpy.float32, ndim=1, flags='C'), numpy.ctypeslib.ndpointer(
                    numpy.float32, ndim=1, flags='C'), numpy.ctypeslib.ndpointer(
                        numpy.float32, ndim=1, flags='C'), ctypes.POINTER(
                            ctypes.c_int), ctypes.POINTER(
                                ctypes.c_longlong)], ctypes.c_int)
#        data_frame = (ctypes.c_float * (width.contents.value *
#                                        height.contents.value))()
#
#        alpha_frame = (ctypes.c_float * (width.contenmts.value *
#                                         height.contents.value))()
#        ctypes.cast(data_frame, ctypes.POINTER(ctypes.c_float))
#        ctypes.cast(alpha_frame, ctypes.POINTER(ctypes.c_float))
        data_frame = numpy.zeros(
            width.contents.value *
            height.contents.value).astype(
            numpy.float32)
        alpha_frame = numpy.zeros(
            width.contents.value *
            height.contents.value).astype(
            numpy.float32)

        sweep_min = numpy.zeros(
            sweep_size.contents.value).astype(
            numpy.float32)
        sweep_max = numpy.zeros(
            sweep_size.contents.value).astype(
            numpy.float32)
        frame_count = ctypes.pointer(ctypes.c_int())
        ns = ctypes.pointer(ctypes.c_longlong())
        
        get_frame(
            self._handle_,
            data_frame,
            alpha_frame,
            sweep_min,
            sweep_max,
            frame_count,
            ns)
        return data_frame, alpha_frame, sweep_min, sweep_max

    def do_set_external_reference(self, ref_val):
        ref_set = APIFunction(
            DLL_LIB.smSetExternalReference, [
                ctypes.c_int, ctypes.c_bool], ctypes.c_int)
        return ref_set(self._handle_, ref_val)

    def do_get_external_reference(self):
        get_ext = APIFunction(
            DLL_LIB.smGetExternalReference, [
                ctypes.c_int, ctypes.POINTER(
                    ctypes.c_bool)], ctypes.c_int)
        ret_bool = ctypes.pointer(ctypes.c_bool())
        get_ext(self._handle_, ret_bool)
        return ret_bool.contents.value

    def do_set_ref(self, new_ref):
        set_ref = APIFunction(DLL_LIB.smSetRefLevel, [ctypes.c_int,
                                                      ctypes.c_double],
                              ctypes.c_int)
        set_ref(self._handle_, new_ref)

    def do_get_ref(self):
        new = ctypes.pointer(ctypes.c_double())
        get_ref = APIFunction(DLL_LIB.smGetRefLevel, [ctypes.c_int,
                                                      ctypes.POINTER(
                                                          ctypes.c_double)],
                              ctypes.c_int)
        get_ref(self._handle_, new)
        return new.contents.value


if __name__ == "__main__":
    test = SignalHoundSM200A(
        "signalhound",
        speed='auto',
        center=1.2e8,
        span=2e7,
        vbw=200e3,
        rbw=200e3,
        ref=10,
        spur=False)
#    a, b, c, d = test.realtime_frame()
    import matplotlib.pyplot as plt
    a, b = test.sweep()
#    plt.plot(a, b)
#    from scipy.signal import find_peaks_cwt
#    widths = numpy.arange(10, 50)
#    peaks = find_peaks_cwt(b, widths)
#    local_maxes = [b[i] for i in peaks]
    
    
    
    

  #  plt.show()
