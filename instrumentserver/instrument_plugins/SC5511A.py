# -*- coding: utf-8 -*-
"""
SignalCore SC5511A RF Source DLL driver.

Python 3.10 compatible version.
"""

import ctypes
import logging
import os

from instrumentserver.instrument import Instrument

SUCCESS = 0
NO_DEVICE = 0

# LB_DLL = r'C:\qrlab-3\instrumentserver\vnx_fmsynth.dll'
LB_DLL = r'C:\qrlab-3\instrumentserver\SignalCore\x64\sc5511a.dll'

NUM_MAX_DEVICES = 5
ID_BUFFER_SIZE = 8


def _to_bytes(value, encoding='ascii'):
    """Return bytes for C char* APIs.

    Python 3 separates text (str) and bytes.  ctypes.c_char_p requires bytes
    or an integer address, not str.
    """
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        return value.encode(encoding)
    raise TypeError('Expected str, bytes, bytearray, or None, got %s' % type(value).__name__)


def _load_signalcore_dll(path):
    """Load the SignalCore DLL using the Windows calling convention."""
    try:
        return ctypes.WinDLL(path)
    except AttributeError as exc:
        raise ValueError('SignalCore DLL driver only works on Windows: %s' % exc)
    except OSError as exc:
        raise ValueError(
            'Unable to load SignalCore DLL. Check that sc5511a.dll exists at %r '
            'and that its architecture matches Python: %s' % (path, exc)
        )


lb_dll = _load_signalcore_dll(LB_DLL)


class device_rf_params_t(ctypes.Structure):
    _fields_ = [
        ('rf1_freq', ctypes.c_ulonglong),
        ('start_freq', ctypes.c_ulonglong),
        ('stop_freq', ctypes.c_ulonglong),
        ('step_freq', ctypes.c_ulonglong),
        ('sweep_dwell_time', ctypes.c_uint),
        ('sweep_cycles', ctypes.c_uint),
        ('buffer_points', ctypes.c_uint),
        ('rf_level', ctypes.c_float),
        ('rf2_freq', ctypes.c_ushort),
    ]

    def print_params(self):
        print('\ndevice rf params:\n'
              + 'rf1_freq = ' + str(self.rf1_freq) + '\n'
              + 'start_freq = ' + str(self.start_freq) + '\n'
              + 'stop_freq = ' + str(self.stop_freq) + '\n'
              + 'step_freq = ' + str(self.step_freq) + '\n'
              + 'sweep_dwell_time = ' + str(self.sweep_dwell_time) + '\n'
              + 'sweep_cycles = ' + str(self.sweep_cycles) + '\n'
              + 'buffer_points = ' + str(self.buffer_points) + '\n'
              + 'rf_level = ' + str(self.rf_level) + '\n'
              + 'rf2_freq = ' + str(self.rf2_freq))


class list_mode_t(ctypes.Structure):
    _fields_ = [
        ('sss_mode', ctypes.c_ubyte),
        ('sweep_dir', ctypes.c_ubyte),
        ('tri_waveform', ctypes.c_ubyte),
        ('hw_trigger', ctypes.c_ubyte),
        ('step_on_hw_trig', ctypes.c_ubyte),
        ('return_to_start', ctypes.c_ubyte),
        ('trig_out_enable', ctypes.c_ubyte),
        ('trig_out_on_cycle', ctypes.c_ubyte),
    ]

    def print_params(self):
        print('\nlist mode params:\n'
              + 'sss_mode = ' + str(self.sss_mode) + '\n'
              + 'sweep_dir = ' + str(self.sweep_dir) + '\n'
              + 'tri_waveform = ' + str(self.tri_waveform) + '\n'
              + 'hw_trigger = ' + str(self.hw_trigger) + '\n'
              + 'step_on_hw_trig = ' + str(self.step_on_hw_trig) + '\n'
              + 'return_to_start = ' + str(self.return_to_start) + '\n'
              + 'trig_out_enable = ' + str(self.trig_out_enable) + '\n'
              + 'trig_out_on_cycle = ' + str(self.trig_out_on_cycle))


