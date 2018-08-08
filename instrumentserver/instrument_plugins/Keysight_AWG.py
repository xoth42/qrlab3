import sys
import time
import types
import ctypes
import numpy as np
import keysightSD1 as key
from instrument import Instrument
import logging

NO_ERROR = u'0,"No error"'


DEFAULT_TIMEOUT = 2000


class Keysight_AWG(Instrument):


    def __init__(self, name, chassis=1, slot=7, AWG_PRODUCT = "M3202A", amps = [1,1,1,1], ofs = [0,0,0,0]):
        super(Keysight_AWG, self).__init__(name)
#        self.set_timeout(120000)

        self._waveform_num = 0
        self._waveform_dict = {}
        self._channel_amps = np.zeros(4)
        self._channel_ofs = np.zeros(4)
        self._n_el = 0
        self._timeout = DEFAULT_TIMEOUT

        self._name = name
        self._chassis = chassis
        self._slot = slot
        self._AWG_PRODUCT = AWG_PRODUCT
        
        self.awg = key.SD_AOU()
        awgID = self.awg.openWithSlot(AWG_PRODUCT, chassis, slot)
        self.stop()
        self.delete_all_waveforms()
        self.clear_sequence()
        if awgID < 0:
            print("ERROR")
            print("awgID:", awgID)
            self.awg.close()
            raise Exception("Shit don't work. Check the chassis and slot")


        
        self.add_parameter('serial', type=types.StringType,
            flags=Instrument.FLAG_GET, 
            value = self.awg.getSerialNumberBySlot(self._chassis, self._slot))
        self.add_parameter('part', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.awg.getProductNameBySlot(self._chassis, self._slot))
        self.add_parameter('num_modules', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.awg.moduleCount())
        self.add_parameter('status', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.awg.getStatus())
        self.add_parameter('clock_freq', type=types.StringType,
            flags=Instrument.FLAG_GETSET,
            value = self.awg.clockGetFrequency())
        self.add_parameter('clock_sync_freq', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.awg.clockGetSyncFrequency())

#        self.add_parameter('clock',
#            type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            minval=1e6, maxval=1.2e9, units='Hz')
#        self.add_parameter('refsrc',
#            type=types.StringType,
#            flags=Instrument.FLAG_GETSET,
#            option_list=('INT', 'EXT'))
#        self.add_parameter('reffreq',
#            type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            option_list=(10e6, 20e6, 100e6), units='Hz')
#        self.add_parameter('trig_impedance',
#            type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            option_list=(1000, 50),
#            units='Ohm')
#        self.add_parameter('trig_level',
#            type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            units='V')
#        self.add_parameter('trig_slope',
#            type=types.StringType,
#            flags=Instrument.FLAG_GETSET,
#            option_list=('POS', 'NEG'))

        # Channel options
        self.add_parameter('amplitude', type=types.FloatType,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 4), channel_prefix='ch%d_',
            minval=0, maxval=4.5, units='V')
        self.add_parameter('offset', type=types.FloatType,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 4), channel_prefix='ch%d_',
            minval=-2, maxval=2, units='V')
#        self.add_parameter('skew', type=types.IntType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_',
#            minval=-5000, maxval=5000, units='ps',
#            gui_group='channels')
        self.add_parameter('output', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 4), channel_prefix='ch%d_',
            gui_group='channels')
#        self.add_parameter('error',
#            type=types.StringType,
#            flags=Instrument.FLAG_GET)
        self.add_parameter('timeout', type=types.IntType, value=DEFAULT_TIMEOUT,
           units='ms', help='Instrument read timeout')

        for i in range(4):
            self.do_set_amplitude(amps[i], i+1)
            self.do_set_offset(ofs[i], i+1)
            self.awg.channelWaveShape(i+1, key.SD_Waveshapes.AOU_AWG)
            self.awg.AWGqueueConfig(i+1,1)
            
        self.get_all()




