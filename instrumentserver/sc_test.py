# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 13:14:53 2017

@author: WangLab
"""


import ctypes
import time

class device_rf_params_t(ctypes.Structure):
    _fields_ =  [('rf1_freq', ctypes.c_ulonglong),
                     ('start_freq', ctypes.c_ulonglong),
                     ('stop_freq', ctypes.c_ulonglong),
                     ('step_freq', ctypes.c_ulonglong),
                     ('sweep_dwell_time', ctypes.c_uint),
                     ('sweep_cycles', ctypes.c_uint),
                     ('buffer_points', ctypes.c_uint),
                     ('rf_level', ctypes.c_float),
                     ('rf2_freq', ctypes.c_ushort)]
    
    def print_params(self):
        print(('\ndevice rf params:\n'
              + 'rf1_freq = ' + str(self.rf1_freq) + '\n'
              + 'start_freq = ' + str(self.start_freq) + '\n'
              + 'stop_freq = ' + str(self.stop_freq) + '\n'
              + 'step_freq = ' + str(self.step_freq) + '\n'
              + 'sweep_dwell_time = ' + str(self.sweep_dwell_time) + '\n'
              + 'sweep_cycles = ' + str(self.sweep_cycles) + '\n'
              + 'buffer_points = ' + str(self.buffer_points) + '\n'
              + 'rf_level = ' + str(self.rf_level) + '\n'
              + 'rf2_freq = ' + str(self.rf2_freq)))
    
    
    
class list_mode_t(ctypes.Structure):
    _fields_ =  [('sss_mode', ctypes.c_ubyte),
                     ('sweep_dir', ctypes.c_ubyte),
                     ('tri_waveform', ctypes.c_ubyte),
                     ('hw_trigger', ctypes.c_ubyte),
                     ('step_on_hw_trig', ctypes.c_ubyte),
                     ('return_to_start', ctypes.c_ubyte),
                     ('trig_out_enable', ctypes.c_ubyte),
                     ('trig_out_on_cycle', ctypes.c_ubyte)]
    
    def print_params(self):
        print(('\nlist mode params:\n'
              + 'sss_mode = ' + str(self.sss_mode) + '\n'
              + 'sweep_dir = ' + str(self.sweep_dir) + '\n'
              + 'tri_waveform = ' + str(self.tri_waveform) + '\n'
              + 'hw_trigger = ' + str(self.hw_trigger) + '\n'
              + 'step_on_hw_trig = ' + str(self.step_on_hw_trig) + '\n'
              + 'return_to_start = ' + str(self.return_to_start) + '\n'
              + 'trig_out_enable = ' + str(self.trig_out_enable) + '\n'
              + 'trig_out_on_cycle = ' + str(self.trig_out_on_cycle)))
        
class pll_status_t(ctypes.Structure):
    _fields_ =  [('sum_pll_ld', ctypes.c_ubyte),
                     ('crs_pll_ld', ctypes.c_ubyte),
                     ('fine_pll_ld', ctypes.c_ubyte),
                     ('crs_ref_pll_ld', ctypes.c_ubyte),
                     ('crs_aux_pll_ld', ctypes.c_ubyte),
                     ('ref_100_pll_ld', ctypes.c_ubyte),
                     ('ref_10_pll_ld', ctypes.c_ubyte),
                     ('rf2_pll_ld', ctypes.c_ubyte)]
    
    def print_params(self):
        print(('\npll status params:\n'
              + 'sum_pll_ld = ' + str(self.sum_pll_ld) + '\n'
              + 'crs_pll_ld = ' + str(self.crs_pll_ld) + '\n'
              + 'fine_pll_ld = ' + str(self.fine_pll_ld) + '\n'
              + 'crs_ref_pll_ld = ' + str(self.crs_ref_pll_ld) + '\n'
              + 'crs_aux_pll_ld = ' + str(self.crs_aux_pll_ld) + '\n'
              + 'ref_100_pll_ld = ' + str(self.ref_100_pll_ld) + '\n'
              + 'ref_10_pll_ld = ' + str(self.ref_10_pll_ld) + '\n'
              + 'rf2_pll_ld = ' + str(self.rf2_pll_ld)))


class operate_status_t(ctypes.Structure):
    _fields_ =  [('rf1_lock_mode', ctypes.c_ubyte),
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
                     ('harmonic_ss', ctypes.c_ubyte)]
    
    def print_params(self):
        print(('\noperate mode status: \n'
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
              + 'harmonic_ss = ' + str(self.harmonic_ss)))


class device_status_t(ctypes.Structure):
    _fields_ =  [('list_mode_t', list_mode_t),
                     ('operate_status_t', operate_status_t),
                     ('pll_status_t', pll_status_t)]
    
    def print_params(self):
        self.list_mode_t.print_params()
        self.operate_status_t.print_params()
        self.pll_status_t.print_params()



LB_DLL = 'C:\\qrlab\\instrumentserver\\SignalCore\\x64\\sc5511a.dll'
lb_dll = ctypes.windll.LoadLibrary(LB_DLL)

NUM_MAX_DEVICES = 5
ID_BUFFER_SIZE = 8

string_buffers = [ctypes.create_string_buffer(ID_BUFFER_SIZE) for i in range(NUM_MAX_DEVICES)]
pointers = (ctypes.c_char_p*NUM_MAX_DEVICES)(*list(map(ctypes.addressof, string_buffers)))
print((lb_dll.sc5511a_search_devices(pointers)))
results = [s.value for s in string_buffers]
print(results)
handle = lb_dll.sc5511a_open_device(results[0])
print(handle)


lb_dll.sc5511a_set_rf_mode(handle, 0)
lb_dll.sc5511a_set_output(handle, 1)
'''
lb_dll.sc5511a_list_cycle_count(handle, ctypes.c_uint(0))

lb_dll.sc5511a_list_start_freq(handle, ctypes.c_ulonglong(12000000000))

#try:
lb_dll.sc5511a_set_freq(handle, ctypes.c_ulonglong(12010000000))
#lb_dll.sc5511a_set_freq(handle, ctypes.c_ulonglong(12010000000))
'''


device_rf_params = device_rf_params_t()
device_status = device_status_t()

lb_dll.sc5511a_get_rf_parameters(handle, device_rf_params)
lb_dll.sc5511a_get_device_status(handle, device_status)

device_rf_params.print_params()
device_status.print_params()


#lb_dll.sc5511a_get_rf_parameters(handle, device_rf_params)
#device_rf_params.print_params()


    
    
    #lb_dll.sc5511a_set_freq(handle, ctypes.cast(12000000, ctypes.POINTER(ctypes.c_ulonglong)))
    #time.sleep(10)
#except:
#    print('shit dont work')
    
    
lb_dll.sc5511a_close_device(handle)