class pll_status_t(ctypes.Structure):
    _fields_ = [
        ('sum_pll_ld', ctypes.c_ubyte),
        ('crs_pll_ld', ctypes.c_ubyte),
        ('fine_pll_ld', ctypes.c_ubyte),
        ('crs_ref_pll_ld', ctypes.c_ubyte),
        ('crs_aux_pll_ld', ctypes.c_ubyte),
        ('ref_100_pll_ld', ctypes.c_ubyte),
        ('ref_10_pll_ld', ctypes.c_ubyte),
        ('rf2_pll_ld', ctypes.c_ubyte),
    ]

    def print_params(self):
        print('\npll status params:\n'
              + 'sum_pll_ld = ' + str(self.sum_pll_ld) + '\n'
              + 'crs_pll_ld = ' + str(self.crs_pll_ld) + '\n'
              + 'fine_pll_ld = ' + str(self.fine_pll_ld) + '\n'
              + 'crs_ref_pll_ld = ' + str(self.crs_ref_pll_ld) + '\n'
              + 'crs_aux_pll_ld = ' + str(self.crs_aux_pll_ld) + '\n'
              + 'ref_100_pll_ld = ' + str(self.ref_100_pll_ld) + '\n'
              + 'ref_10_pll_ld = ' + str(self.ref_10_pll_ld) + '\n'
              + 'rf2_pll_ld = ' + str(self.rf2_pll_ld))


class operate_status_t(ctypes.Structure):
    _fields_ = [
        ('rf1_lock_mode', ctypes.c_ubyte),
        ('rf1_loop_gain', ctypes.c_ubyte),
        ('device_access', ctypes.c_ubyte),
        ('rf2_standby', ctypes.c_ubyte),
        ('rf1_standby', ctypes.c_ubyte),
        ('auto_pwr_disable', ctypes.c_ubyte),
        ('alc_mode', ctypes.c_ubyte),
        ('rf1_out_enable', ctypes.c_ubyte),
        ('ext_ref_lock_enable', ctypes.c_ubyte),
        ('ext_ref_detect', ctypes.c_ubyte),
        ('ref_out_select', ctypes.c_ubyte),
        ('list_mode_running', ctypes.c_ubyte),
        ('rf1_mode', ctypes.c_ubyte),
        ('over_temp', ctypes.c_ubyte),
        ('harmonic_ss', ctypes.c_ubyte),
    ]

    def print_params(self):
        print('\noperate mode status: \n'
              + 'rf1_lock_mode = ' + str(self.rf1_lock_mode) + '\n'
              + 'rf1_loop_gain = ' + str(self.rf1_loop_gain) + '\n'
              + 'device_access = ' + str(self.device_access) + '\n'
              + 'rf2_standby = ' + str(self.rf2_standby) + '\n'
              + 'rf1_standby = ' + str(self.rf1_standby) + '\n'
              + 'auto_pwr_disable = ' + str(self.auto_pwr_disable) + '\n'
              + 'alc_mode = ' + str(self.alc_mode) + '\n'
              + 'rf1_out_enable = ' + str(self.rf1_out_enable) + '\n'
              + 'ext_ref_lock_enable = ' + str(self.ext_ref_lock_enable) + '\n'
              + 'ext_ref_detect = ' + str(self.ext_ref_detect) + '\n'
              + 'ref_out_select = ' + str(self.ref_out_select) + '\n'
              + 'list_mode_running = ' + str(self.list_mode_running) + '\n'
              + 'rf1_mode = ' + str(self.rf1_mode) + '\n'
              + 'over_temp = ' + str(self.over_temp) + '\n'
              + 'harmonic_ss = ' + str(self.harmonic_ss))


class device_status_t(ctypes.Structure):
    _fields_ = [
        ('list_mode_t', list_mode_t),
        ('operate_status_t', operate_status_t),
        ('pll_status_t', pll_status_t),
    ]

    def print_params(self):
        self.list_mode_t.print_params()
        self.operate_status_t.print_params()
        self.pll_status_t.print_params()


class date(ctypes.Structure):
    _fields_ = [
        ('year', ctypes.c_ubyte),
        ('month', ctypes.c_ubyte),
        ('day', ctypes.c_ubyte),
        ('hour', ctypes.c_ubyte),
    ]


class device_info_t(ctypes.Structure):
    _fields_ = [
        ('product_serial_number', ctypes.c_ubyte),
        ('hardware_revision', ctypes.c_float),
        ('firmware_revision', ctypes.c_float),
        ('man_date', date),
    ]


# The SC5511A API returns a device handle from sc5511a_open_device.
# The old driver used POINTER(c_int), so keep that ABI assumption.
DEVICE_HANDLE = ctypes.POINTER(ctypes.c_int)


