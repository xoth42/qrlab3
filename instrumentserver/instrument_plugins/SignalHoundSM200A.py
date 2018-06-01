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
        print "ALERT: There was an error with the SM200A:"
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
        self.mode_selection = kwargs['mode']
        self.speed_selection = kwargs['speed']

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
            value=10)
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
        if self.mode_selection == 'swept':
            self.sweep_config(kwargs)

    def sweep_config(self, kwargs):
        sweep_speed = APIFunction(DLL_LIB.smSetSweepSpeed,
                                  [ctypes.c_int, ctypes.c_int], ctypes.c_int)
        sweep_speed(self._handle_, speeds[self.speed_selection])
        start_stop = APIFunction(
            DLL_LIB.smSetSweepCenterSpan, [
                ctypes.c_int, ctypes.c_double, ctypes.c_double], ctypes.c_int)
        start_stop(self._handle_, kwargs['center'], kwargs['span'])
        coupling = APIFunction(DLL_LIB.smSetSweepCoupling, [ctypes.c_int,
                                                            ctypes.c_double,
                                                            ctypes.c_double,
                                                            ctypes.c_double],
                               ctypes.c_int)
        # Mot really sure what this parameter should be...
        sweep_time = 1
        coupling(self._handle_, kwargs['rbw'], kwargs['vbw'], sweep_time)
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
        spur_reject(self._handle_, kwargs['spur'])

        get_sweep = APIFunction(DLL_LIB.smGetSweep, [ctypes.c_int,
                                                     numpy.ctypeslib.ndpointer(
                                                         numpy.float32, ndim=1,
                                                         flags='C'),
                                                     numpy.ctypeslib.ndpointer(
                                                         numpy.float32, ndim=1,
                                                         flags='C'),
                                                     ctypes.c_int],
                                ctypes.c_int)
        configure = APIFunction(
            DLL_LIB.smConfigure, [
                ctypes.c_int, ctypes.c_int], ctypes.c_int)
        configure(self._handle_, modes[self.mode_selection])
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

        get_sweep(self._handle_, sweep_min, sweep_max,
                  ctypes.c_int(0))
        print sweep_max

    def IQ_config(self):
        pass

    def realtime_config(self):
        pass

    def do_set_external_reference(self, ref_val):
        ref_set = APIFunction(
            DLL_LIB.smSetExternalReference, [
                ctypes.c_int, ctypes.c_bool], ctypes.c_int)
        return ref_set(self._handle_, ref_val)


if __name__ == "__main__":
    test = SignalHoundSM200A("signalhound", mode='swept', speed='normal',
                             center=1e6, span=1e4, vbw=300e3, rbw=300e3,
                             spur=True)
