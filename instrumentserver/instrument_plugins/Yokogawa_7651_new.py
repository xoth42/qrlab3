import pyvisa
import numpy as np
from instrumentserver.instrument import Instrument
import re

# TODO: review


currSource = 'none'

# Some exceptions to make errors nicer.
class StateWrongValueError(Exception):
    pass


class VoltageError(Exception):
    pass


class CurrentError(Exception):
    pass


class PolarityError(Exception):
    pass


class VISACommand(object):
    """
    A class to make the handling of the VISA commands easier.
    """

    def __init__(self, command, instrument, *args, **kwargs):
        self.command = command
        self.ins = instrument
        self.term_chars = '\r\n'

    def send(self, arguments=''):
        '''
        Send a piece of information to the device. Includes a trigger to make
        sure the value actually sticks.
        :param arguments: Any info that actually needs to be sent to the
        device, like a voltage or current.
        :return: None
        Functions based on the send definition act through "Listener Functions"
        in the Yoko 7651 manual
        '''
        self.ins.write(self.command + str(arguments) + ';')
        self.ins.write('E;')

    def recieve(self):
        '''
        This needs to work such that "Talker Functions" in the Yoko 7651 manual
        communicate through the recieve function.
        Get a piece of info from the device.
        :return: A list of the results.
        '''
        
        # 3/25/19 Alex, Yingying, Brendan
        # rewrite receive to return single string
        
        try:
            query_string = self.command
            result = self.ins.query(query_string)

        except pyvisa.errors.VisaIOError:
            raise IOError('There was problem communicating with the yoko.')

        return result


class Yokogawa_7651_new(Instrument):
    def __init__(self, name, address, *args, **kwargs):
        super(Yokogawa_7651_new, self).__init__(name, address=address,
                                            term_chars='\r\n', **kwargs)
        # Determines whether the unit should be milliamps or amps.
        # Open the device
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(address)
        self.instrument.timeout = 10000

        # Define all of the necesary commands that we'll need to interact with
        #  the device.
        self.OS = VISACommand('OS', self.instrument) #OS is "Set Information Output"
        self.voltage_function = VISACommand('F1', self.instrument) #F1 is Function setting for voltage
        self.auto_range_value = VISACommand('SA', self.instrument) #SA is for auto ranging mode (?)
        self.range_value = VISACommand('S', self.instrument)
        self.output = VISACommand('OD', self.instrument) #OD "Output Value Data Output"
        self.current_function = VISACommand('F5', self.instrument) #F5 is Function setting for current
        self.polarity = VISACommand('SG', self.instrument) #SG is for specifying or altering polarity
        self.output_state = VISACommand('O', self.instrument) #O is On/Off, i.e. O1 or O2
        self.voltage_limit = VISACommand('LV', self.instrument) #LV is Voltage Limit Setting
        self.current_limit = VISACommand('LA', self.instrument) #LA is Current Limit Setting
        self.status = VISACommand('OC', self.instrument) #OC is "Status Code Output" 8 bit number to tell behavior of Yoko
#        self.voltage_limit = VISACommand('LV', self.instrument) Repeated

        self.add_parameter('output_state', type=int,
                           flags=Instrument.FLAG_GETSET,
                          )
        self.add_parameter('source_type', type=bytes,
                           flags=Instrument.FLAG_GETSET)
        self.add_parameter('voltage_range', type=float,
                            flags=Instrument.FLAG_GETSET, units='V',
                            )
        self.add_parameter('current_range', type=float,
                            flags=Instrument.FLAG_GETSET, units='V',
                            )
        # self.add_parameter('voltage_range', type=types.IntType,
        #                    flags=Instrument.FLAG_GETSET, units='V',
        #                    format_map={2: '10 mV',
        #                                3: '100 mV',
        #                                4: '1 V',
        #                                5: '10 V',
        #                                6: '30 V'})
        # self.add_parameter('current_range', type=types.IntType,
        #                    flags=Instrument.FLAG_GETSET, units='mA',
        #                    format_map={4: '1 mA',
        #                                5: '10 mA',
        #                                6: '100 mA'})
        # self.add_parameter('current_limit', type=types.IntType,
        #                    flags=Instrument.FLAG_GETSET, units='mA',
        #                    minvalue=5, maxvalue=120)
        # self.add_parameter('voltage_limit', type=types.IntType,
        #                    flags=Instrument.FLAG_GETSET, units='V',
        #                    minvalue=1, maxvalue=30)
        self.add_parameter('current', type=float,
                           flags=Instrument.FLAG_GETSET, maxval=120,
                           minval=-120, units='mA')
        self.add_parameter('ramp_current', type=float,
                           flags=Instrument.FLAG_GETSET, maxval=120,
                           minval=-120, units='mA')
        self.add_parameter('voltage', type=float,
                   flags=Instrument.FLAG_GETSET, units='V',
                   minvalue=-30.0, maxvalue=30.0)
        self.add_parameter('ramp_voltage', type=float,
                   flags=Instrument.FLAG_GETSET, units='V',
                   minvalue=-30.0, maxvalue=30.0)