#        trigger = key.SD_Wave()
#        trigger_data = np.concatenate((np.ones(10)*.5, np.zeros(10)))
#        trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
#        self.awg.waveformLoad(trigger, 0)   
#        self.waveform_num += 1
#        
#        self.awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
#        self.awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
        

        
        
        
        

    ###############################################
    # Status checks / controls
    ###############################################

    def do_get_serial(self):
        return self.awg.getSerialNumberBySlot(self._chassis, self._slot)

    def do_get_part(self):
        return self.awg.getProductNameBySlot(self._chassis, self._slot)

    def do_get_num_modules(self):
        return self.awg.moduleCount()
        
    def do_get_status(self):
        return self.awg.getStatus()
        
    def do_get_clock_freq(self):
        return self.awg.clockGetFrequency()
        
    def do_get_clock_sync_freq(self):
        return self.awg.clockGetSyncFrequency()
        
    def get_runstate(self):
        print('keysight get_runstate', self.awg.getStatus())
        return self.awg.getStatus() == 0
        
    def wait_done(self, delay=60000):
        print('keysight wait_done')
        self.set_timeout(delay)
        self.do_get_output(1)
        self.set_timeout(DEFAULT_TIMEOUT)
        return
        
    def wait_getID(self, delay=60000):
        print('keysight wait_getID')
        return

    def wait_until_run(self):
        print('keysight wait_until_run')
        return
        

    ###############################################
    # Sequence management
    ###############################################

    def delete_all_waveforms(self, wait=60000):
        print('keysight waveform flush')
        self.awg.waveformFlush()

    def prime(self):
        '''
        logging.info('Priming the AWG')
        data = [[],[],[],[]]
        for e in range(self.n_el):
            trigger_off = False
            for n in range(4):
                if self.m1[self.waveform_queue[n, e]] is not None:
                    data[n].extend(self.m1[self.waveform_queue[n, e]])
                    trigger_off = True
                    
                elif self.m2[self.waveform_queue[n, e]] is not None :
                    data[n].extend(self.m2[self.waveform_queue[n, e]])
                    trigger_off = True
                else:
                    data[n].extend(self.waveform_list[self.waveform_queue[n, e]])
            if trigger_off:
                for n in range(4):
                    data[n].extend([0]*self.waveform_delay)
                
        for n in range(4):
            waveform_data = np.array(data[n])
            print('waveform length', 1, len(waveform_data))
            
            wave = key.SD_Wave()
            wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, waveform_data)
            self.awg.waveformLoad(wave, n)
            self.awg.AWGqueueWaveform(n+1, n, key.SD_TriggerModes.SWHVITRIG, 0, 0, 0)
        logging.info('AWG priming finished')
#        time.sleep(5)

#        print(self.waveform_dict)
#        print(self.waveform_queue)
#        print(self.m1)
#        print(self.m2)
        '''
        '''
        for i in range(4):
            data = []
            for j in range(self.n_el):
#                print(i, j, self.m1[self.waveform_queue[i, j]])
#                print(i, j, self.m2[self.waveform_queue[i, j]])
                if self.m1[self.waveform_queue[i, j]] is not None:
#                    print(i, j, 'm1 appended')
                    data.extend(self.m1[self.waveform_queue[i, j]])
                elif self.m2[self.waveform_queue[i, j]] is not None :
#                    print(i, j, 'm2 appended')
                    data.extend(self.m2[self.waveform_queue[i, j]])
                else:
                    data.extend(self.waveform_list[self.waveform_queue[i, j]])
            data = np.array(data)
            data = np.concatenate((data, np.zeros(self.waveform_delay)))
            
            print('waveform length', 1, len(data))
            
            wave = key.SD_Wave()
            wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, data)
            self.awg.waveformLoad(wave, i)
            self.awg.AWGqueueWaveform(i+1, i, key.SD_TriggerModes.SWHVITRIG, 0, 0, 0)
        '''       


    def run(self):
        print('keysight run')
        time.sleep(1)
        self.awg.AWGstartMultiple(15)
#        self.awg.AWGtriggerMultiple(15)


    def stop(self):
        self.awg.AWGstopMultiple(15)

    ###############################################
    # Channel options
    ###############################################

    def do_get_output(self, channel):
        return self.awg.AWGisRunning(channel)

    def do_set_output(self, enable, channel):
        0==0
        #TODO

    def all_on(self):
        print('keysight all_on')
        0==0
        #TODO


    def all_off(self):
        self.__init__(self._name, self._chassis, self._slot, self._AWG_PRODUCT,
                      self._channel_amps, self._channel_ofs)
