# Josh started this driver on 8/1/18 since the old driver didn't work at all
# really.

#3/26/2019 -- Dario 
#Yoko driver is currently in process of being improved by Brendan, Yingying et. al.
#Something was not compatible with the gui, so this is a slightly deprecated version



import pyvisa
from instrumentserver.instrument import Instrument


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
        '''
        self.ins.write(self.command + str(arguments) + ';')
        self.ins.write('E;')

    def recieve(self):
        '''
        Get a piece of info from the device.
        :return: A list of the results.
        '''
        result_list = [None]
        try:
            for _ in range(1000):
                query_string = self.command + '?;'
                self.ins.write(query_string)
                result = self.ins.read_raw()
                if result == result_list[-1]:
                    break
                if (result != 'END' + self.term_chars) and (result != ''):
                    result_list.append(result)
                else:
                    break
            else:
                raise IOError('Yokogawa reply exceeded 1000 records')
        except pyvisa.errors.VisaIOError:
            raise IOError('There was problem communicating with the yoko.')
        return result_list[1:]


class Yokogawa_7651_old(Instrument):
    def __init__(self, name, address, *args, **kwargs):
        super(Yokogawa_7651_old, self).__init__(name, address=address,
                                            term_chars='\r\n', **kwargs)
        # Determines whether the unit should be milliamps or amps.
        # Open the device
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(address)
        self.instrument.timeout = 10000

        # Define all of the necesary commands that we'll need to interact with
        #  the device.
        self.OS = VISACommand('OS', self.instrument)
        self.voltage_function = VISACommand('F1', self.instrument)
        self.auto_range_value = VISACommand('SA', self.instrument)
        self.output = VISACommand('OD', self.instrument)
        self.current_function = VISACommand('F5', self.instrument)
        self.polarity = VISACommand('SG', self.instrument)
        self.output_state = VISACommand('O', self.instrument)
        self.voltage_limit = VISACommand('LV', self.instrument)
        self.current_limit = VISACommand('LA', self.instrument)
        self.status = VISACommand('OC', self.instrument)
        self.voltage_limit = VISACommand('LV', self.instrument)

        self.add_parameter('output_state', type=int,
                           flags=Instrument.FLAG_GETSET,
                           format_map={1: 'on', 0: 'off'})
        self.add_parameter('source_type',
                           flags=Instrument.FLAG_GETSET)
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
        self.add_parameter('voltage', type=float,
                           flags=Instrument.FLAG_GETSET, units='V',
                           minvalue=-30.0, maxvalue=30.0)
        self.add_parameter('current', type=float,
                           flags=Instrument.FLAG_GETSET, maxval=120,
                           minval=-120, units='mA')
        self.add_parameter('polarity', type=int,
                           flags=Instrument.FLAG_GETSET,
                           format_map={0: 'positive',
                                       1: 'negative',
                                       2: 'invert'})
        self.add_parameter('output_data_value', type=bytes,
                           flags=Instrument.FLAG_GET)

    def do_get_output_state(self):
        return None

    def do_set_output_state(self, state):
        if state not in [0, 1]:
            raise StateWrongValueError("Output state can be 0 or 1, nothing "
                                       "else.")
        self.output_state.send(state)

    def do_set_source_type(self, source):
        if source == 'voltage':
            source = 1
        if source == 'current':
            source = 2
        if source not in [1, 2]:
            raise ValueError('source_type is invalid')
        if source == 1:
            self.voltage_function.send()
        if source == 2:
            self.current_function.send()

    def do_get_source_type(self):
        return None

    def do_set_voltage(self, voltage):
        if (abs(voltage) > 30):
            raise VoltageError("Voltage out of range")
        self.voltage_function.send()
        self.auto_range_value.send(voltage)

    def do_get_voltage(self):
        return None

    def do_set_current(self, current):
        if (abs(current) > 120):
            raise CurrentError('Current out of range.')

        self.current_function.send()
        self.auto_range_value.send(current / 1000)

    def do_get_current(self):
        return None

    def do_set_polarity(self, polarity):
        if polarity not in list(range(0, 3)):
            raise PolarityError('Polarity not 0, 1, or 2')
        self.polarity.send(polarity)

    def do_get_polarity(self):
        return None

    def do_set_voltage_limit(self, limit):
        self.current_function.send()
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
    test = Yokogawa_7651_old('test', address='GPIB0::3::INSTR')
    test.do_get_polarity()
