# -*- coding: utf-8 -*-

from ctypes import *
import numpy
from scipy.signal import get_window
import matplotlib.pyplot as plt
import seaborn as sns; sns.set() # styling

smlib = cdll.sm_api

SM_FALSE = 0
SM_TRUE = 1

SM_MAX_DEVICES = 9

SM200A_AUTO_ATTEN = -1
SM200A_MAX_ATTEN = 6

SM_MODE_IDLE = 0
SM_MODE_SWEEPING = 1
SM_MODE_REAL_TIME = 2
SM_MODE_IQ = 3
SM_MODE_AUDIO = 4

SM_SWEEP_SPEED_AUTO = 0
SM_SWEEP_SPEED_NORMAL = 1
SM_SWEEP_SPEED_FAST = 2

SM_POWER_STATE_ON = 0
SM_POWER_STATE_STANDBY = 1

SM_DETECTOR_AVERAGE = 0
SM_DETECTOR_MIN_MAX = 1

SM_SCALE_LOG = 0
SM_SCALE_LIN = 1
SM_SCALE_FULL_SCALE = 2

SM_VIDEO_LOG = 0
SM_VIDEO_VOLTAGE = 1
SM_VIDEO_POWER = 2
SM_VIDEO_SAMPLE = 3

SM_WINDOW_FLAT_TOP = 0
# SM_WINDOW_DOLPH_CHEBYSHEV = 1
SM_WINDOW_NUTALL = 2
SM_WINDOW_BLACKMAN = 3
SM_WINDOW_HAMMING = 4
SM_WINDOW_GAUSSIAN_6_DB = 5
SM_WINDOW_RECT = 6

SM_IQ_STREAMING = 0
SM_IQ_FULL_BAND = 1
SM_IQ_WIDEBAND_COMPRESSED = 2

SM_TRIGGER_TYPE_IMMEDIATE = 0
SM_TRIGGER_TYPE_VIDEO = 1
SM_TRIGGER_TYPE_EXTERNAL= 2
SM_TRIGGER_TYPE_FREQUENCY_MASK = 3

SM_TRIGGER_EDGE_RISING = 0
SM_TRIGGER_EDGE_FALLING = 1

SM_GPIO_STATE_OUTPUT = 0
SM_GPIO_STATE_INPUT = 1

SM_REFERENCE_USE_INTERNAL = 0
SM_REFERENCE_USE_EXTERNAL = 1

SM_DEVICE_TYPE_SM200A = 0

SM_AUDIO_TYPE_AM = 0
SM_AUDIO_TYPE_FM = 1
SM_AUDIO_TYPE_USB = 2
SM_AUDIO_TYPE_LSB = 3
SM_AUDIO_TYPE_CW = 4

SM_GPS_STATE_NOT_PRESENT = 0
SM_GPS_STATE_LOCKED = 1
SM_GPS_STATE_DISCIPLINED = 2

class SmGPIOStep(Structure):
    _fields_ = [("freq", c_double),
                ("mask", c_ubyte)]

class SmDeviceDiagnostics(Structure):
    _fields_ = [("voltage", c_float),
                ("currentInput", c_float),
                ("currentOCXO", c_float),
                ("current58", c_float),
                ("tempFPGAInternal", c_float),
                ("tempFPGANear", c_float),
                ("tempOCXO", c_float),
                ("tempVCO", c_float),
                ("tempRFBoardLO", c_float),
                ("tempPowerSupply", c_float)]


# ----------------------- Internal Mappings to C API ------------------------ #
smGetDeviceList = smlib.smGetDeviceList
smGetDeviceList.argtypes = [numpy.ctypeslib.ndpointer(c_int, ndim=1, flags='C'),
                            POINTER(c_int)]
smOpenDevice = smlib.smOpenDevice
smOpenDeviceBySerial = smlib.smOpenDeviceBySerial
smCloseDevice = smlib.smCloseDevice
smPreset = smlib.smPreset
smPresetSerial = smlib.smPresetSerial

smGetDeviceInfo = smlib.smGetDeviceInfo
smGetFirmwareVersion = smlib.smGetFirmwareVersion

smGetDeviceDiagnostics = smlib.smGetDeviceDiagnostics
smGetFullDeviceDiagnostics = smlib.smGetFullDeviceDiagnostics