#        ''' I honestly don't know why but we need these resets.... '''
#        for i in range(4):
#            self.do_set_amplitude(self.do_get_amplitude(i+1), i+1)
#            self.do_set_offset(self.do_get_offset(i+1), i+1)
#            self.awg.channelWaveShape(i+1, key.SD_Waveshapes.AOU_AWG)
#            self.awg.AWGqueueConfig(i+1,1)
#        self.clear_sequence()
#        self.stop()
#        self.clear_sequence()
        time.sleep(1)

    def do_set_amplitude(self, amp, channel):
        self._channel_amps[channel-1] = amp
        self.awg.channelAmplitude(channel, amp)
        

    def do_get_amplitude(self, channel):
        return self._channel_amps[channel-1]

    def do_set_offset(self, ofs, channel):
        self._channel_ofs[channel-1] = ofs
        self.awg.channelOffset(channel, ofs)
        #TODO

    def do_get_offset(self, channel):
        return self._channel_ofs[channel-1]
        
    def do_get_timeout(self):
        return self._timeout
        
    def do_set_timeout(self, timeout):
        self._timeout = timeout
#
#    def do_set_skew(self, skew, channel):
#        0==0
#        #TODO
#
#
#    def do_get_skew(self, channel):
#        '''Get channel skew in ps.'''
#        val = self.ask('SOURCE%d:SKEW?' % (channel,))
#        print val
#        return float(val) * 1e12

    def get_all(self):
        '''
        Query all parameters with FLAG_GET flag.
        '''
        keys = []
        for k, v in self._parameters.iteritems():
            if v['flags'] & Instrument.FLAG_GET:
                keys.append(k)
            if v['flags'] & Instrument.FLAG_GETSET:
                keys.append(k)
#        print('keys', keys)
        return self.get(keys)


    ###############################################
    # Waveform loading functions
    ###############################################

    def get_bindata(self, data, m1=None, m2=None):
        '''
        Convert floating point data into 14 bit integers.
        '''
        absmax = np.max(np.abs(data))
        if absmax > 1:
            raise ValueError('Unable to convert data with absolute value larger than 1')

        # 0 corresponds to minus full-scale + (1 / 2**14)
        # 2**13-1 = 8191 corresponds to zero
        # 2**14-1 = 16383 corresponds to plus full-scale
        bytemem = np.round(data * (2**13-2)) + (2**13-1)
        bytemem = bytemem.astype(np.uint16)

        if m1 is not None:
            if len(data) != len(m1):
                raise ValueError('Data and marker1 should have same length')
            print m1
            bytemem |= 1<<14 * m1.astype(np.uint16)
        if m2 is not None:
            if len(data) != len(m2):
                raise ValueError('Data and marker2 should have same length')
            bytemem |= 1<<15 * m2.astype(np.uint16)

        return bytemem

    # add custom waveform as file, not correct
    def add_file(self, fn, data):
        bindata = self.get_bindata(data)
        cmd = ('MMEM:DATA "%s",#6%06d'%(fn,2*len(data))) + bindata.tostring() + '\n'
        self.write_raw(cmd)

    def add_waveform(self, wname, data, m1=None, m2=None, replace=True, return_cmd=False):
        '''
        Add waveform <wname> to AWG with content <data> and marker content
        <m1> and <m2>.
        '''
        wave_data = data[:]
#        print(wave_data)

#        print(wave_data.flags.writeable)
#        wave_data.setflags(write=1)
#        wave_data.flags.writeable = True
#        print(wave_data.flags.writeable)
#        print('inside keysight add_waveform')
#        print('wname', wname, 'm1', m1, 'm2', m2, 'waveform_num', self._waveform_num)

#        print(wave_data.tolist())
        if(len(data) < 1000):
            print('Waveform might be too short. Check the sequencer')

