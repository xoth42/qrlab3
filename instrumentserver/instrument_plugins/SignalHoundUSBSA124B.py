# Driver for the Signal Hound SA124B spectrum analyzer
# Started by Josh Carey 1/30/18
# joshuacarey@umass.edu
# Not placed in instrument_plugins since then the Instrument class is not
# available. How do the other plugins get around this?
# Misc notes:
# (1) See sa_api.h for the meaning of all the error codes. Notably a return code of 0 means
# no error.
# (2) You cannot have spike and this script running at the same time.
# (3) General note: for an instrument driver, the name of the file must be
# identical to the name of the instrument class object.
# (4) The driver usually takes on the order of 10 seconds to connect to the
# actual signal hound.
# (5) The amount of time required to open the device is much larger than the time
# to run a sweep. Thus the best idea is to open the device once, and perform multiple
# sweeps for each center and span.
# (6) When one of the API functions expects a bool, passing True or False is not enough
# or doesn't register with the API. Instead you must use argtypes to explicitly tell
# ctypes its a bool.
# (7) If you sometimes get two peaks, or the spectrum is reflected acrosss ~21 MHz
# of spectrum, the API is not doing something called spur rejection. You can tooggle
# it under SPIKE in the settings menu.
# TODO: Fix the signal clamping issue; VBW and RBW seem to get clamped regardless of their value.
# TODO: Return a faster numpy array as the end result of the whole computation.
from instrument import Instrument
import ctypes
import types
import numpy as np

DLL_PATH = "C:\\qrlab\\instrumentserver\\instrument_plugins\\sa_api.dll"
DLL_LIB = ctypes.windll.LoadLibrary(DLL_PATH)

# A whole list of constants

SA_MIN_MAX = 0x0
SA_AVERAGE = 0x1
SA_LOG_SCALE = 0x0
SA_LIN_SCALE = 0x1
SA_LOG_FULL_SCALE = 0x2
SA_LIN_FULL_SCALE = 0x3
SA_LOG_UNITS = 0x0
SA_SWEEPING = 0x0


class NotOpenError(Exception):
    pass