smSetPowerState = smlib.smSetPowerState
smGetPowerState = smlib.smGetPowerState

smSetAttenuator = smlib.smSetAttenuator
smGetAttenuator = smlib.smGetAttenuator

smSetRefLevel = smlib.smSetRefLevel
smGetRefLevel = smlib.smGetRefLevel

smSetPreselector = smlib.smSetPreselector
smGetPreselector = smlib.smGetPreselector

smSetGPIOState = smlib.smSetGPIOState
smGetGPIOState = smlib.smGetGPIOState
smWriteGPIOImm = smlib.smWriteGPIOImm
smReadGPIOImm = smlib.smReadGPIOImm
smWriteSPI = smlib.smWriteSPI
smSetGPIOSweepDisabled = smlib.smSetGPIOSweepDisabled
smSetGPIOSweep = smlib.smSetGPIOSweep
smSetGPIOSweep.argtypes = [c_int,
                           numpy.ctypeslib.ndpointer(SmGPIOStep, ndim=1, flags='C'),
                           c_int]
smSetGPIOSwitchingDisabled = smlib.smSetGPIOSwitchingDisabled
smSetGPIOSwitching = smlib.smSetGPIOSwitching
smSetGPIOSwitching.argtypes = [c_int,
                               numpy.ctypeslib.ndpointer(c_ubyte, ndim=1, flags='C'),
                               numpy.ctypeslib.ndpointer(c_uint, ndim=1, flags='C'),
                               c_int]

smSetExternalReference = smlib.smSetExternalReference
smGetExternalReference = smlib.smGetExternalReference
smSetReference = smlib.smSetReference
smGetReference = smlib.smGetReference

smSetGPSTimebaseUpdate = smlib.smSetGPSTimebaseUpdate
smGetGPSTimebaseUpdate = smlib.smGetGPSTimebaseUpdate

smGetGPSState = smlib.smGetGPSState

smSetSweepSpeed = smlib.smSetSweepSpeed
smSetSweepCenterSpan = smlib.smSetSweepCenterSpan
smSetSweepStartStop = smlib.smSetSweepStartStop
smSetSweepCoupling = smlib.smSetSweepCoupling
smSetSweepDetector = smlib.smSetSweepDetector
smSetSweepScale = smlib.smSetSweepScale
smSetSweepWindow = smlib.smSetSweepWindow
smSetSweepSpurReject = smlib.smSetSweepSpurReject

smSetRealTimeCenterSpan = smlib.smSetRealTimeCenterSpan
smSetRealTimeRBW = smlib.smSetRealTimeRBW
smSetRealTimeDetector = smlib.smSetRealTimeDetector
smSetRealTimeScale = smlib.smSetRealTimeScale
smSetRealTimeWindow = smlib.smSetRealTimeWindow

smSetIQCaptureType = smlib.smSetIQCaptureType
smSetIQCenterFreq = smlib.smSetIQCenterFreq
smSetIQSampleRate = smlib.smSetIQSampleRate
smSetIQBandwidth = smlib.smSetIQBandwidth
smSetIQExtTriggerEdge = smlib.smSetIQExtTriggerEdge
smGetIQExtTriggerEdge = smlib.smGetIQExtTriggerEdge

smSetAudioCenterFreq = smlib.smSetAudioCenterFreq
smSetAudioType = smlib.smSetAudioType
smSetAudioFilters = smlib.smSetAudioFilters
smSetAudioFMDeemphasis = smlib.smSetAudioFMDeemphasis

smConfigure = smlib.smConfigure
smGetCurrentMode = smlib.smGetCurrentMode
smAbort = smlib.smAbort

smGetSweepParameters = smlib.smGetSweepParameters
smGetRealTimeParameters = smlib.smGetRealTimeParameters
smGetIQParameters = smlib.smGetIQParameters

smGetSweep = smlib.smGetSweep
smGetSweep.argtypes = [c_int,
                       numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                       numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                       POINTER(c_longlong)]

smStartSweep = smlib.smStartSweep
smFinishSweep = smlib.smFinishSweep
smFinishSweep.argtypes = [c_int,
                          numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                          numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                          numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                          POINTER(c_int),
                          POINTER(c_longlong)]