#        self.add_parameter('polarity', type=types.IntType,
#                           flags=Instrument.FLAG_GETSET,
#                           format_map={0: 'positive',
#                                       1: 'negative',
#                                       2: 'invert'})
#        self.add_parameter('output_data_value', type=types.StringType,
#                           flags=Instrument.FLAG_GET)

    def do_get_output(self):
        return self.output.recieve()

    def do_set_output_state(self, state):
        if state not in [0, 1]:
            raise StateWrongValueError("Output state can be 0 or 1, nothing else.")
        self.output_state.send(state)
#        self.output = state

    def do_get_output_state(self):
        print('yes')
        state = self.status.recieve()
        digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", state)
        digit = float(digit[-1])
        state = bin(int(digit))
        if len(state) < 5:
            return 0
        else:       
            return int(state[-5])
        
# Useful Functions --------------------------------------------

    def do_set_source_type(self, source):
        if source == 'voltage':
            self.voltage_function.send()
        elif source == 'current':
            self.current_function.send()
        else:
            raise ValueError('source_type is invalid')

    def do_get_source_type(self):
        print('getting source type')
        strng = self.do_get_output()
        print(strng)
        char = strng[3]
        if (char == 'V'):
            return 'voltage'
        if (char == 'A'):
            return 'current'
            
    def do_try(self):
        print('yes')
        return 2
                    
# Voltage Functions:  
    
    def do_get_voltage(self):
        if (self.do_get_source_type() != 'voltage'):
#            raise VoltageError('Not in voltage mode')
            return None
        strng = self.do_get_output()
        digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", strng)
        digit = float(digit[0])
        return digit
        
    def do_set_voltage(self, voltage): # WARNING: Jumps right to voltage you set, as long as in voltage mode (-Alex S. 5/1/19)
        # 3/25/19 Alex S:
            
        if (abs(voltage) > 30):
            raise VoltageError('Voltage out of range.')
#       The if statement below is necessary to ensure Yoko can switch between
#       current and voltage. BS & AS, 2/13/19.
#        if (self.do_get_source_type() != 'voltage'):
#            self.do_set_source_type('voltage')
#        self.voltage_function.send()
        if np.abs(voltage) > np.abs(self.get_voltage_range()):
            raise VoltageError('%0.6f is out of voltage limit!')
        self.range_value.send(voltage)
        
    def do_ramp_voltage(self,vtarget):
#        if (self.do_get_source_type() != 'voltage'):
#            raise VoltageError('Not in voltage mode')
#            return               
        v = self.do_get_voltage()
        vstep = .01
#        bigger = np.max((abs(v),abs(vtarget)))
#        self.do_set_voltage_range(bigger)
        max_steps = int(np.ceil(abs(vtarget - v) / vstep))
        if (v < vtarget):   
            for _ in range(max_steps):
                if not (v+vstep <= vtarget):
                    break
                self.range_value.send(v+vstep)
                v = self.do_get_voltage()
        if (v > vtarget):
            for _ in range(max_steps):
                if not (v-vstep >= vtarget):
                    break
                self.range_value.send(v-vstep)
                v = self.do_get_voltage()
        self.do_set_voltage(vtarget)
                
    def do_set_ramp_voltage(self,v_target):
        self.do_ramp_voltage(v_target)
    
    def do_get_ramp_voltage(self):
        self.do_get_voltage()

    def do_set_voltage_range(self,R):
        R = abs(R)
#        if (self.do_get_source_type() != 'voltage'):
#            raise VoltageError('Not in voltage mode')
#            return
        if ( R <= .01):
            VISACommand('R2', self.instrument).send()
        elif (R <= .1):
            VISACommand('R3', self.instrument).send()
        elif (R <= 1):
            VISACommand('R4', self.instrument).send()
        elif (R <= 10):
            VISACommand('R5', self.instrument).send()
        elif (R <= 30):
            VISACommand('R6', self.instrument).send()
        else:
            raise VoltageError('Range not supported!!!')

    def do_get_voltage_range(self):
