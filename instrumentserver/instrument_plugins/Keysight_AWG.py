import logging
import time

import keysightSD1 as key
import numpy as np
from instrument import Instrument

logger = logging.getLogger(__name__)

NO_ERROR = '0,"No error"'


DEFAULT_TIMEOUT = 2000
# MIN_WAVEFORM_SIZE = 1000
MIN_WAVEFORM_SIZE = 1


class Keysight_AWG(Instrument):
    def __init__(
        self,
        name,
        chassis=1,
        slot=7,
        AWG_PRODUCT="M3202A",
        amps=[1, 1, 1, 1],
        ofs=[0, 0, 0, 0],
        trigger_io_mode=None,  # 'out', 'in', or None (leave the module's own TRG connector unconfigured)
        use_hvi=True,  # True: keep SWHVITRIG-gated elements (HVI drives timing). False: free-run.
    ):
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
        self._trigger_io_mode = trigger_io_mode
        self._use_hvi = use_hvi

        self.awg = key.SD_AOU()
        awgID = self.awg.openWithSlot(AWG_PRODUCT, chassis, slot)
        self.stop()
        self.delete_all_waveforms()
        self.clear_sequence()
        if awgID < 0:
            print("ERROR")
            print(("awgID:", awgID))
            self.awg.close()
            raise Exception("Shit don't work. Check the chassis and slot")

        logger.debug("__init__ received trigger_io_mode=%r", trigger_io_mode)
        self._configure_trigger_io(trigger_io_mode)

        self.add_parameter(
            "serial",
            type=bytes,
            flags=Instrument.FLAG_GET,
            value=self.awg.getSerialNumberBySlot(self._chassis, self._slot),
        )
        self.add_parameter(
            "part",
            type=bytes,
            flags=Instrument.FLAG_GET,
            value=self.awg.getProductNameBySlot(self._chassis, self._slot),
        )
        self.add_parameter(
            "num_modules",
            type=bytes,
            flags=Instrument.FLAG_GET,
            value=self.awg.moduleCount(),
        )
        self.add_parameter(
            "status", type=bytes, flags=Instrument.FLAG_GET, value=self.awg.getStatus()
        )
        self.add_parameter(
            "clock_freq",
            type=bytes,
            flags=Instrument.FLAG_GET,
            value=self.awg.clockGetFrequency(),
        )
        self.add_parameter(
            "clock_sync_freq",
            type=bytes,
            flags=Instrument.FLAG_GET,
            value=self.awg.clockGetSyncFrequency(),
        )

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
        self.add_parameter(
            "amplitude",
            type=float,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 4),
            channel_prefix="ch%d_",
            minval=0,
            maxval=4.5,
            units="V",
        )
        self.add_parameter(
            "offset",
            type=float,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 4),
            channel_prefix="ch%d_",
            minval=-2,
            maxval=2,
            units="V",
        )
        #        self.add_parameter('skew', type=types.IntType,
        #            flags=Instrument.FLAG_GETSET,
        #            channels=(1, 4), channel_prefix='ch%d_',
        #            minval=-5000, maxval=5000, units='ps',
        #            gui_group='channels')
        self.add_parameter(
            "output",
            type=bool,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 4),
            channel_prefix="ch%d_",
            gui_group="channels",
        )
        #        self.add_parameter('error',
        #            type=types.StringType,
        #            flags=Instrument.FLAG_GET)
        self.add_parameter(
            "timeout",
            type=int,
            value=DEFAULT_TIMEOUT,
            units="ms",
            help="Instrument read timeout",
        )

        for i in range(4):
            self.do_set_amplitude(amps[i], i + 1)
            self.do_set_offset(ofs[i], i + 1)
            self.awg.channelWaveShape(i + 1, key.SD_Waveshapes.AOU_AWG)
            self.awg.AWGqueueConfig(i + 1, 1)

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
        print(("keysight get_runstate", self.awg.getStatus()))
        return self.awg.getStatus() == 0

    def get_use_hvi(self):
        return self._use_hvi

    def set_use_hvi(self, val):
        """Toggle HVI-gated (True) vs free-running AUTOTRIG (False) sequencing.

        Takes effect on the next sequence load (set_seq_element), so reload the
        sequence after changing this.
        """
        self._use_hvi = bool(val)

    def _configure_trigger_io(self, mode):
        """Configure this module's own dedicated Trigger In/Out connector
        (separate from the 4 analog channel outputs).

        mode: 'out' to drive it as an output -- e.g. wiring it directly to
        another instrument's trigger input instead of repurposing an analog
        channel as a pseudo-trigger -- 'in' to use it as an external trigger
        input, or None (default) to leave it unconfigured, since most setups
        don't use a module's own TRG connector at all.
        """
        if mode is None:
            return
        direction = {
            "out": key.SD_TriggerDirections.AOU_TRG_OUT,
            "in": key.SD_TriggerDirections.AOU_TRG_IN,
        }[mode]
        result = self.awg.triggerIOconfig(direction, key.SD_SyncModes.SYNC_NONE)
        logger.debug("triggerIOconfig(mode=%s) -> %s", mode, result)

    def wait_done(self, delay=60000):
        print("keysight wait_done")
        self.set_timeout(delay)
        self.do_get_output(1)
        self.set_timeout(DEFAULT_TIMEOUT)
        return

    def wait_getID(self, delay=60000):
        print("keysight wait_getID")
        return

    def wait_until_run(self):
        print("keysight wait_until_run")
        return

    ###############################################
    # Sequence management
    ###############################################

    def delete_all_waveforms(self, wait=60000):
        print("keysight waveform flush")
        self.awg.waveformFlush()

    def run(self):
        print("keysight run")
        start_result = self.awg.AWGstartMultiple(15)

        # Every channel's first queue element is SWHVITRIG-gated (see
        # set_seq_element); AWGstartMultiple only arms the queue, it does
        # not fire that gate. Without this call the queue sits forever on
        # the first (near-zero) element and never reaches the real pulse,
        # even though AWGisRunning() reports the channel as running.
        trigger_result = self.awg.AWGtriggerMultiple(15)
        logger.debug(
            "run(): AWGstartMultiple(15) -> %s, AWGtriggerMultiple(15) -> %s",
            start_result, trigger_result,
        )

    def software_trigger(self, mask=15):
        """Fire a software (SWHVITRIG) trigger on the masked channels, advancing
        their queues past any SWHVITRIG-gated element.

        Exposed for timing-sensitive diagnostics: AWGtriggerMultiple in run()
        fires once at start_awgs() time, long before a later AUTOTRIG digitizer
        capture. To catch the pulse, arm the digitizer first, then call this.
        """
        return self.awg.AWGtriggerMultiple(mask)

    def stop(self):
        self.awg.AWGstopMultiple(15)

    def stop_channel(self, channel):
        self.awg.AWGstop(channel)

    def flush_channel(self, channel):
        self.awg.AWGflush(channel)

    ###############################################
    # Channel options
    ###############################################

    def do_get_output(self, channel):
        return self.awg.AWGisRunning(channel)

    def do_set_output(self, enable, channel):
        if enable:
            self.awg.AWGstart(channel)
        else:
            self.awg.AWGstop(channel)

    def all_on(self):
        print("keysight all_on")
        pass
        # TODO

    def all_off(self):
        time.sleep(0.1)
        self.__init__(
            self._name,
            self._chassis,
            self._slot,
            self._AWG_PRODUCT,
            self._channel_amps,
            self._channel_ofs,
        )
        #        ''' I honestly don't know why but we need these resets.... '''
        #        for i in range(4):
        #            self.do_set_amplitude(self.do_get_amplitude(i+1), i+1)
        #            self.do_set_offset(self.do_get_offset(i+1), i+1)
        #            self.awg.channelWaveShape(i+1, key.SD_Waveshapes.AOU_AWG)
        #            self.awg.AWGqueueConfig(i+1,1)
        #        self.clear_sequence()
        #        self.stop()
        #        self.clear_sequence()
        time.sleep(0.1)

    def do_set_amplitude(self, amp, channel):
        self._channel_amps[channel - 1] = amp
        self.awg.channelAmplitude(channel, amp)

    def do_get_amplitude(self, channel):
        return self._channel_amps[channel - 1]

    def do_set_offset(self, ofs, channel):
        self._channel_ofs[channel - 1] = ofs
        self.awg.channelOffset(channel, ofs)
        # TODO

    def do_get_offset(self, channel):
        return self._channel_ofs[channel - 1]

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
        """
        Query all parameters with FLAG_GET flag.
        """
        keys = []
        for k, v in self._parameters.items():
            if v["flags"] & Instrument.FLAG_GET:
                keys.append(k)
            if v["flags"] & Instrument.FLAG_GETSET:
                keys.append(k)
        #        print('keys', keys)
        return self.get(keys)

    ###############################################
    # Waveform loading functions
    ###############################################

    def get_bindata(self, data, m1=None, m2=None):
        """
        Convert floating point data into 14 bit integers.
        """
        absmax = np.max(np.abs(data))
        if absmax > 1:
            raise ValueError("Unable to convert data with absolute value larger than 1")

        # 0 corresponds to minus full-scale + (1 / 2**14)
        # 2**13-1 = 8191 corresponds to zero
        # 2**14-1 = 16383 corresponds to plus full-scale
        bytemem = np.round(data * (2**13 - 2)) + (2**13 - 1)
        bytemem = bytemem.astype(np.uint16)

        if m1 is not None:
            if len(data) != len(m1):
                raise ValueError("Data and marker1 should have same length")
            print(m1)
            bytemem |= 1 << 14 * m1.astype(np.uint16)
        if m2 is not None:
            if len(data) != len(m2):
                raise ValueError("Data and marker2 should have same length")
            bytemem |= 1 << 15 * m2.astype(np.uint16)

        return bytemem

    # add custom waveform as file, not correct
    def add_file(self, fn, data):
        bindata = self.get_bindata(data)
        cmd = (
            ('MMEM:DATA "%s",#6%06d' % (fn, 2 * len(data))) + bindata.tostring() + "\n"
        )
        self.write_raw(cmd)

    def add_waveform(
        self, wname, data, m1=None, m2=None, replace=True, return_cmd=False
    ):
        """
        Add waveform <wname> to AWG with content <data> and marker content
        <m1> and <m2>.
        """
        wave_data = data[:]
        #        np.savetxt(wname + '.txt', data)
        #        print('TEST OF SEQUENCE LOADING', wname)
        #        print(wave_data)

        #        print(wave_data.flags.writeable)
        #        wave_data.setflags(write=1)
        #        wave_data.flags.writeable = True
        #        print(wave_data.flags.writeable)
        #        print('inside keysight add_waveform')
        #        print('wname', wname, 'm1', m1, 'm2', m2, 'waveform_num', self._waveform_num)

        #        print(wave_data.tolist())
        if len(data) < MIN_WAVEFORM_SIZE:
            print("Waveform might be too short. Check the sequencer")

        #            print('wname', wname, 'm1', m1, 'm2', m2, 'waveform_num', self._waveform_num)
        #        if(len(data) % 10 is not 0):
        #            print('Waveform is not a multiple of ten. Will ruin the autotrigger. Check the sequencer')
        #            print('wname', wname, 'm1', m1, 'm2', m2, 'waveform_num', self._waveform_num)

        if m1 is not None:
            wave_data = m1
            wave_data = np.concatenate((wave_data[:-10], np.zeros(10)))
        if m2 is not None:
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
        return int(self.ask("AWGC:SEQ:POS?"))

    def clear_sequence(self):
        print("keysight clear_sequence")
        time.sleep(0.1)
        self.awg.AWGflush(1)
        self.awg.AWGflush(2)
        self.awg.AWGflush(3)
        self.awg.AWGflush(4)
        # TODO
        """ maybe this should be clearing a queue """

    def setup_sequence(self, n_el, reset=True, loop=True):
        self._n_el = n_el
        print(("n_el", n_el, loop))
        0 == 0
        # TODO
        """ maybe this should be adding to a queue. Need to figure out what n_el is. loop might be cyclic mode """

    def set_seq_element(self, ch, el, wname, repeat=1, trig=False):
        # use_hvi=False forces every element to AUTOTRIG so the (cyclic)
        # queue free-runs with no HVI trigger gating -- the pulse loops
        # continuously instead of waiting at a SWHVITRIG-gated element for
        # an HVI trigger that has to be distributed separately.
        if not self._use_hvi:
            trig = False
        logger.debug(
            "set_seq_element(ch=%s, el=%s, wname=%s, repeat=%s, trig=%s, use_hvi=%s) -> %s",
            ch, el, wname, repeat, trig, self._use_hvi,
            "SWHVITRIG" if trig else "AUTOTRIG",
        )
        if trig:
            self.awg.AWGqueueWaveform(
                ch,
                self._waveform_dict[wname],
                key.SD_TriggerModes.SWHVITRIG,
                0,
                repeat,
                0,
            )
        else:
            self.awg.AWGqueueWaveform(
                ch,
                self._waveform_dict[wname],
                key.SD_TriggerModes.AUTOTRIG,
                0,
                repeat,
                0,
            )

    def free_run_pulse(self, channel=1, length=2000, amp=0.9,
                       trigger_out=False, marker_length=100):
        """Diagnostic: continuously output a square pulse on <channel>, free
        running with no trigger gating, so an AUTOTRIG digitizer capture is
        guaranteed to catch it regardless of HVI/SWHVITRIG timing.

        Half of <length> samples high at +<amp>, half at 0. Queued AUTOTRIG +
        cyclic so it loops forever once started. Use this to test the analog
        path (e.g. AWG ch -> DIG ch) end to end, isolated from the sequencer,
        HVI, and any SWHVITRIG gating. Call stop()/clear_sequence() to undo.

        If <trigger_out> is True, also drive this module's front-panel Trigger
        I/O connector high at the start of every pulse (AWGqueueMarkerConfig,
        markerMode=2 = on first sample of waveform). This emits a hardware
        trigger edge synchronized to the ch pulse -- wire TRG OUT -> a
        digitizer's TRG IN to capture each pulse with EXTTRIG. <marker_length>
        sets the marker pulse width in units of TCLKsys*5 (~5 ns each at
        1 GS/s).
        """
        data = np.zeros(int(length))
        data[: int(length) // 2] = amp

        self.awg.AWGstop(channel)
        self.awg.AWGflush(channel)

        wname = "free_run_pulse_%d" % channel
        self.add_waveform(wname, data)
        self.awg.AWGqueueConfig(channel, 1)  # 1 = cyclic, loop forever
        self.awg.AWGqueueWaveform(
            channel,
            self._waveform_dict[wname],
            key.SD_TriggerModes.AUTOTRIG,
            0,
            1,
            0,
        )

        if trigger_out:
            # Front-panel TRG connector must be an output for the marker to
            # appear on it.
            self._configure_trigger_io("out")
            # markerMode=2: pulse at the first sample of every waveform play
            # (i.e. the same moment the ch pulse starts). trgPXImask=0 (no PXI
            # line), trgIOmask=1 (front-panel TRG IO, bit0), value=1 (active
            # high), syncMode=0 (CLKsys), delay=0.
            marker_result = self.awg.AWGqueueMarkerConfig(
                channel, 2, 0, 1, 1, 0, int(marker_length), 0
            )
            logger.debug(
                "free_run_pulse(channel=%s) AWGqueueMarkerConfig -> %s",
                channel, marker_result,
            )

        result = self.awg.AWGstart(channel)
        logger.debug("free_run_pulse(channel=%s, trigger_out=%s) AWGstart -> %s",
                     channel, trigger_out, result)
        return result

    ###############################################
    # Convenience functions to play simple waveforms
    ###############################################

    def play_waveforms(self, chan_wform, run=True):
        print("keysight play_waveforms")
        """
        Play simple waveforms on channels.
        chan_wform is a list of <chan>, <waveform name> tuples.
        """
        0 == 0
        # TODO

    def sideband_modulate(
        self, period=None, freq=None, dphi=0, amp=1.0, chans=(1, 2), run=True
    ):
        """
        Sideband modulate using period <period> or frequency <freq>.
        (period is negative for negative frequencies).

        The first channel will be setup as I (cosine) and the second as
        Q (sine). The phase adjustment <dphi> is added to the Q channel,
        resulting in outputs:

        chan[0] = cos(2pi*x/period)
        chan[1] = sin(2pi*x/period + dphi)
        """

        0 == 0
        # TODO

    def output_zeros(self, chans=(1, 2), run=True):
        0 == 0
        # TODO

    def output_sqwave(self, period, chans=(1, 2), amp=0.1, dcycle=0.5, run=True):
        0 == 0
        # TODO

    ###############################################
    # Bulk loading routines
    ###############################################

    def bulk_waveform_load(self, wforms, maxlen=100000, replace=False):
        """
        Bulk load of waveforms.
        <wforms> should be a list of (name, data, m1, m2) tuples.
        <maxlen> is the maximum command string length at which the command
        should be sent to the AWG.
        """

        0 == 0
        # TODO

    def bulk_sequence_load(self, chan, seq):
        """
        Bulk load of sequence elements.
        <seq> should be a list of (index, waveform name, loop count, trigger).
        """

        0 == 0
        # TODO

    def pull_dot_awg(self, path):
        """
        Save the AWG state to a .awg file.
        """
        0 == 0
        # TODO

    def load_dot_awg(self, path):
        """
        Load the AWG state from a .awg file.
        """
        0 == 0
        # TODO

    def get_seq_length(self):
        """
        See how long the loaded sequence is.  Useful to check that a load
        was successful.
        """
        0 == 0
        # TODO

    def jump(self, pos=1):
        0 == 0
        # TODO
        # TODO