smGetRealTimeFrame = smlib.smGetRealTimeFrame
smGetRealTimeFrame.argtypes = [c_int, c_int,
                          numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                          numpy.ctypeslib.ndpointer(numpy.float32, ndim=1, flags='C'),
                          POINTER(c_longlong)]

smGetIQ = smlib.smGetIQ
smGetIQ.argtypes = [c_int, numpy.ctypeslib.ndpointer(numpy.complex64, ndim=1, flags='C'),
                    c_int, numpy.ctypeslib.ndpointer(c_double, ndim=1, flags='C'),
                    c_int, POINTER(c_longlong), c_int, POINTER(c_int), POINTER(c_int)]

smGetAudio = smlib.smGetAudio

smGetGPSInfo = smlib.smGetGPSInfo
smGetGPSInfo.argtypes = [c_int, c_int, POINTER(c_int), POINTER(c_longlong),
                         POINTER(c_double), POINTER(c_double), POINTER(c_double),
                         numpy.ctypeslib.ndpointer(c_char, ndim=1, flags='C'),
                         POINTER(c_int)]

smSetFanThreshold = smlib.smSetFanThreshold
smGetFanThreshold = smlib.smGetFanThreshold

smGetCalDate = smlib.smGetCalDate

smGetAPIVersion = smlib.smGetAPIVersion
smGetAPIVersion.restype = c_char_p
smGetErrorString = smlib.smGetErrorString
smGetErrorString.restype = c_char_p
smGetProductID = smlib.smGetProductID
smGetProductID.restype = c_char_p


# --------------------------------- Utility --------------------------------- #
def print_status(handle, status):
    error_string = smGetErrorString(status)
    print("id:\t", handle)
    print("status:\t", status)
    print(error_string)

def print_status_if_error(handle, status, function):
    if(status != 0):
        print ("\n", function)
        print_status(handle, status)


# --------------------------------- Public ---------------------------------- #
def sm_get_device_list():
    serials = numpy.zeros(SM_MAX_DEVICES).astype(c_int)
    device_count = c_int(-1)
    status = smGetDeviceList(serials, byref(device_count))
    print_status_if_error(handle, status, "smGetDeviceList")
    return serials, device_count.value, status

def sm_open_device():
    handle = c_int(-1)
    status = smOpenDevice(byref(handle))
    print_status_if_error(handle, status, "smOpenDevice")
    return handle.value, status

def sm_open_device_by_serial(serial_number):
    handle = c_int(-1)
    status = smOpenDeviceBySerial(byref(handle), serial_number)
    print_status_if_error(handle, status, "smOpenDeviceBySerial")
    return handle.value, status

def sm_close_device(handle):
    status = smCloseDevice(handle)
    print_status_if_error(handle, status, "smCloseDevice")
    return status

def sm_preset(handle):
    status = smPreset(handle)
    print_status_if_error(handle, status, "smPreset")
    return status

def sm_preset_serial(serial_number):
    status = smPresetSerial(serial_number)
    print_status_if_error(handle, status, "smPresetSerial")
    return status

def sm_get_device_info(handle):
    device_type = c_int(-1)
    serial_number = c_int(-1)
    status = smGetDeviceInfo(handle, byref(device_type), byref(serial_number))
    print_status_if_error(handle, status, "smGetDeviceInfo")
    return device_type.value, serial_number.value, status

def sm_get_firmware_version(handle):
    major = c_int(-1)
    minor = c_int(-1)
    revision = c_int(-1)
    status = smGetFirmwareVersion(handle, byref(major), byref(minor), byref(revision))
    print_status_if_error(handle, status, "smGetFirmwareVersion")
    return major.value, minor.value, revision.value, status

def sm_get_device_diagnostics(handle):
    voltage = c_float(-1)
    current = c_float(-1)
    temperature = c_float(-1)
    status = smGetDeviceDiagnostics(handle, byref(voltage), byref(current), byref(temperature))
    print_status_if_error(handle, status, "smGetDeviceDiagnostics")
    return voltage.value, current.value, temperature.value, status

def sm_get_full_device_diagnostics(handle):
    diagnostics = SmDeviceDiagnostics()
    status = smGetDeviceDiagnostics(handle, byref(diagnostics))
    print_status_if_error(handle, status, "smGetDeviceDiagnostics")
    return diagnostics.value, status

