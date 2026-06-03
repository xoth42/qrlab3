# FPGA_Yngwie.py, instrument driver for Yngwie FPGA card
# Reinier Heeres 2014

import os
import sys
import inspect
import time
import ctypes
import types
import numpy as np
from .instrument import Instrument
import logging

# Add paths for dependencies.
srcdir = os.path.split(os.path.abspath(inspect.getsourcefile(lambda _: None)))[0]
basedir = '\\'.join(srcdir.split('\\')[:-2])
sys.path.append(os.path.join(basedir, 'Yngwie\\Python\\Core'))

import YngwieInterface

INI_DEFAULT = '''
adcTestEnable=0
Alerts=65535
ClockFrequency=1000
dacTestEnable=0
dacTestFrequency=20
DumpEnabled=0
DumpEntireVelo=0
DumpPath
ExternalClock=1
ExternalReference=1
ReferenceFrequency=1000
Rx.EdgeMode=1
Rx.EnabledChannels=3
Rx.ExternalTrigger=1
Rx.FrameMode=0
Rx.FrameSize=65536
Rx.SampleRate=1000
SeparatePackets=0
TimerInterval=1000
TriggerDelay=1
Tx.EdgeMode=1
Tx.ExternalTrigger=1
Tx.FrameMode=0
Tx.FrameSize=8192
VeloPacketSize=65336
'''

