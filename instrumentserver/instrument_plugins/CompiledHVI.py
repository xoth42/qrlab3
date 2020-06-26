# -*- coding: utf-8 -*-
import keysightSD1 as key
def error_decorator(function):
    def wrapper(*args):
        result = function(*args)
        if (result < 0) and (result != -8038) and (result != -8031):
            raise ValueError("Error is " + str(result) + ' in function: ' + str(function.func_name))
    return wrapper
        
class CompiledHVI(object):
    def __init__(self, HVI_path_str, awg_list, *args, **kwargs):
        self.hvi = key.SD_HVI()
        self.identifier = self.hvi.open(HVI_path_str)
        self.error(self.identifier)
        for i in range(len(awg_list)):
            self.assignHardware(i, 0, awg_list[i]) #DARIO 1/31 dynamic slot assignment
#        self.assignHardware(1, 0, 10) #DARIO 1/17/19 changed for different slot arrangement on the third
#                                                                   (digitizer-less) chassis
#        self.assignHardware(2, 0, 10)
            
#        self.assignHardware(0, 0, 7)
#        self.assignHardware(1, 0, 8)
        

        self.hvi.compile()
        self.hvi.load()
        
    def error(self, value):
        if (value < 0) and (value != -8038) and (value != -8031):
            raise ValueError('HVI error ' + str(value))
    @error_decorator       
    def start(self):
        result = self.hvi.start()
        return result
    @error_decorator    
    def pause(self):
        result = self.hvi.pause()
        return result
    @error_decorator    
    def resume(self):
        result = self.hvi.resume()
        return result
    @error_decorator
    def assignHardware(self, Index, chassisnumber, slotnumber):
        result = self.hvi.assignHardwareWithIndexAndSlot(Index, chassisnumber, slotnumber)
        return result
    @error_decorator
    def stop(self):
        result = self.hvi.stop()
        return result
    @error_decorator
    def compile(self):
        result = self.hvi.compile()
        return result
    @error_decorator
    def load(self):
        result = self.hvi.load()
        return result