def sm_set_power_state(handle, power_state):
    status = smSetPowerState(handle, power_state)
    print_status_if_error(handle, status, "smSetPowerState")
    return status

def sm_get_power_state(handle):
    power_state = c_int(-1)
    status = smGetPowerState(handle, byref(power_state))
    print_status_if_error(handle, status, "smGetPowerState")
    return power_state.value, status

def sm_set_attenuator(handle, atten):
    status = smSetAttenuator(handle, atten)
    print_status_if_error(handle, status, "smSetAttenuator")
    return status

def sm_get_attenuator(handle):
    atten = c_int(-1)
    status = smGetAttenuator(handle, byref(atten))
    print_status_if_error(handle, status, "smGetAttenuator")
    return atten.value, status

def sm_set_ref_level(handle, ref_level):
    status = smSetRefLevel(handle, c_double(ref_level))
    print_status_if_error(handle, status, "smSetRefLevel")
    return status

def sm_get_ref_level(handle):
    ref_level = c_double(-1)
    status = smGetRefLevel(handle, byref(ref_level))
    print_status_if_error(handle, status, "smGetRefLevel")
    return ref_level.value, status

def sm_set_preselector(handle, enabled):
    enabledInt = SM_TRUE if enabled is True else SM_FALSE
    status = smSetPreselector(handle, enabledInt)
    print_status_if_error(handle, status, "smSetPreselector")
    return status

def sm_get_preselector(handle):
    enabledInt = c_int(-1)
    status = smGetPreselector(handle, byref(enabledInt))
    enabled = True if enabledInt is SM_TRUE else False
    print_status_if_error(handle, status, "smGetPreselector")
    return enabled, status

def sm_set_GPIO_state(handle, lower_state, upper_state):
    status = smSetGPIOState(handle, lower_state, upper_state)
    print_status_if_error(handle, status, "smSetGPIOState")
    return status

def sm_get_GPIO_state(handle):
    lower_state = c_int(-1)
    upper_state = c_int(-1)
    status = smGetGPIOState(handle, byref(lower_state), byref(upper_state))
    print_status_if_error(handle, status, "smGetGPIOState")
    return lower_state.value, upper_state.value, status

def sm_write_GPIO_imm(handle, data):
    status = smWriteGPIOImm(handle, data)
    print_status_if_error(handle, status, "smWriteGPIOImm")
    return status

def sm_read_GPIO_imm(handle):
    data = c_ubyte(-1)
    status = smReadGPIOImm(handle, byref(data))
    print_status_if_error(handle, status, "smReadGPIOImm")
    return data.value, status

def sm_write_SPI(handle, data, byte_count):
    status = smWriteSPI(handle, data, byte_count)
    print_status_if_error(handle, status, "smWriteSPI")
    return status

def sm_set_GPIO_sweep_disabled(handle):
    status = smSetGPIOSweepDisabled(handle)
    print_status_if_error(handle, status, "smSetGPIOSweepDisabled")
    return status

def sm_set_GPIO_sweep(handle, steps, step_count):
    status = smSetGPIOSweep(handle, steps, step_count)
    print_status_if_error(handle, status, "smSetGPIOSweep")
    return status

def sm_set_GPIO_switching_disabled(handle):
    status = smSetGPIOSwitchingDisabled(handle)
    print_status_if_error(handle, status, "smSetGPIOSwitchingDisabled")
    return status

def sm_set_GPIO_switching(handle, gpio, counts, gpio_steps):
    status = smSetGPIOSwitching(handle, gpio, counts, gpio_steps)
    print_status_if_error(handle, status, "smSetGPIOSwitching")
    return status

def sm_set_external_reference(handle, enabled):
    status = smSetExternalReference(handle, enabled)
    print_status_if_error(handle, status, "smSetExternalReference")
    return status

def sm_get_external_reference(handle):
    enabled = c_int(-1)
    status = smGetExternalReference(handle, byref(enabled))
    print_status_if_error(handle, status, "smGetExternalReference")
    return enabled.value, status

def sm_set_reference(handle, reference):
    status = smSetReference(handle, reference)
    print_status_if_error(handle, status, "smSetReference")
    return status

