#==============================================================================
# Yokogawa GS200
# TODO: controller for 7651
#==============================================================================

import numpy as np
from instrumentserver.visainstrument import VisaInstrument
from instrumentserver.instrument import Instrument
import logging
class YokoException(Exception):
    pass
class Yokogawa_GS200(VisaInstrument):

    def __init__(self, name, address, **kwargs):
        super(Yokogawa_GS200, self).__init__(name, address=address, term_chars='\n', **kwargs)

        self.add_visa_parameter('output_state', ':OUTP?', ':OUTP %d',
            type=bool, flags=Instrument.FLAG_GETSET)
        self.add_visa_parameter('source_type', ':SOUR:FUNC?', ':SOUR:FUNC %s',
            type=bytes, flags=Instrument.FLAG_GETSET,
            option_list=('VOLT', 'CURR'))
        self.add_parameter('current_range', type=bytes,
                           flags=Instrument.FLAG_SET,
                           option_list=('MIN', 'MAX', 'UP', 'DOWN', '1E-3',
                                        '10E-3', '100E-3', '200E-3'),
                           )
#        self.add_parameter('voltage_range', type=types.StringType,
#                           flags=Instrument.FLAG_SET,
#                           option_list=('MIN', 'MAX', 'UP', 'DOWN', '1E-3',
#                                        '10E-3', '100E-3', '1E+0', '10E+0', '30E+0'),
#                           )
        self.add_parameter('source_range', type=bytes,
                           flags=Instrument.FLAG_GET)

        self.add_visa_parameter('slope', ':PROG:SLOP?', ':PROG:SLOP %s',
            type=float, flags=Instrument.FLAG_GETSET,
            minval=0, maxval=3600)
        self.add_visa_parameter('repeat', ':PROG:REP?', ':PROG:REP %s',
            type=int, flags=Instrument.FLAG_GETSET)
        self.add_visa_parameter('voltage_limit', 'SOUR:PROT:VOLT?', 'SOUR:PROT:VOLT %s',
            type=float, flags=Instrument.FLAG_GETSET,
            units='V')
        self.add_visa_parameter('current_limit', 'SOUR:PROT:CURR?', 'SOUR:PROT:CURR %s',
            type=float, flags=Instrument.FLAG_GETSET,
            units='A', minval=-10e-3, maxval=10e-3)
        self.add_parameter('voltage', type=float,
                           flags=Instrument.FLAG_GETSET,
                           units='V')
        self.add_parameter('current', type=float,
                           flags=Instrument.FLAG_GETSET,
                           units='A')
        self.add_parameter('source_level', type=float,
                           flags=Instrument.FLAG_GET)

        #self.get_all()

    def do_set_voltage(self, level, range='AUTO'):
        self.set_source_type('VOLT')
        self.set_source_level(level, range)

    def do_get_voltage(self):
        if self.get_source_type()=='CURR':
            #The yoko raises these exceptions all of the time, and the new GUI doesn't 
            #like them. They're harmless anyway.
            raise YokoException('Source type is VOLTAGE, not CURRENT')
        return self.do_get_source_level()

    def do_set_current(self, level, range='AUTO'):
        print(level, self.get_current_limit())
        if np.abs(level) > np.abs(self.get_current_limit()):
            raise YokoException('%0.6f is out of current limit!')
        self.set_source_type('CURR')
        self.set_source_level(level, range)

    def do_get_current(self):
        if self.get_source_type()=='VOLT':
            raise YokoException('Source type is CURRENT, not VOLTAGE')
        return self.do_get_source_level()

    def set_interval(self, period):
        if period >= 0.0 and period <= 3600.0:
            self.write(f'PROG:INT {period}')

    def get_current_protection(self):
        return float(self.ask(':SOUR:PROT:CURR?'))

    def do_set_source_range(self, range):
        self.write(f':SOUR:RANG {range}\n')

    def do_get_source_range(self):
        return self.ask(':SOUR:RANG?')

    def do_get_source_level(self):
        return self.ask(':SOUR:LEV?')

    def do_set_current_range(self, range):
        self.set_source_type('CURR')
        self.set_source_range(range)

#    def set_voltage_range(self, range):
#        # don't change state if at limits
#        if self.get_source_range() == '1E-3' and range == 'DOWN':
#            return
#        if self.get_source_range() == '30E+0' and range == 'UP':
#            return
#
#        self.set_source_type('VOLT')
#        self.set_source_range(range)

    # range auto updates at val * 1.2 (i.e. 1.21 V is 10 V scale)
    # here for simplicity just change scales if value is above the
    # current scale
    def select_voltage_range(self, value):
        ranges = ['10E-3', '100E-3', '1E+0', '10E+0', '30E+0']

        value = np.abs(value)
        if value <= float(ranges[0]):
            range = ranges[0]
        elif value <= float(ranges[1]):
            range = ranges[1]
        elif value <= float(ranges[2]):
            range = ranges[2]
        elif value <= float(ranges[3]):
            range = ranges[3]
        elif value <= float(ranges[4]):
            range = ranges[4]
        #elif value <= float(ranges[5]):
            #range = ranges[5]

        else:
            # voltage is out of range
            print('voltage is out of range')
            range = -1
        return range

    def set_source_level(self, level, range):
        if range=='AUTO' or range=='FIX':
            self.write(f'SOUR:LEV:{range} {level}\n')

    def find_ramp_time(self, initial, final, slew):
        '''
            calculates the appropriate slope and interval for a
            chosen slew rate
        '''

        return np.abs(final - initial) / float(slew)

    # yoko does not like changing ranges in ramp
    # slew is in V/s
    def set_voltage_ramp(self, level, slew=5.0):
        if float(self.do_get_source_level()) == level:

            return

        self.set_output_state('ON')
        self.set_source_type('VOLT')
        self.set_repeat('OFF')

        # determine appropriate ramp time given slew rate
        initial = float(self.do_get_source_level())

        ramp_time = self.find_ramp_time(initial, level, slew)
        self.set_slope(ramp_time)
        self.set_interval(ramp_time)

        # set new range if required
        if np.abs(level) - np.abs(initial) > 0:
            self.set_voltage_range(self.select_voltage_range(level))
        self.set_voltage_range('30E+0')

        self.write(':PROG:EDIT:STAR')
        self.set_voltage(level, range='FIX')
        self.write(':PROG:EDIT:END')

        self.write(':PROG:RUN')

    def get_voltage_protection(self):
        return self.ask(':SOUR:PROT:VOLT?')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    ins = Instrument.test(Yokogawa_GS200)