#        if (self.do_get_source_type() != 'voltage'):
##            raise VoltageError('Not in voltage mode')
#            return None
        strng = self.do_get_output()
        
        if ( strng[7] == '.' and strng[13] == '-' and strng[14] == '3'):
            return 0.01
        if ( strng[8] == '.' and strng[13] == '-' and strng[14] == '3'):
            return 0.1
        if ( strng[6] == '.' and strng[13] == '+' and strng[14] == '0'):
            return 1
        if ( strng[7] == '.' and strng[13] == '+' and strng[14] == '0'):
            return 10     
        if ( strng[8] == '.' and strng[13] == '+' and strng[14] == '0'):
            return 30
        else:
            raise VoltageError('Range not found!!!')   
      
# Current Functions:
# IMPORTANT NOTE:
    # All current values are in units of mA!!! (-Alex S. 5/1/19)
    def do_set_current(self, current):
        if (abs(current) > 120):
            raise CurrentError('Current out of range.')
#       The if statement below is necessary to ensure Yoko can switch between
#       current and voltage. BS & AS, 2/13/19.
#        if (self.do_get_source_type() != 'current'):
#            self.do_set_source_type('current')
#        self.current_function.send()
        if np.abs(current) > np.abs(self.get_current_range()):
            raise CurrentError('%0.6f is out of current limit!')
        self.range_value.send(current / 1000)

    def do_get_current(self):
        if (self.do_get_source_type() != 'current'):
#            raise CurrentError('Not in current mode')
            return None
        strng = self.do_get_output()
        digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", strng)
        digit = float(digit[0]) * 1000
        return digit

    def do_ramp_current(self,i_target):
#        if (self.do_get_source_type() != 'current'):
#            raise CurrentError('Not in current mode')
#            return               
        i = self.do_get_current()
        i_step = self.get_current_range()*0.0005 / 1000
#        bigger = np.max((abs(i),abs(i_target)))
#        self.do_set_current_range(bigger)
        max_steps = int(np.ceil(abs(i_target / 1000 - i / 1000) / i_step))
        if (i/1000 < i_target /1000 ):   
            for _ in range(max_steps):
                if not (i/1000+i_step <= i_target / 1000):
                    break
                self.range_value.send(i/1000+i_step)
                i = self.do_get_current()
        if (i /1000> i_target / 1000):
            for _ in range(max_steps):
                if not (i/1000-i_step >= i_target / 1000):
                    break
                self.range_value.send(i/1000-i_step)
                i = self.do_get_current()                
        self.range_value.send(i_target/1000)

    def do_set_current_range(self,R):
        R = abs(R)
#        if (self.do_get_source_type() != 'current'):
#            raise CurrentError('Not in current mode')
#            return
        if ( R <= 1):
            VISACommand('R4', self.instrument).send()
        elif (R <= 10):
            VISACommand('R5', self.instrument).send()
        elif (R <= 120):
            VISACommand('R6', self.instrument).send()
        else:
            raise VoltageError('Range not supported!!!')
       
    def do_get_current_range(self):
        if (self.do_get_source_type() != 'current'):
#            raise CurrentError('Not in current mode')
            return None
        strng = self.do_get_output()
        
        if ( strng[6] == '.'):
            return 1
        if ( strng[7] == '.'):
            return 10        
        if ( strng[8] == '.'):
            return 100
        else:
            raise currentError('Range not found!!!')  
            
            
    def do_set_ramp_current(self,i_target):
        self.do_ramp_current(i_target)
    
    def do_get_ramp_current(self):
        self.do_get_current()
        
    

    def do_set_polarity(self, polarity):
        if polarity not in list(range(0, 3)):
            raise PolarityError('Polarity not 0, 1, or 2')
        self.polarity.send(polarity)

    def do_get_polarity(self):
        return None

    def do_set_voltage_limit(self, limit):
#        self.current_function.send()
        self.voltage_limit.send(limit)

    def do_get_voltage_limit(self):
        return None

    def do_get_output_data_value(self):
        return None

    def do_set_current_limit(self, limit):
        self.current_limit.send(limit)

    def do_get_current_limit(self):
        return None


if __name__ == '__main__':
    test = Yokogawa_7651_new('test', address='GPIB0::6::INSTR') #why is this ::3 and not ::6? Uh oh.
    test.do_get_polarity()