def sm_get_reference(handle):
    reference = c_int(-1)
    status = smGetReference(handle, byref(reference))
    print_status_if_error(handle, status, "smGetReference")
    return reference.value, status

def sm_set_GPS_timebase_update(handle, enabled):
    status = smSetGPSTimebaseUpdate(handle, enabled)
    print_status_if_error(handle, status, "smSetGPSTimebaseUpdate")
    return status

def sm_get_GPS_timebase_update(handle):
    status = smGetGPSTimebaseUpdate(handle, byref(enabled))
    print_status_if_error(handle, status, "smGetGPSTimebaseUpdate")
    return enabled.value, status

def sm_get_GPS_state(handle):
    GPS_state = c_int(-1)
    status = smGetGPSState(handle, byref(GPS_state))
    print_status_if_error(handle, status, "smGetGPSState")
    return GPS_state.value, status

def sm_set_sweep_speed(handle, sweep_speed):
    status = smSetSweepSpeed(handle, sweep_speed)
    print_status_if_error(handle, status, "smSetSweepSpeed")
    return status

def sm_set_sweep_center_span(handle, center_freq_Hz, span_Hz):
    status = smSetSweepCenterSpan(handle, c_double(center_freq_Hz), c_double(span_Hz))
    print_status_if_error(handle, status, "smSetSweepCenterSpan")
    return status

def sm_set_sweep_start_stop(handle, start_freq_Hz, stop_freq_Hz):
    status = smSetSweepStartStop(handle, c_double(start_freq_Hz), c_double(stop_freq_Hz))
    print_status_if_error(handle, status, "smSetSweepStartStop")
    return status

def sm_set_sweep_coupling(handle, rbw, vbw, sweep_time):
    status = smSetSweepCoupling(handle, c_double(rbw), c_double(vbw), c_double(sweep_time))
    print_status_if_error(handle, status, "smSetSweepCoupling")
    return status

def sm_set_sweep_detector(handle, detector, video_units):
    status = smSetSweepDetector(handle, detector, video_units)
    print_status_if_error(handle, status, "smSetSweepDetector")
    return status

def sm_set_sweep_scale(handle, scale):
    status = smSetSweepScale(handle, scale)
    print_status_if_error(handle, status, "smSetSweepScale")
    return status

def sm_set_sweep_window(handle, window):
    status = smSetSweepWindow(handle, window)
    print_status_if_error(handle, status, "smSetSweepWindow")
    return status

def sm_set_sweep_spur_reject(handle, spur_reject_enabled):
    status = smSetSweepSpurReject(handle, spur_reject_enabled)
    print_status_if_error(handle, status, "smSetSweepSpurReject")
    return status

def sm_set_real_time_center_span(handle, center_freq_Hz, span_Hz):
    status = smSetRealTimeCenterSpan(handle, c_double(center_freq_Hz), c_double(span_Hz))
    print_status_if_error(handle, status, "smSetRealTimeCenterSpan")
    return status

def sm_set_real_time_RBW(handle, rbw):
    status = smSetRealTimeRBW(handle, c_double(rbw))
    print_status_if_error(handle, status, "smSetRealTimeRBW")
    return status

def sm_set_real_time_detector(handle, detector):
    status = smSetRealTimeDetector(handle, detector)
    print_status_if_error(handle, status, "smSetRealTimeDetector")
    return status

def sm_set_real_time_scale(handle, scale, frame_ref, frame_scale):
    status = smSetRealTimeScale(handle, scale, c_double(frame_ref), c_double(frame_scale))
    print_status_if_error(handle, status, "smSetRealTimeScale")
    return status

def sm_set_real_time_window(handle, window):
    status = smSetRealTimeWindow(handle, window)
    print_status_if_error(handle, status, "smSetRealTimeWindow")
    return status

def sm_set_IQ_capture_type(handle, capture_type):
    status = smSetIQCaptureType(handle, capture_type) # SmIQCaptureType
    print_status_if_error(handle, status, "smSetIQCaptureType")
    return status

def sm_set_IQ_center_freq(handle, center_freq_Hz):
    status = smSetIQCenterFreq(handle, c_double(center_freq_Hz))
    print_status_if_error(handle, status, "smSetIQCenterFreq")
    return status