class SignalHoundUSBSA124B(Instrument):
    def __init__(self, name, **kwargs):
        super(SignalHoundUSBSA124B, self).__init__(name)
        # Take all of the different parameters and make them values.
        for key in kwargs:
            setattr(self, key, kwargs[key])
        # These return codes are only for debugging purposes.
        self.return_codes = {}
        self.device_pointer = ctypes.c_int()
        self.device_handle_p = ctypes.pointer(self.device_pointer)
        # Sometimes the device handle needs to be min_array pointer to min_array 32 bit int.
        # I'm sure whether this is 32 bit, but it seems to work. It also
        # might need the value at that memory address. Check the API for
        # reference.

        # ~~~ Configure the device
        self.return_codes['device open'] = DLL_LIB.saOpenDeviceBySerialNumber(
            self.device_handle_p, self.serial_no)
        if self.return_codes['device open'] == -8:
            raise NotOpenError("signal hound failed to open.")
        self.device_handle = self.device_handle_p.contents
        # Configure the device in such a way that for each sweep, the minimum and
        # maxiumum values for each bin are averaged together to produce one set of
        # values, and set the scale to logarithmic. Both of these parameters can be
        # changed at will.
        self.return_codes['dec and scale ac'] = DLL_LIB.saConfigAcquisition(
            self.device_handle, SA_AVERAGE, SA_LOG_SCALE)
        # The argtype attribute specifies the types of arguments that a
        # function will take, in C types. For some reason the following
        # function needs to have these types specified, unlike all the others.
        DLL_LIB.saConfigCenterSpan.argtypes = [ctypes.c_int, ctypes.c_double,
                                               ctypes.c_double]
        self.return_codes['center and span'] = \
            DLL_LIB.saConfigCenterSpan(self.device_handle,
                                       float(self.center), float(self.span))
        self.return_codes['ref'] = DLL_LIB.saConfigLevel(
            self.device_handle, self.ref)
        # -1 means use the automatic gain and attenuation settings, provided by the
        # device itself.
        self.return_codes['gain and atten'] = DLL_LIB.saConfigGainAtten(
            self.device_handle, -1, -1, True)
        DLL_LIB.saConfigSweepCoupling.argtypes = [ctypes.c_int, ctypes.c_double,
                                                  ctypes.c_double,
                                                  ctypes.c_bool]
        self.return_codes['sweep coupling'] = \
            DLL_LIB.saConfigSweepCoupling(self.device_handle,
                                          self.rbw, self.vbw,
                                          True)
        self.return_codes['proc units'] = DLL_LIB.saConfigProcUnits(
            self.device_handle, SA_LOG_UNITS)
        # The last parameter here is unused and gets thrown away, as documented in
        # the API.
        self.return_codes['initialize'] = DLL_LIB.saInitiate(
            self.device_handle, SA_SWEEPING, 0)

        ###~~~Parameters~~~###

        self.add_parameter('center', type=types.FloatType, flags=
        Instrument.FLAG_GETSET, doc="", set_func=lambda x: True, value=
                           6e6, units='Hz')
        self.add_parameter('span', type=types.FloatType, flags=
        Instrument.FLAG_GETSET, doc="", set_func=lambda x: True, value=2e6,
                           units='Hz')
        self.add_parameter('ref', type=types.IntType, flags=
        Instrument.FLAG_GETSET, doc="", set_func=lambda x: True, value=0,
                           units='dBm')
        self.add_parameter('rbw', type=types.IntType, flags=
        Instrument.FLAG_GETSET, doc="resolution bandwidth", set_func=
                           lambda x: True, value=100000, units="Hz")
        self.add_parameter('vbw', type=types.IntType, flags=
        Instrument.FLAG_GETSET, doc="video bandwidth", set_func=lambda x:
        True, value=100000, units="Hz")

        print "Signal Hound diagnostic info:"
        for key in self.return_codes:
            print str(key) + ":  " + str(self.return_codes[key])

        # Warnings and errors.

        if self.return_codes['initialize'] == 4:
            print "ALERT: VBW and RBW bandwith has been clamped"

    def do_set_center(self, center):
        self.return_codes['set center and span'] = DLL_LIB.saConfigCenterSpan(
            self.device_handle, center, self.span)
        self.center = center
        print self.return_codes['set center and span']
        print "foo"

    def do_set_span(self, span):
        self.return_codes['set center and span 2'] = DLL_LIB.saConfigCenterSpan(
            self.device_handle, self.center,
            span)
        self.span = span
        print "bar"

    def do_set_ref(self, ref):
        self.return_codes['set ref'] = DLL_LIB.saConfigLevel(self.device_handle,
                                                             ref)

    def do_set_rbw(self, rbw):
        DLL_LIB.saConfigSweepCoupling.argtypes = [ctypes.c_int, ctypes.c_double,
                                                  ctypes.c_double,
                                                  ctypes.c_bool]
        DLL_LIB.saConfigSweepCoupling(
            self.device_handle, rbw, self.vbw, True)
        self.rbw = rbw

    def do_set_vbw(self, vbw):
        DLL_LIB.saConfigSweepCoupling(
            self.device_handle, self.rbw, vbw, True)
        self.vbw = vbw

    def do_get_center(self):
        return self.center

    def do_get_span(self):
        return self.span

    def do_get_ref(self):
        return self.ref

    def do_get_rbw(self):
        return self.rbw

    def do_get_vbw(self):
        return self.vbw

    def perform_sweep(self, peak_find = True, plot = False, **kwargs):

        print "Performing sweep for parameters: "
        print "Center: " + str(self.center)
        print "Span: " + str(self.span)
        self.sweep_length_ = ctypes.c_int()
        self.sweep_length_p = ctypes.pointer(self.sweep_length_)
        self.start_freq = ctypes.c_double()
        self.start_freq_p = ctypes.pointer(self.start_freq)
        self.bin_size = ctypes.c_double()
        self.bin_size_p = ctypes.pointer(self.bin_size)
        # Get all of the information needed to perform a nice sweep.
        self.return_codes['sweep info'] = DLL_LIB.saQuerySweepInfo(
            self.device_handle, self.sweep_length_p, self.start_freq_p,
            self.bin_size_p)
        self.array_length = self.sweep_length_p.contents.value

        self.min_array = (ctypes.c_float * self.array_length)()
        self.max_array = (ctypes.c_float * self.array_length)()
        ctypes.cast(self.min_array, ctypes.POINTER(ctypes.c_float))
        ctypes.cast(self.max_array, ctypes.POINTER(ctypes.c_float))
        print 'test'
        DLL_LIB.saGetSweep_32f.argtypes = [ctypes.c_int,
                                           ctypes.POINTER(
                                               ctypes.c_float * self.array_length),
                                           ctypes.POINTER(
                                               ctypes.c_float * self.array_length)]

        self.return_codes['GET SWEEP'] = DLL_LIB.saGetSweep_32f(
            self.device_handle, self.min_array, self.max_array)
        result = list()
        print 'thing'
        freq = self.start_freq_p.contents.value
        # Only need to consider min_array since both arrays hold the same value.
        for i, value in enumerate(self.min_array, 1):
            result.append([freq, value])
            freq = self.start_freq_p.contents.value + i * self.bin_size_p.contents.value
        #The function below smooths the data by taking a moving average box.
        def smooth(y, box_pts=20):
            box = np.ones(box_pts) / box_pts
            y_smooth = np.convolve(y, box, mode='same')
            return y_smooth
        frequencies = [thing[0] for thing in result]
        powers = [thing[1] for thing in result]
        if peak_find == True:
            from scipy.signal import find_peaks_cwt
            widths = np.arange(300, 500)
            peaks = find_peaks_cwt(powers, widths)
            local_maxes = [powers[i] for i in peaks]
            if plot == True:
                import matplotlib
                matplotlib.rcParams['backend'] = 'Qt4Agg'
                matplotlib.rcParams['backend.qt4'] = 'PyQt4'
                import matplotlib.pyplot as plt
                plt.plot(frequencies, powers, 'r')
                for i in peaks:
                    plt.plot(frequencies[i], powers[i], 'bo')
                plt.grid()
                plt.title("Frequency vs power for signal hound")
                plt.show()
            del self.sweep_length_p, self.start_freq
            return local_maxes, result
        else:
            return result


