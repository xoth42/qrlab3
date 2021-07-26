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
from .instrument import Instrument
import logging

SUCCESS = 0
NO_DEVICE = 0

#LB_DLL = r'c:\qrlab-3\instrumentserver\vnx_fmsynth.dll'
LB_DLL = 'C:\\qrlab-3\\instrumentserver\\SignalCore\\x64\\sc5413a.dll'
try:
    lb_dll = ctypes.windll.LoadLibrary(LB_DLL)
    #lb_dll = ctypes.cdll.LoadLibrary(LB_DLL)
    
except Exception as e:
    s = 'Unable to load SignalCore DLL, please put sc5413a.dll in instrumentserver directory ' + str(e)
    raise ValueError(s)
    
class deviceInfo_t(ctypes.Structure):
    _fields_ = [('productSerialNumber', ctypes.c_uint),
                ('rfModuleSerialNumber', ctypes.c_uint),
                ('firmwareRevision', ctypes.c_float),
                ('hardwareRevision', ctypes.c_float),
                ('calDate', ctypes.c_uint),
                ('manDate', ctypes.c_uint)]
    
    def print_params(self):
        print(('\ndevice info params:\n'
              + 'productSerialNumber = ' + str(self.productSerialNumber) + '\n'
              + 'rfModuleSerialNumber = ' + str(self.rfModuleSerialNumber) + '\n'
              + 'firmwareRevision = ' + str(self.firmwareRevision) + '\n'
              + 'hardwareRevision = ' + str(self.hardwareRevision) + '\n'
              + 'calDate = ' + str(self.calDate) + '\n'
              + 'manDate = ' + str(self.manDate)))
              
        
class deviceStatus_t(ctypes.Structure):
    _fields_ =  [('rfAmpEnable', ctypes.c_ubyte),
                     ('rfPath', ctypes.c_ubyte),
                     ('loEnable', ctypes.c_ubyte),
                     ('deviceAccess', ctypes.c_ubyte)]
    
    def print_params(self):
        print(('\ndevice status params:\n'
              + 'rfAmpEnable = ' + str(self.rfAmpEnable) + '\n'
              + 'rfPath = ' + str(self.rfPath) + '\n'
              + 'loEnable = ' + str(self.loEnable) + '\n'
              + 'deviceAccess = ' + str(self.deviceAccess)))        

NUM_MAX_DEVICES = 5
ID_BUFFER_SIZE = 8



class SC5413A(Instrument):

    def __init__(self, name, devid=None, serial=None):
        super(SC5413A, self).__init__(name)

        if devid is None:
            raise Exception('SignalCore driver needs devid or serial as parameter')


        
        # This is the code Josh wrote
        string_buffers = [ctypes.create_string_buffer(ID_BUFFER_SIZE) for i in range(NUM_MAX_DEVICES)]
        pointers = (ctypes.c_char_p*NUM_MAX_DEVICES)(*list(map(ctypes.addressof, string_buffers)))
        results = [s.value for s in string_buffers]
        self.dev_num = ctypes.c_char_p(devid)
        lb_dll.sc5413a_OpenDevice.restype = ctypes.POINTER(ctypes.c_int)
        self._handle = lb_dll.sc5413a_OpenDevice(self.dev_num)

        deviceStatus = deviceStatus_t()

        deviceStatus_temp = ctypes.pointer(deviceStatus)
#        lb_dll.sc5413a_get_device_status.argtypes = [ctypes.POINTER(ctypes.c_int),
#                                                    ctypes.POINTER(device_status_t)]
        lb_dll.sc5413a_GetDeviceStatus(self._handle, deviceStatus_temp.contents)
        
#        lb_dll.sc5413a_InitDevice(self._handle, deviceStatus_temp.contents) #DARIO to-do 

        
        
        '''
        # This is the code Jeff wrote, this is probably still wrong
        string_buffers = [ctypes.create_string_buffer(ID_BUFFER_SIZE) for i in range(NUM_MAX_DEVICES)]
        pointers = (ctypes.c_char_p*NUM_MAX_DEVICES)(*map(ctypes.addressof, string_buffers))
        print "THING", lb_dll.sc5413a_search_devices(pointers)
        results = [s.value for s in string_buffers]
        self._handle = lb_dll.sc5413a_open_device(results[0])
        
        device_rf_params = device_rf_params_t()
        device_status = device_status_t()
        print "HANDLE", self._handle
        print "STATS", device_status
        lb_dll.sc5413a_get_device_status(self._handle, device_status)
        lb_dll.sc5413a_get_rf_parameters(self._handle, device_rf_params)
        '''