def sm_set_IQ_sample_rate(handle, decimation):
    status = smSetIQSampleRate(handle, decimation)
    print_status_if_error(handle, status, "smSetIQSampleRate")
    return status

def sm_set_IQ_bandwidth(handle, enable_software_filter, bandwidth):
    status = smSetIQBandwidth(handle, enable_software_filter, c_double(bandwidth))
    print_status_if_error(handle, status, "smSetIQBandwidth")
    return status

def sm_set_IQ_external_trigger_edge(handle, edge):
    status = smSetTriggerEdge(handle, edge)
    print_status_if_error(handle, status, "smSetTriggerEdge")
    return status

def sm_get_IQ_external_trigger_edge(handle):
    edge = c_int(-1)
    status = smGetTriggerEdge(handle, byref(edge))
    print_status_if_error(handle, status, "smGetTriggerEdge")
    return edge.value, status

def sm_set_audio_center_freq(handle, center_freq_Hz):
    status = smSetAudioCenterFreq(handle, c_double(center_freq_Hz))
    print_status_if_error(handle, status, "smSetAudioCenterFreq")
    return status

def sm_set_audio_type(handle, audio_type):
    status = smSetAudioType(handle, audioType)
    print_status_if_error(handle, status, "smSetAudioType")
    return status

def sm_set_audio_filters(handle, if_bandwidth, audio_lpf, audio_hpf):
    status = smSetAudioFilters(handle, c_double(if_bandwidth), c_double(audio_lpf), c_double(audio_hpf))
    print_status_if_error(handle, status, "smSetAudioFilters")
    return status

def sm_set_audio_FM_deemphasis(handle, deemphasis):
    status = smSetAudioFMDeemphasis(handle, c_double(deemphasis))
    print_status_if_error(handle, status, "smSetAudioFMDeemphasis")
    return status

def sm_configure(handle, mode):
    status = smConfigure(handle, mode)
    print_status_if_error(handle, status, "smConfigure")
    return status

def sm_get_current_mode(handle):
    mode = c_int(-1)
    status = smGetCurrentMode(handle, byref(mode))
    print_status_if_error(handle, status, "smGetCurrentMode")
    return mode.value, status

def sm_abort(handle):
    status = smAbort(handle)
    print_status_if_error(handle, status, "smAbort")
    return status

def sm_get_sweep_parameters(handle):
    actual_RBW = c_double(-1)
    actual_VBW = c_double(-1)
    actual_start_freq = c_double(-1)
    bin_size = c_double(-1)
    sweep_size = c_int(-1)
    status = smGetSweepParameters(handle, byref(actual_RBW), byref(actual_VBW), byref(actual_start_freq), byref(bin_size), byref(sweep_size))
    print_status_if_error(handle, status, "smGetSweepParameters")
    return actual_RBW.value, actual_VBW.value, actual_start_freq.value, bin_size.value, sweep_size.value, status

def sm_get_real_time_parameters(handle):
    actual_RBW = c_double(-1)
    sweep_size = c_int(-1)
    actual_start_freq = c_double(-1)
    bin_size = c_double(-1)
    frame_width = c_int(-1)
    frame_height = c_int(-1)
    poi = c_double(-1)
    status = smGetRealTimeParameters(handle, byref(actual_RBW), byref(sweep_size), byref(actual_start_freq), byref(bin_size), byref(frame_width), byref(frame_height), byref(poi))
    print_status_if_error(handle, status, "smGetRealTimeParameters")
    return actual_RBW.value, sweep_Size.value, actual_start_freq.value, bin_size.value, frame_width.value, frame_height.value, poi.value, status

def sm_get_IQ_parameters(handle):
    sample_rate = c_double(-1)
    bandwidth = c_double(-1)
    status = smGetIQParameters(handle, byref(sample_rate), byref(bandwidth))
    print_status_if_error(handle, status, "smGetIQParameters")
    return sample_rate.value, bandwidth.value, status

def sm_get_sweep(handle):
    actual_RBW, actual_VBW, actual_start_freq, bin_size, sweep_size, status = sm_get_sweep_parameters(handle)
    sweep_min = numpy.zeros(sweep_size).astype(numpy.float32)
    sweep_max = numpy.zeros(sweep_size).astype(numpy.float32)
    ns_since_epoch = c_longlong(-1)
    status = smGetSweep(handle, sweep_min, sweep_max, byref(ns_since_epoch))
    print_status_if_error(handle, status, "smGetSweep")
    return sweep_min, sweep_max, ns_since_epoch.value, status

