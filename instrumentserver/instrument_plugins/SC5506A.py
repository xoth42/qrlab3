# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 09:12:40 2017

@author: WangLab
"""

# SignalCore RF Source DLL driver
#

import sys
import time
import ctypes
import ctypes.wintypes as win
import types
import numpy as np
from instrument import Instrument
import logging

SUCCESS = 0
NO_DEVICE = 0

#LB_DLL = r'c:\qrlab\instrumentserver\vnx_fmsynth.dll'
LB_DLL = 'C:\\qrlab\\instrumentserver\\SignalCore\\x64\\sc5506a_usb.dll'
try:
    lb_dll = ctypes.windll.LoadLibrary(LB_DLL)
    #lb_dll = ctypes.cdll.LoadLibrary(LB_DLL)
    
except Exception, e:
    s = 'Unable to load SignalCore DLL, please put sc5506a_usb.dll in instrumentserver directory ' + str(e)
    raise ValueError(s)

class deviceParams_t(ctypes.Structure):
    _fields_ =  [('ch1Frequency', ctypes.c_double),
                     ('ch2Frequency', ctypes.c_double),
                     ('ch1PowerLevel', ctypes.c_float),
                     ('ch2PowerLevel', ctypes.c_float)]
    
    def print_params(self):
        print('\ndevice rf params:\n'
              + 'ch1Frequency = ' + str(self.ch1Frequency) + '\n'
              + 'ch2Frequency = ' + str(self.ch2Frequency) + '\n'
              + 'ch1PowerLevel = ' + str(self.ch1PowerLevel) + '\n'
              + 'ch2PowerLevel = ' + str(self.ch2PowerLevel))
    
class deviceInfo_t(ctypes.Structure):
    _fields_ = [('productSerialNumber', ctypes.c_uint),
                ('rfModuleSerialNumber', ctypes.c_uint),
                ('firmwareRevision', ctypes.c_float),
                ('hardwareRevision', ctypes.c_float),
                ('calDate', ctypes.c_uint),
                ('manDate', ctypes.c_uint)]
    
    def print_params(self):
        print('\ndevice info params:\n'
              + 'productSerialNumber = ' + str(self.productSerialNumber) + '\n'
              + 'rfModuleSerialNumber = ' + str(self.rfModuleSerialNumber) + '\n'
              + 'firmwareRevision = ' + str(self.firmwareRevision) + '\n'
              + 'hardwareRevision = ' + str(self.hardwareRevision) + '\n'
              + 'calDate = ' + str(self.calDate) + '\n'
              + 'manDate = ' + str(self.manDate))
              
        
class deviceStatus_t(ctypes.Structure):
    _fields_ =  [('ch1AutoLevelEnable', ctypes.c_ubyte),
                     ('ch2AutoLevelEnable', ctypes.c_ubyte),
                     ('ch1AlcOpen', ctypes.c_ubyte),
                     ('ch2AlcOpen', ctypes.c_ubyte),
                     ('ch1RfOutEnable', ctypes.c_ubyte),
                     ('ch2RfOutEnable', ctypes.c_ubyte),
                     ('ch1StandbyEnable', ctypes.c_ubyte),
                     ('ch2StandbyEnable', ctypes.c_ubyte),
                     ('ch1SumPllStatus', ctypes.c_ubyte),
                     ('ch1CrsPllStatus', ctypes.c_ubyte),
                     ('ch1FinePllStatus', ctypes.c_ubyte),
                     ('ch2SumPllStatus', ctypes.c_ubyte),
                     ('ch2CrsPllStatus', ctypes.c_ubyte),
                     ('ch2FinePllStatus', ctypes.c_ubyte),
                     ('vcxoPllStatus', ctypes.c_ubyte),
                     ('tcxoPllStatus', ctypes.c_ubyte),
                     ('extRefDetected', ctypes.c_ubyte),
                     ('extRefLockEnable', ctypes.c_ubyte),
                     ('refClkOutEnable', ctypes.c_ubyte),
                     ('deviceAccess', ctypes.c_ubyte)]
    
    def print_params(self):
        print('\ndevice status params:\n'
              + 'ch1AutoLevelEnable = ' + str(self.ch1AutoLevelEnable) + '\n'
              + 'ch2AutoLevelEnable = ' + str(self.ch2AutoLevelEnable) + '\n'
              + 'ch1AlcOpen = ' + str(self.ch1AlcOpen) + '\n'
              + 'ch2AlcOpen = ' + str(self.ch2AlcOpen) + '\n'
              + 'ch1RfOutEnable = ' + str(self.ch1RfOutEnable) + '\n'
              + 'ch2RfOutEnable = ' + str(self.ch2RfOutEnable) + '\n'
              + 'ch1StandbyEnable = ' + str(self.ch1StandbyEnable) + '\n'
              + 'ch2StandbyEnable = ' + str(self.ch2StandbyEnable) + '\n'
              + 'ch1SumPllStatus = ' + str(self.ch1SumPllStatus) + '\n'
              + 'ch1CrsPllStatus = ' + str(self.ch1CrsPllStatus)
              + 'ch1FinePllStatus = ' + str(self.ch1FinePllStatus) + '\n'
              + 'ch2SumPllStatus = ' + str(self.ch2SumPllStatus) + '\n'
              + 'ch2CrsPllStatus = ' + str(self.ch2CrsPllStatus) + '\n'
              + 'ch2FinePllStatus = ' + str(self.ch2FinePllStatus) + '\n'
              + 'vcxoPllStatus = ' + str(self.vcxoPllStatus) + '\n'
              + 'tcxoPllStatus = ' + str(self.tcxoPllStatus)
              + 'extRefDetected = ' + str(self.extRefDetected) + '\n'
              + 'extRefLockEnable = ' + str(self.extRefLockEnable) + '\n'
              + 'refClkOutEnable = ' + str(self.refClkOutEnable) + '\n'
              + 'deviceAccess = ' + str(self.deviceAccess))        

NUM_MAX_DEVICES = 5
ID_BUFFER_SIZE = 8



class SC5506A(Instrument):

    def __init__(self, name, devid=None, serial=None):
        super(SC5506A, self).__init__(name)

        if devid is None:
            raise Exception('SignalCore driver needs devid or serial as parameter')


        
        # This is the code Josh wrote
        string_buffers = [ctypes.create_string_buffer(ID_BUFFER_SIZE) for i in range(NUM_MAX_DEVICES)]
        pointers = (ctypes.c_char_p*NUM_MAX_DEVICES)(*map(ctypes.addressof, string_buffers))
        results = [s.value for s in string_buffers]
        self.dev_num = ctypes.c_char_p(devid)
        lb_dll.sc5506a_OpenDevice.restype = ctypes.POINTER(ctypes.c_int)
        phandle = win.HANDLE()
#        phandle = ctypes.POINTER(ctypes.c_voidp)
#        print(phandle, ctypes.byref(phandle))
        lb_dll.sc5506a_OpenDevice(self.dev_num, ctypes.byref(phandle))
#        print(phandle, phandle.value)
        self._handle = phandle.value
        
        
        deviceParams = deviceParams_t() 
        deviceStatus = deviceStatus_t()

        deviceStatus_temp = ctypes.pointer(deviceStatus)
#        lb_dll.sc5506a_get_device_status.argtypes = [ctypes.POINTER(ctypes.c_int),
#                                                    ctypes.POINTER(device_status_t)]
        lb_dll.sc5506a_GetDeviceStatus(self._handle, deviceStatus_temp.contents)
#        lb_dll.sc5506a_GetDeviceParams(self._handle, device_rf_params) DARIO
        
        
        '''
        # This is the code Jeff wrote, this is probably still wrong
        string_buffers = [ctypes.create_string_buffer(ID_BUFFER_SIZE) for i in range(NUM_MAX_DEVICES)]
        pointers = (ctypes.c_char_p*NUM_MAX_DEVICES)(*map(ctypes.addressof, string_buffers))
        print "THING", lb_dll.sc5506a_search_devices(pointers)
        results = [s.value for s in string_buffers]
        self._handle = lb_dll.sc5506a_open_device(results[0])
        
        device_rf_params = device_rf_params_t()
        device_status = device_status_t()
        print "HANDLE", self._handle
        print "STATS", device_status
        lb_dll.sc5506a_get_device_status(self._handle, device_status)
        lb_dll.sc5506a_get_rf_parameters(self._handle, device_rf_params)
        '''

#        lb_dll.sc5506a_set_rf_mode(self._handle, 0)
#        lb_dll.sc5506a_set_output(self._handle, 1)
        
#        self._serialno = results[0]
        self._min_freq = 25000000    
        self._max_freq = 6000000000
        self._min_power = -50
        self._max_power = 10

        
    
#        self.add_parameter('serial', type=types.StringType,
#            flags=Instrument.FLAG_GET, value=self._serialno)
#        self.add_parameter('handle', type=types.IntType,
#            flags=Instrument.FLAG_GET, value=self._handle)
        self.add_parameter('ch1_frequency', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='Hz',
            minval=self._min_freq, maxval=self._max_freq,
            display_scale=6, value = deviceParams.ch1Frequency)
        self.add_parameter('ch2_frequency', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='MHz',
            minval=self._min_freq, maxval=self._max_freq,
            display_scale=6, value = deviceParams.ch2Frequency)
        self.add_parameter('ch1_power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='dBm',
            minval=self._min_power, maxval=self._max_power,
            format='%.02f', value = deviceParams.ch1PowerLevel)
        self.add_parameter('ch2_power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET, units='dBm',
            minval=self._min_power, maxval=self._max_power,
            format='%.02f', value = deviceParams.ch2PowerLevel)
        self.add_parameter('ch1_output', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET, value = True)
        self.add_parameter('ch2_output', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET, value = True)
        self.add_parameter('ext_locked', type=types.BooleanType,
            flags=Instrument.FLAG_GET, value = True)
        
        
        
        '''



        self.add_parameter('fast_pulse_option', type=types.BooleanType,
            flags=Instrument.FLAG_GET)

        self.add_parameter('use_extref', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET)
        self.add_parameter('pulse_on', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET)

        if kwargs.pop('reset', False):
            self.reset()
        else:
            self.get_all()
        self.set(kwargs)
        
        '''
   
    '''
    def do_get_rf_mode(self):
        device_status = device_status_t()
        lb_dll.sc5506a_get_device_status(self._handle, device_status)
        if(device_status.operate_status_t.rf1_mode == 0):
            return 'fixed'
        else:
            return 'sweep'

    def do_set_rf_mode(self, mode):
        if(mode == 'sweep'):
            lb_dll.sc5506a_set_rf_mode(self._handle, 1)
        else:
            lb_dll.sc5506a_set_rf_mode(self._handle, 0)

    '''

#    def do_get_handle(self):
#        return self._handle.contents.value

#    def do_get_serial(self):
#        return self._serialno

    def do_get_ch1_frequency(self):
        deviceParams = deviceParams_t()        
        lb_dll.sc5506a_GetDeviceParams(self._handle, deviceParams)
        return float(deviceParams.ch1Frequency)
    
    def do_get_ch2_frequency(self):
        deviceParams = deviceParams_t()        
        lb_dll.sc5506a_GetDeviceParams(self._handle, deviceParams)
        return float(deviceParams.ch2Frequency)

    def do_set_ch1_frequency(self, freq_Hz):
        return lb_dll.sc5506a_SetFrequency(self._handle, ctypes.c_ubyte(0), ctypes.c_ulonglong(int(freq_Hz)))
    
    def do_set_ch2_frequency(self, freq_Hz):
        return lb_dll.sc5506a_SetFrequency(self._handle, ctypes.c_ubyte(1), ctypes.c_ulonglong(int(freq_Hz)))

    def do_get_ch1_power(self):
        deviceParams = deviceParams_t()        
        lb_dll.sc5506a_GetDeviceParams(self._handle, deviceParams)
        return deviceParams.ch1PowerLevel
    
    def do_get_ch2_power(self):
        deviceParams = deviceParams_t()        
        lb_dll.sc5506a_GetDeviceParams(self._handle, deviceParams)
        return deviceParams.ch2PowerLevel

    def do_set_ch1_power(self, power):
        return lb_dll.sc5506a_SetPowerLevel(self._handle, ctypes.c_ubyte(0), ctypes.c_float(power))
    
    def do_set_ch2_power(self, power):
        return lb_dll.sc5506a_SetPowerLevel(self._handle, ctypes.c_ubyte(1), ctypes.c_float(power))

    def do_get_ch1_output(self):
        deviceStatus = deviceStatus_t()
        lb_dll.sc5506a_GetDeviceStatus(self._handle, deviceStatus)
        return deviceStatus.ch1RfOutEnable
    
    def do_get_ch2_output(self):
        deviceStatus = deviceStatus_t()
        lb_dll.sc5506a_GetDeviceStatus(self._handle, deviceStatus)
        return deviceStatus.ch2RfOutEnable

    def do_set_ch1_output(self, val):
        if(val):
            return lb_dll.sc5506a_SetRfOutput(self._handle, ctypes.c_ubyte(0), 1)
        else:
            return lb_dll.sc5506a_SetRfOutput(self._handle, ctypes.c_ubyte(0), 0)
        
    def do_set_ch2_output(self, val):
        if(val):
            return lb_dll.sc5506a_SetRfOutput(self._handle, ctypes.c_ubyte(1), 1)
        else:
            return lb_dll.sc5506a_SetRfOutput(self._handle, ctypes.c_ubyte(1), 0)
            

    def do_get_ext_locked(self):
        return True
    
    
    
    '''
    def do_get_model(self):
        return self._modelname

    def _init(self):
        f = get_lb_func('fnLMS_InitDevice')
        return f(self._devid)

    def _close(self):
        f = get_lb_func('fnLMS_CloseDevice')
        return f(self._devid)

    def _get_max_freq(self):
        return self._max_freq

    def _get_min_freq(self):
        return self._min_freq

    def _get_status(self):
        f = get_lb_func('fnLMS_GetDeviceStatus')
        return f(self._devid)

    def _get_max_power(self):
        f = get_lb_func('fnLMS_GetMaxPwr')
        return f(self._devid) * 0.25

    def _get_min_power(self):
        f = get_lb_func('fnLMS_GetMinPwr')
        return f(self._devid) * 0.25

    def convert_to_units(self, power):
        return int(round(power * 4))

    def convert_to_dBm(self, val):
        return self._max_power - 0.25 * val

   



    def do_get_fast_pulse_option(self):
        return bool(self._get_status() & STATUS_FAST_PULSE_OPT)

    def do_get_use_extref(self):
        f = get_lb_func('fnLMS_GetUseInternalRef')
        return f(self._devid) == 0

    def do_set_use_extref(self, val):
        f = get_lb_func('fnLMS_SetUseInternalRef', [ctypes.c_uint32, ctypes.c_bool])
        return f(self._devid, not val)

    def do_get_pulse_on(self):
        f = get_lb_func('fnLMS_GetUseInternalPulseMod')
        return not f(self._devid)

    def do_set_pulse_on(self, val):
        f = get_lb_func('fnLMS_SetUseExternalPulseMod', [ctypes.c_uint32, ctypes.c_bool])
        return f(self._devid, val)
    '''



#if __name__ == '__main__':
#    logging.getLogger().setLevel(logging.DEBUG)
#    lb = Instrument.test(LabBrick_RFSourceDLL)