#            print('wname', wname, 'm1', m1, 'm2', m2, 'waveform_num', self._waveform_num)
#        if(len(data) % 10 is not 0):
#            print('Waveform is not a multiple of ten. Will ruin the autotrigger. Check the sequencer')
#            print('wname', wname, 'm1', m1, 'm2', m2, 'waveform_num', self._waveform_num)
        
        if(m1 is not None):
            wave_data = m1
            wave_data = np.concatenate((wave_data[:-10], np.zeros(10)))
        if(m2 is not None):
            wave_data = m2
            wave_data = np.concatenate((wave_data[:-10], np.zeros(10)))
        
        wave = key.SD_Wave()
        wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, wave_data)
        self.awg.waveformLoad(wave, self._waveform_num)
            
        self._waveform_dict[wname] = self._waveform_num
        self._waveform_num += 1
        
#        logging.info(self.do_get_status())

    ###############################################
    # Sequence functions
    ###############################################

    def do_get_seq_pos(self):
        return int(self.ask('AWGC:SEQ:POS?'))

    def clear_sequence(self):
        print('keysight clear_sequence')
        self.awg.AWGflush(1)
        self.awg.AWGflush(2)
        self.awg.AWGflush(3)
        self.awg.AWGflush(4)
        #TODO
        ''' maybe this should be clearing a queue '''

    def setup_sequence(self, n_el, reset=True, loop=True):
        self._n_el = n_el
        print('n_el', n_el, loop)
        0==0
        #TODO
        ''' maybe this should be adding to a queue. Need to figure out what n_el is. loop might be cyclic mode '''

    def set_seq_element(self, ch, el, wname, repeat=1, trig=False):
        
#        print('keysight set_seq_element')
#        print('ch', ch, 'el', el, 'wname', wname, 'repeat', repeat, 'trig', trig)
        if trig:
            self.awg.AWGqueueWaveform(ch, self._waveform_dict[wname], key.SD_TriggerModes.SWHVITRIG, 0, repeat, 0)
        else:
            self.awg.AWGqueueWaveform(ch, self._waveform_dict[wname], key.SD_TriggerModes.AUTOTRIG, 0, repeat, 0)



    ###############################################
    # Convenience functions to play simple waveforms
    ###############################################

    def play_waveforms(self, chan_wform, run=True):
        print('keysight play_waveforms')
        '''
        Play simple waveforms on channels.
        chan_wform is a list of <chan>, <waveform name> tuples.
        '''
        0==0
        #TODO

    def sideband_modulate(self, period=None, freq=None, dphi=0, amp=1.0, chans=(1,2), run=True):
        '''
        Sideband modulate using period <period> or frequency <freq>.
        (period is negative for negative frequencies).

        The first channel will be setup as I (cosine) and the second as
        Q (sine). The phase adjustment <dphi> is added to the Q channel,
        resulting in outputs:

        chan[0] = cos(2pi*x/period)
        chan[1] = sin(2pi*x/period + dphi)
        '''

        0==0
        #TODO

    def output_zeros(self, chans=(1,2), run=True):
        0==0
        #TODO

    def output_sqwave(self, period, chans=(1,2), amp=0.1, dcycle=0.5, run=True):
        0==0
        #TODO

    ###############################################
    # Bulk loading routines
    ###############################################

    def bulk_waveform_load(self, wforms, maxlen=100000, replace=False):
        '''
        Bulk load of waveforms.
        <wforms> should be a list of (name, data, m1, m2) tuples.
        <maxlen> is the maximum command string length at which the command
        should be sent to the AWG.
        '''

        0==0
        #TODO

    def bulk_sequence_load(self, chan, seq):
        '''
        Bulk load of sequence elements.
        <seq> should be a list of (index, waveform name, loop count, trigger).
        '''

        0==0
        #TODO

    def pull_dot_awg(self, path):
        '''
        Save the AWG state to a .awg file.
        '''
        0==0
        #TODO

    def load_dot_awg(self, path):
        '''
        Load the AWG state from a .awg file.
        '''
        0==0
        #TODO



    def get_seq_length(self):
        '''
        See how long the loaded sequence is.  Useful to check that a load
        was successful.
        '''
        0==0
        #TODO

    def jump(self, pos=1):
        0==0
        #TODO