def sm_start_sweep(handle, pos):
    status = smStartSweep(handle, pos)
    print_status_if_error(handle, status, "smStartSweep")
    return status

def sm_finish_sweep(handle, pos):
    actual_RBW, actual_VBW, actual_start_freq, bin_size, sweep_size, status = sm_get_sweep_parameters(handle)
    sweep_min = numpy.zeros(sweep_size).astype(numpy.float32)
    sweep_max = numpy.zeros(sweep_size).astype(numpy.float32)
    ns_since_epoch = c_longlong(-1)
    status = smFinishSweep(handle, pos, sweep_min, sweep_max, byref(ns_since_epoch))
    print_status_if_error(handle, status, "smFinishSweep")
    return sweep_min.value, sweep_max.value, ns_since_epoch.value, status

def sm_get_real_time_frame(handle):
    actual_RBW, sweep_Size, actual_start_freq, bin_size, frame_width, frame_height, poi, status = sm_get_real_time_parameters(handle)
    frame = numpy.zeros(frame_width * frame_height).astype(numpy.float32)
    sweep_min = numpy.zeros(sweep_size).astype(numpy.float32)
    sweep_max = numpy.zeros(sweep_size).astype(numpy.float32)
    frame_count = c_int(-1)
    ns_since_epoch = c_longlong(-1)
    status = smGetRealTimeFrame(handle, frame, sweep_min, sweep_max, byref(frame_count), byref(ns_since_epoch))
    print_status_if_error(handle, status, "smGetRealTimeFrame")
    return frame, sweep_min, sweep_max, frame_count.value, ns_since_epoch.value, status

def sm_get_IQ(handle, iq_buf_size, trigger_buf_size, purge):
    iq_buf = numpy.zeros(iq_buf_size).astype(numpy.complex64)
    triggers = numpy.zeros(trigger_buf_size).astype(c_double)
    ns_since_epoch = c_longlong(-1)
    sample_loss = c_int(-1)
    samples_remaining = c_int(-1)
    status = smGetIQ(handle, iq_buf, iq_buf_size,
                     triggers, trigger_buf_size,
                     byref(ns_since_epoch), purge,
                     byref(sample_loss), byref(samples_remaining));
    print_status_if_error(handle, status, "smGetIQ")
    return iq_buf, triggers, ns_since_epoch.value, sample_loss.value, samples_remaining.value, status

def sm_get_audio(handle):
    audio = c_float(-1)
    status = smGetAudio(handle, byref(audio))
    print_status_if_error(handle, status, "smGetAudio")
    return audio.value, status

def sm_get_GPS_info(handle, refresh, nmeaLen):
    updated = c_int(-1)
    sec_since_epoch = c_longlong(-1)
    latitude = c_double(-1)
    longitude = c_double(-1)
    altitude = c_double(-1)
    nmea = numpy.zeros(nmeaLen).astype(c_char)
    status = smGetGPSInfo(handle, refresh, byref(updated), byref(sec_since_epoch), byref(latitude), byref(longitude), byref(altitude), nmea, byref(nmeaLen))
    print_status_if_error(handle, status, "smGetGPSInfo")
    return updated.value, sec_since_epoch.value, latitude.value, longitude.value, altitude.value, nmea, nmea_len.value, status

def sm_set_fan_threshold(handle, temp):
    status = smSetFanThreshold(handle, temp)
    print_status_if_error(handle, status, "smSetFanThreshold")
    return status

def sm_get_fan_threshold(handle):
    temp = c_int(-1)
    status = smGetFanThreshold(handle, byref(temp))
    print_status_if_error(handle, status, "smGetFanThreshold")
    return temp.value, status

def sm_get_cal_date(handle):
    last_cal_date = c_ulonglong(-1)
    status = smGetCalDate(handle, byref(last_cal_date))
    print_status_if_error(handle, status, "smGetCalDate")
    return last_cal_date.value, status

def sm_get_API_version():
    return smGetAPIVersion()

def sm_get_error_string(status):
    return smGetErrorString(status)

def sm_get_product_ID():
    return smGetProductID()