class Yngwie_FPGA(Instrument):

    def __init__(self, name, boardid=None, open=True, **kwargs):
        super(Yngwie_FPGA, self).__init__(name)

        if boardid is None:
            raise Exception('Yngwie driver needs a boardid')
        self._target = int(boardid)

        self.yng = None
        self._ssb_freq = {}
        self._ssb_theta = {}
        self._ssb_ratio = {}

        self._noutputs = kwargs.pop('noutputs', 4)
        self._nmodes = kwargs.pop('nmodes', 2)

        self.add_parameter('noutputs', type=int,
            option_list=(2,4), value=self._noutputs,
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('nmodes', type=int,
            options_list=(1,2,4), value=self._nmodes,
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('reshape_mode', type=bytes,
            option_list=('full', 'none', 'mixer'),
            flags=Instrument.FLAG_GETSET)
        self.add_parameter('dot_product_mode', type=bytes,
            option_list=('dot product', "pass both", "dup ch0", "dup ch1"),
            flags=Instrument.FLAG_GETSET)

        modes = [i for i in range(self._nmodes)]
        self.add_parameter('ssbfreq', type=float, channels=modes,
            value=0, gui_group='ssb',
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('ssbtheta', type=float, channels=modes,
            min=-180, max=180, units='deg', format='%.03f',
            value=0, gui_group='ssb',
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('ssbratio', type=float, channels=modes,
            min=0, max=1.99, format='%.06f',
            value=1, gui_group='ssb',
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('offset', type=tuple, channels=modes,
            gui_group='ssb',
            flags=Instrument.FLAG_GETSET)

        self.add_parameter('fillup_thresh', type=int,
            min=0, max=255, gui_group='internal',
            flags=Instrument.FLAG_GET)
        self.add_parameter('regulation_thresh', type=int,
            min=0, max=255, gui_group='internal',
            flags=Instrument.FLAG_GET)

        self.add_parameter('regulation_enabled', type=bool,
            gui_group='internal', flags=Instrument.FLAG_GETSET)
        self.add_parameter('awg_enabled', type=bool,
            gui_group='internal', flags=Instrument.FLAG_GETSET)
        self.add_parameter('external_trigger_enabled', type=bool,
            gui_group='internal', flags=Instrument.FLAG_GETSET)

        self.add_parameter('dump_path', type=bytes,
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
            value=r'd:\data\fpga\exp_')
        self.add_parameter('run_status', type=int,
            flags=Instrument.FLAG_GET)
        self.add_parameter('unlimited', type=bool,
            flags=Instrument.FLAG_GETSET)

        self.add_parameter('buffer_gen_width', type=int,
            flags=Instrument.FLAG_GETSET)
        self.add_parameter('buffer_gen_delay', type=int,
            flags=Instrument.FLAG_GETSET)

        self.add_parameter('delay_analog', type=int,
            gui_group='delays', flags=Instrument.FLAG_GETSET)
        self.add_parameter('delay_marker', type=int, channels=(0,1,2,3),
            gui_group='delays', flags=Instrument.FLAG_GETSET)
        self.add_parameter('rrec_generate', type=int,
            flags=Instrument.FLAG_GETSET,
            help='Get/set result record generation mask')
        self.add_parameter('demod_scale_sig', type=float,
            minval=0, maxval=8.0, value=1.0,
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('demod_scale_ref', type=float,
            minval=0, maxval=8.0, value=1.0,
            flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)

        self.add_function('stop')

        self.set(kwargs)

        if open:
            self.open()

        if kwargs.pop('reset', False):
            self.reset()
        else:
            self.get_all()

    def write_ini_file(self, fn='yngwie.ini'):
        data = INI_DEFAULT

        if self.get_noutputs() == 2:
            data += 'Tx.EnabledChannels=5\nTx.SampleRate=1000\nfourOutputChannels=0'
        else:
            data += 'Tx.EnabledChannels=15\nTx.SampleRate=500\nfourOutputChannels=1'

        f = open(fn, 'w')
        f.write(data)
        f.close()

    def open(self):
        '''Open or re-open device.'''

        if self.yng:
            del self.yng

        fn = os.path.join(srcdir, 'yngwie_instrument.ini')
        self.write_ini_file(fn)
        self.yng = YngwieInterface.YngwieInterface(self._target, fn)
        print(f'Setting dump path to {self.get_dump_path()}')
        self.yng.dump_path = self.get_dump_path()

        self.update_modes()

    def update_modes(self):
        '''
        Update analog mode settings on FPGA.
        '''

        nmodes = self.get_nmodes()
        if nmodes == 2:
            mul = 2
        else:
            mul = 1

        self.yng.AnalogModes.number = nmodes
        self.yng.AnalogModes.reshape_mode = self.get_reshape_mode()
        self.yng.AnalogModes.four_channels_enabled = (self.get_noutputs() == 4)

        for i in range(nmodes):
            freq = int(round(self._ssb_freq.get(i, 0)))
            theta = self._ssb_theta.get(i, 0)
            ratio = self._ssb_ratio.get(i, 1.0)
            self.yng.AnalogModes.load(mode_index=mul*i,
                    frequency=freq,
                    theta=theta,
                    ratio=ratio,
            )

    def do_set_noutputs(self, v):
        self._noutputs = v

    def do_set_nmodes(self, v):
        self.yng.AnalogModes.number = v
        self._nmodes = v

    def do_set_reshape_mode(self, v):
        self.yng.AnalogModes.reshape_mode = v.lower()

    def do_get_reshape_mode(self):
        return self.yng.AnalogModes.reshape_mode

    def do_set_dot_product_mode(self, v):
        self.yng.dot_product_mode = v.lower()

    def do_get_dot_product_mode(self):
        return self.yng.dot_product_mode

    def do_set_offset(self, v, channel=None):
        if len(v) != 2:
            raise ValueError('Offset should be specified as 2 integers')
        setattr(self.yng.AnalogModes, f'offset{int(channel)}', v)

    def do_get_offset(self, channel=None):
        return getattr(self.yng.AnalogModes, f'offset{int(channel)}')

    def do_set_ssbfreq(self, v, channel=None):
        self._ssb_freq[channel] = v

    def do_set_ssbtheta(self, v, channel=None):
        self._ssb_theta[channel] = v

    def do_set_ssbratio(self, v, channel=None):
        self._ssb_ratio[channel] = v

    def do_get_fillup_thresh(self):
        return self.yng.fillup_threshold

    def do_set_fillup_thresh(self, v):
        self.yng.fillup_threshold = v

    def do_get_regulation_thresh(self):
        return self.yng.regulation_threshold

    def do_set_regulation_thresh(self, v):
        self.yng.regulation_threshold = v

    def do_set_dump_path(self, v):
        self.yng.dump_path = v

    def do_read_logic(self, address, bitrange=(31,0)):
        return self.yng.m_yng.ReadLogic(address, bitrange)

    def do_write_logic(self, address, val, bitrange=(31,0)):
        return self.yng.m_yng.WriteLogic(address, val, bitrange)

    def accept_stream(self, streamID, bytes_needed, file_size=None, first_file_size=None, stream_pattern=0xffffffff):
        print(f'Accepting {streamID},{bytes_needed},{file_size}')
        return self.yng.StreamRouter.accept(streamID, bytes_needed, file_size, first_file_size, stream_pattern)

    def do_set_buffer_gen_width(self, val):
        self.do_write_logic(0xc05, 13, [21,16])
        self.do_write_logic(0xc04, val)

    def do_get_buffer_gen_width(self):
        return self.do_read_logic(0xc04)

    def do_set_buffer_gen_delay(self, val):
        self.do_write_logic(0xc05, 13, [21,16])
        self.do_write_logic(0xc05, val, [29, 24])

    def do_get_buffer_gen_delay(self):
        return self.do_read_logic(0xc05, [29, 24])

    def do_set_rrec_generate(self, val):
        self.do_write_logic(0xc03, val)

    def do_get_rrec_generate(self):
        return self.do_read_logic(0xc03)

    def is_streaming(self):
        return self.yng.m_yng.IsStreaming()

    def do_get_regulation_enabled(self):
        return self.yng.regulation_enabled

    def do_set_regulation_enabled(self, v):
        self.yng.regulation_enabled = v

    def do_get_awg_enabled(self):
        return self.yng.awg_enabled

    def do_set_awg_enabled(self, v):
        self.yng.awg_enabled = v

    def do_get_external_trigger_enabled(self):
        return self.yng.external_trigger_enabled

    def do_set_external_trigger_enabled(self, v):
        self.yng.external_trigger_enabled = v

    def do_set_delay_analog(self, v):
        self.yng.Delays.analog = v

    def do_get_delay_analog(self):
        return self.yng.Delays.analog

    def do_set_delay_marker(self, v, channel=None):
        setattr(self.yng.Delays, f'marker{int(channel)}', v)

    def do_get_delay_marker(self, channel=None):
        return getattr(self.yng.Delays, f'marker{int(channel)}')

    def load_tables(self, file_prefix):
        print(f'Yngwie: Loading tables from {file_prefix}')
        self.yng.regulation_enabled = True
        return self.yng.load_tables(file_prefix)

    def start(self):
        self.yng.m_yng.DumpSettings()
        self.yng.StreamRouter.dump()

        print('Yngwie: Starting...')
        self.yng.start()
        time.sleep(0.75)
        self.set_awg_enabled(True)
        time.sleep(0.1)
        self.set_external_trigger_enabled(True)
        time.sleep(0.1)

    def stop(self):
        print('Yngwie: Stopping...')
        self.yng.StreamRouter.dump()
        self.yng.stop()
        self.set_external_trigger_enabled(False)
        self.set_awg_enabled(False)

    def do_get_run_status(self):
        return self.yng.run_status()

    def do_get_unlimited(self):
        return self.yng.StreamRouter.unlimited

    def do_set_unlimited(self, v):
        self.yng.StreamRouter.unlimited = v

    def do_set_demod_scale_sig(self, v):
        self._demod_scale_sig = v

    def do_set_demod_scale_ref(self, v):
        self._demod_scale_ref = v

    def close(self):
        '''Clean-up yngwie (to prevent crashing).'''
        if not self.yng:
            return
        self.stop()
        del self.yng
        self.yng = None

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    yng = Instrument.test(Yngwie_FPGA)