def _configure_dll_functions():
    """Declare ctypes prototypes used by this driver.

    Prototypes catch type mistakes early in Python 3 and make pointer passing
    deterministic.
    """
    lb_dll.sc5511a_open_device.argtypes = [ctypes.c_char_p]
    lb_dll.sc5511a_open_device.restype = DEVICE_HANDLE

    lb_dll.sc5511a_get_device_status.argtypes = [DEVICE_HANDLE, ctypes.POINTER(device_status_t)]
    lb_dll.sc5511a_get_device_status.restype = ctypes.c_int

    lb_dll.sc5511a_get_rf_parameters.argtypes = [DEVICE_HANDLE, ctypes.POINTER(device_rf_params_t)]
    lb_dll.sc5511a_get_rf_parameters.restype = ctypes.c_int

    lb_dll.sc5511a_set_rf_mode.argtypes = [DEVICE_HANDLE, ctypes.c_ubyte]
    lb_dll.sc5511a_set_rf_mode.restype = ctypes.c_int

    lb_dll.sc5511a_set_output.argtypes = [DEVICE_HANDLE, ctypes.c_ubyte]
    lb_dll.sc5511a_set_output.restype = ctypes.c_int

    lb_dll.sc5511a_set_freq.argtypes = [DEVICE_HANDLE, ctypes.c_ulonglong]
    lb_dll.sc5511a_set_freq.restype = ctypes.c_int

    lb_dll.sc5511a_set_level.argtypes = [DEVICE_HANDLE, ctypes.c_float]
    lb_dll.sc5511a_set_level.restype = ctypes.c_int


_configure_dll_functions()


class SC5511A(Instrument):

    def __init__(self, name, devid=None, serial=None):
        super(SC5511A, self).__init__(name)

        if devid is None:
            raise ValueError('SignalCore driver needs devid')

        # Keep the bytes object alive for as long as the instrument object exists.
        self._dev_num_bytes = _to_bytes(devid)
        self.dev_num = ctypes.c_char_p(self._dev_num_bytes)

        self._handle = lb_dll.sc5511a_open_device(self.dev_num)
        if not self._handle:
            raise RuntimeError('Could not open SignalCore SC5511A device %r' % self._dev_num_bytes)

        device_rf_params = device_rf_params_t()
        device_status = device_status_t()

        lb_dll.sc5511a_get_device_status(self._handle, ctypes.byref(device_status))
        lb_dll.sc5511a_get_rf_parameters(self._handle, ctypes.byref(device_rf_params))

        lb_dll.sc5511a_set_rf_mode(self._handle, ctypes.c_ubyte(0))
        lb_dll.sc5511a_set_output(self._handle, ctypes.c_ubyte(1))

        self._min_freq = 100000000
        self._max_freq = 20000000000
        self._min_power = -40
        self._max_power = 20

        self.add_parameter('frequency', type=float,
                           flags=Instrument.FLAG_GETSET, units='Hz',
                           minval=self._min_freq, maxval=self._max_freq,
                           display_scale=6, value=device_rf_params.rf1_freq)
        self.add_parameter('power', type=float,
                           flags=Instrument.FLAG_GETSET, units='dBm',
                           minval=self._min_power, maxval=self._max_power,
                           format='%.02f', value=device_rf_params.rf_level)
        self.add_parameter('rf_on', type=bool,
                           flags=Instrument.FLAG_GETSET, value=True)

    def do_get_frequency(self):
        device_rf_params = device_rf_params_t()
        lb_dll.sc5511a_get_rf_parameters(self._handle, ctypes.byref(device_rf_params))
        return float(device_rf_params.rf1_freq)

    def do_set_frequency(self, freq_Hz):
        return lb_dll.sc5511a_set_freq(self._handle, ctypes.c_ulonglong(int(freq_Hz)))

    def do_get_power(self):
        device_rf_params = device_rf_params_t()
        lb_dll.sc5511a_get_rf_parameters(self._handle, ctypes.byref(device_rf_params))
        return float(device_rf_params.rf_level)

    def do_set_power(self, power):
        return lb_dll.sc5511a_set_level(self._handle, ctypes.c_float(float(power)))

    def do_get_rf_on(self):
        device_status = device_status_t()
        lb_dll.sc5511a_get_device_status(self._handle, ctypes.byref(device_status))
        return bool(device_status.operate_status_t.rf1_out_enable)

    def do_set_rf_on(self, val):
        return lb_dll.sc5511a_set_output(self._handle, ctypes.c_ubyte(1 if val else 0))