#        lb_dll.sc5413a_set_rf_mode(self._handle, 0)
#        lb_dll.sc5413a_set_output(self._handle, 1)
        
#        self._serialno = results[0]
        self._min_freq = 25000000    
        self._max_freq = 6000000000
        self._min_power = -50
        self._max_power = 10

        
    
#        self.add_parameter('serial', type=types.StringType,
#            flags=Instrument.FLAG_GET, value=self._serialno)
#        self.add_parameter('handle', type=types.IntType,
#            flags=Instrument.FLAG_GET, value=self._handle)
        self.add_parameter('frequency', type=float,
            flags=Instrument.FLAG_SET, units='Hz',
            minval=self._min_freq, maxval=self._max_freq,
            display_scale=6, value = deviceParams.ch1Frequency)
        self.add_parameter('gain', type=float,
            flags=Instrument.FLAG_SET, units='dBm',
            minval=self._min_gain, maxval=self._max_gain,
            display_scale=6, value = deviceParams.ch2Frequency)
        self.add_parameter('amplifier', type=bool,
            flags=Instrument.FLAG_SET, value = True)
        self.add_parameter('path', type=bool,
            flags=Instrument.FLAG_SET, value = True)
        self.add_parameter('lo_output', type=bool,
            flags=Instrument.FLAG_SET, value = True)

        
        
        
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
        lb_dll.sc5413a_get_device_status(self._handle, device_status)
        if(device_status.operate_status_t.rf1_mode == 0):
            return 'fixed'
        else:
            return 'sweep'

    def do_set_rf_mode(self, mode):
        if(mode == 'sweep'):
            lb_dll.sc5413a_set_rf_mode(self._handle, 1)
        else:
            lb_dll.sc5413a_set_rf_mode(self._handle, 0)

    '''

#    def do_get_handle(self):
#        return self._handle.contents.value

#    def do_get_serial(self):
#        return self._serialno

#    def do_get_ch1_frequency(self):
#        deviceParams = deviceParams_t()        
#        lb_dll.sc5413a_GetDeviceParams(self._handle, deviceParams)
#        return float(deviceParams.ch1Frequency)
#    
#    def do_get_ch2_frequency(self):
#        deviceParams = deviceParams_t()        
#        lb_dll.sc5413a_GetDeviceParams(self._handle, deviceParams)
#        return float(deviceParams.ch2Frequency)

    def do_set_frequency(self, freq_Hz):
        return lb_dll.sc5413a_SetFrequency(self._handle, ctypes.c_ulonglong(int(freq_Hz)))

#    def do_get_ch1_power(self):
#        deviceParams = deviceParams_t()        
#        lb_dll.sc5413a_GetDeviceParams(self._handle, deviceParams)
#        return deviceParams.ch1PowerLevel
#    
#    def do_get_ch2_power(self):
#        deviceParams = deviceParams_t()        
#        lb_dll.sc5413a_GetDeviceParams(self._handle, deviceParams)
#        return deviceParams.ch2PowerLevel

    def do_set_gain(self, gain):
        return lb_dll.sc5413a_SetRfGain(self._handle, ctypes.c_float(gain))
    
    def do_set_amplifier(self, val):
        if(val):
            return lb_dll.sc5413a_SetRfAmplifier(self._handle, 1)
        else:
            return lb_dll.sc5413a_SetRfAmplifier(self._handle, 0)

    def do_set_path(self, val):
        if(val):
            return lb_dll.sc5413a_SetRfPath(self._handle, 1)
        else:
            return lb_dll.sc5413a_SetRfPath(self._handle, 0)

    def do_set_lo_output(self, val):
        if(val):
            return lb_dll.sc5413a_SetLoOut(self._handle, 1)
        else:
            return lb_dll.sc5413a_SetLoOut(self._handle, 0)
        
    
    
    
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
