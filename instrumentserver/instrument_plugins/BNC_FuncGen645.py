import time
import types
import pyvisa
from visainstrument import VisaInstrument, Instrument

class BNC_FuncGen645(VisaInstrument):

    def __init__(self, name, address, **kwargs):
        super(BNC_FuncGen645, self).__init__(name, address=address, term_chars='\n', **kwargs)

        self.add_visa_parameter('output_on',
            'OUTP?', 'OUTP %s',
            type=bool,
            flags=Instrument.FLAG_GETSET)
        self.add_visa_parameter('function',
            'FUNC?', 'FUNC %s',
            type=bytes,
            flags=Instrument.FLAG_GETSET,
            format_map={
                'SIN': 'SIN',
                'SQU': 'SQUARE',
                'RAMP': 'RAMP',
                'PULS': 'PULSE',
                'NOIS': 'NOISE',
                'DC': 'DC',
                'USER': 'USER',
            })

        self.add_visa_parameter('frequency',
            'FREQ?', 'FREQ %.06f',
            type=float,
            flags=Instrument.FLAG_GETSET, units='Hz')

        self.add_parameter('amplitude', type=float,
            flags=Instrument.FLAG_GETSET, units='V')
        self.add_parameter('offset', type=float,
            flags=Instrument.FLAG_GETSET, units='V')

        self.add_parameter('Vlow', type=float,
            flags=Instrument.FLAG_GETSET, units='V')
        self.add_parameter('Vhigh', type=float,
            flags=Instrument.FLAG_GETSET, units='V')

        self.add_visa_parameter('sync_on',
            'OUTP:SYNC?', 'OUTP:SYNC %d',
            type=bool,
            flags=Instrument.FLAG_GETSET,
            help='Whether sync output is enabled')

        self.get_all()
        self.set(kwargs)

    def do_get_Vhigh(self):
        val = self.ask('VOLT:HIGH?\n')
        return float(val)

    def do_set_Vhigh(self, val):
        self.write(f'VOLT:HIGH {val:.6f}\n')
        self.get_amplitude()
        self.get_offset()

    def do_get_Vlow(self):
        val = self.ask('VOLT:LOW?\n')
        return float(val)

    def do_set_Vlow(self, val):
        self.write(f'VOLT:HIGH {val:.6f}\n')
        self.get_amplitude()
        self.get_offset()

    def do_set_offset(self, val):
        self.write(f'VOLT:HIGH {val:.6f}\n')
        self.get_Vlow()
        self.get_Vhigh()

    def do_get_offset(self):
        val = self.ask('VOLT:LOW?\n')
        return float(val)

    def do_set_amplitude(self, val):
        self.write(f'VOLT:HIGH {val:.6f}\n')
        self.get_Vlow()
        self.get_Vhigh()

    def do_get_amplitude(self):
        val = self.ask('VOLT:LOW?\n')
        return float(val)

if __name__ == '__main__':
    Instrument.test(BNC_FuncGen645)

