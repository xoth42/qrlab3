import sys
import time
import types
import ctypes
import numpy as np
import keysightSD1 as key
from instrument import Instrument
import logging
from lib.math import demod
import gc


NO_ERROR = u'0,"No error"'


DEFAULT_TIMEOUT = 2000
VOLTAGE_SCALE = 2.8


class Keysight_DIG(Instrument):


    def __init__(self, name, chassis=0, slot=3, DIG_PRODUCT = "M3102A", **kwargs):
        super(Keysight_DIG, self).__init__(name)
        self._timeout = DEFAULT_TIMEOUT
        self._main_channel=1
        self._ref_channel=2
        self._nsamples=1000
        self._naverages=1000
        self._main_delay=0
        self._ref_delay=0
        self._if_period=10

        self._name = name
        self._chassis = chassis
        self._slot = slot
        self._DIG_PRODUCT = DIG_PRODUCT
        
        self.dig = key.SD_AIN()
        ainID = self.dig.openWithSlot(DIG_PRODUCT, self._chassis, self._slot)
        self.flush()
        self.stop()

        if ainID < 0:
            print("ERROR")
            print("ainID:", ainID)
            raise Exception("Shit don't work. Check the chassis and slot")


        
        
        # Device Properties
        self.add_parameter('serial', type=types.StringType,
            flags=Instrument.FLAG_GET, 
            value = self.dig.getSerialNumberBySlot(self._chassis, self._slot))
        self.add_parameter('part', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.dig.getProductNameBySlot(self._chassis, self._slot))
        self.add_parameter('num_modules', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.dig.moduleCount())
        self.add_parameter('status', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.dig.getStatus())
        self.add_parameter('clock_freq', type=types.StringType,
            flags=Instrument.FLAG_GETSET,
            value = self.dig.clockGetFrequency())
        self.add_parameter('clock_sync_freq', type=types.StringType,
            flags=Instrument.FLAG_GET,
            value = self.dig.clockGetSyncFrequency())

        # Channel options
#        self.add_parameter('triggerIO', type=types.StringType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_')
#        self.add_parameter('DAQdigitalTrigger', type=types.StringType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_')
#        self.add_parameter('prescaler', type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_')
#        self.add_parameter('fullScale', type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_')
#        self.add_parameter('impedance', type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_', units='ohms')
#        self.add_parameter('coupling', type=types.FloatType,
#            flags=Instrument.FLAG_GETSET,
#            channels=(1, 4), channel_prefix='ch%d_')
        
        self.add_parameter('main_channel', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           value=1)
        self.add_parameter('ref_channel', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           value=2)
        # Acquisition options
        self.add_parameter('nsamples', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=64, maxval=1e9, value=5120,
                           help='Number of samples per record')
        self.add_parameter('naverages', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=1, maxval=1000000, value=500,
                           help='Number of averages to do')
        
        self.add_parameter('main_delay', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           value=0)
        
        self.add_parameter('ref_delay', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           value=0)
        
        self.add_parameter('if_period', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=2, maxval=1000, value=20,
                               help='Intermediate Frequency period')
        
        self.add_parameter('timeout', type=types.IntType, value=DEFAULT_TIMEOUT,
           units='ms', help='Instrument read timeout')
        
        self.set(kwargs)
        self.get_all()

        
        

    ###############################################
    # Status checks / controls
    ###############################################

    def do_get_serial(self):
        return self.dig.getSerialNumberBySlot(self._chassis, self._slot)

    def do_get_part(self):
        return self.dig.getProductNameBySlot(self._chassis, self._slot)

    def do_get_num_modules(self):
        return self.dig.moduleCount()
        
    def do_get_status(self):
        return self.dig.getStatus()
        
    def do_get_clock_freq(self):
        return self.dig.clockGetFrequency()

    def do_set_clock_freq(self, freq):
        self.dig.clockSetFrequency(self, freq, mode = 1)
        
    def do_get_clock_sync_freq(self):
        return self.dig.clockGetSyncFrequency()
            
    def get_runstate(self):
        print('keysight get_runstate', self.dig.getStatus())
        return self.dig.getStatus() == 0

    def do_get_timeout(self):
        return self._timeout
        
    def do_set_timeout(self, timeout):
        self._timeout = timeout
        

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
        return self.get(keys)
    
    def set_all(self):
        '''
        Query all parameters with FLAG_GET flag.
        '''
        keys = []
        for k, v in self._parameters.iteritems():
            if v['flags'] & Instrument.FLAG_SET:
                keys.append(k)
            if v['flags'] & Instrument.FLAG_GETSET:
                keys.append(k)
        return self.set(keys)

    ###############################################
    # Channel settings and operation
    ###############################################

    def run(self):
        print('keysight dig run')
        self.dig.DAQstartMultiple(15)

    def run_channel(self, channel):
        self.dig.DAQstart(channel)

    def stop(self):
        self.dig.DAQstopMultiple(15)
        
    def stop_channel(self, channel):
        self.dig.DAQstop(channel)
        
    def flush(self):
        self.dig.DAQflushMultiple(15)
        
    def flush_channel(self, channel):
        self.dig.DAQflush(channel)
        
    def DAQread(self, nDAQ, nPoints, timeOut = 0):
        self.dig.DAQread(self, nDAQ, nPoints, timeOut)

    def set_DAQ(self, channel, pointsPerCycle, nCycles, triggerDelay, triggermode = key.SD_TriggerModes.EXTTRIG):
        self.dig.DAQconfig(self, channel, pointsPerCycle, nCycles, triggerDelay, triggermode)

#    def do_set_triggerIO(self, direction = key.SD_TriggerDirections.AOU_TRG_IN):
#        self._triggerIOconfig = direction
#        self.dig.triggerIOconfig(direction)
#                
#    def do_get_triggerIO(self):
#        return self._triggerIOconfig
#    
#    def do_set_DAQdigitalTrigger(self, channel, triggerSource = key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
#                                    triggerBehavior = key.SD_TriggerBehaviors.TRIGGER_HIGH):
#        self.dig.DAQdigitalTriggerConfig(self, channel, triggerSource, triggerBehavior)

#    def do_set_prescaler(self, channel, prescaler):
#        self._prescaler = prescaler
#        self.dig.channelPrescalerConfig(channel, prescaler)
#        
#    def do_set_fullScale(self, channel, fullScale):
#        self._fullScale = fullScale
#        self.dig.channelInputConfig(channel, fullScale, self._impedance, self._coupling)        
#        
#    def do_set_impedance(self, channel, impedance):
#        self._impedance = impedance
#        self.dig.channelInputConfig(channel, self._fullScale, impedance, self._coupling)
#        
#    def do_set_coupling(self, channel, coupling):
#        self._coupling = coupling
#        self.dig.channelInputConfig(channel, self._fullScale, self._impedance, coupling)
#        
#    def do_get_prescaler(self, channel):
#        return self.dig.channelPrescaler(channel)
#        
#    def do_get_fullScale(self, channel):
#        return self.dig.channelFullScale(channel)
#        
#    def do_get_impedance(self, channel):
#        return self.dig.channelImpedance(channel)
#        
#    def do_get_coupling(self, channel):
#        return self.dig.channelCoupling(channel)
    
    def do_get_nsamples(self):
        return self._nsamples
        
    def do_set_nsamples(self, nsamples):
        self._nsamples = nsamples
        
    def do_get_naverages(self):
        return self._naverages
        
    def do_set_naverages(self, naverages):
        self._naverages = naverages
        
    def do_get_main_channel(self):
        return self._main_channel
        
    def do_set_main_channel(self, channel):
        self._main_channel = channel
        
    def do_get_ref_channel(self):
        return self._ref_channel
        
    def do_set_ref_channel(self, channel):
        self._ref_channel = channel
        
    def do_get_main_delay(self):
        return self._main_delay
        
    def do_set_main_delay(self, delay):
        self._main_delay = delay
        
    def do_get_ref_delay(self):
        return self._ref_delay
        
    def do_set_ref_delay(self, delay):
        self._ref_delay = delay
        
    def do_get_if_period(self):
        return self._if_period
    
    def do_set_if_period(self, if_period):
        self._if_period = if_period

    ###############################################
    # Acquizition Methods
    ###############################################

    def arm(self):
        self.dig.DAQstartMultiple(15)

#    def setup_shots(self, N):
#        self.dig.channelInputConfig(self._main_channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
#        self.dig.channelInputConfig(self._ref_channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
#        
#        self.dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
#        
#        self.dig.DAQdigitalTriggerConfig(self._main_channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
#        self.dig.DAQdigitalTriggerConfig(self._ref_channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
#
#        self.dig.DAQconfig(self._main_channel, self._nsamples, N, self._main_delay, key.SD_TriggerModes.EXTTRIG)
#        self.dig.DAQconfig(self._ref_channel, self._nsamples, N, self._ref_delay, key.SD_TriggerModes.EXTTRIG)
#    
#    def take_shots(self, N):
#        signal = np.zeros((N, self._nsamples))
#        ref = np.zeros_like(signal)
#        for i in range(N):
#            signal[i] = self.dig.DAQread(self._main_channel, self._nsamples, self._timeout)
#            ref[i] = self.dig.DAQread(self._ref_channel, self._nsamples, self._timeout)
#        return signal, ref

    def setup_avg_shot(self):
        self.dig.channelInputConfig(self._main_channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
        self.dig.channelInputConfig(self._ref_channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
        
        self.dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
        
        self.dig.DAQdigitalTriggerConfig(self._main_channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
        self.dig.DAQdigitalTriggerConfig(self._ref_channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)

        self.dig.DAQconfig(self._main_channel, self._nsamples, self._naverages, self._main_delay, key.SD_TriggerModes.EXTTRIG)
        self.dig.DAQconfig(self._ref_channel, self._nsamples, self._naverages, self._ref_delay, key.SD_TriggerModes.EXTTRIG)
        
        self.set_demod(avg_periods=1)

    def take_avg_shot(self, acqtimeout=None):
        signal = np.zeros((self._naverages, self._nsamples), dtype = np.complex64)
        ref = np.zeros_like(signal)
        for i in range(self._naverages):
            try:
                signal[i] = self.dig.DAQread(self._main_channel, self._nsamples, self._timeout)
                ref[i] = self.dig.DAQread(self._ref_channel, self._nsamples, self._timeout)
            except ValueError, e:
                print(str(e))
                print('digitizer is likely not getting triggered')
                raise ValueError
                    
        self._demodA.demodulate(signal.reshape(self._naverages * self._nsamples))
        IQA = self._demodA.IQ.reshape([self._naverages, self._nsamples / self._if_period])
#        IQA = self._demodA.IQ

        # Calculate reference angles
        self._demodB.demodulate(ref.reshape(self._naverages * self._nsamples))
        IQB = self._demodB.IQ.reshape([self._naverages, self._nsamples / self._if_period])
#        IQB = self._demodB.IQ
        refs = np.exp(-1j * np.angle(np.average(IQB, 1)))
        avg = np.zeros_like(IQA[0,:])
        for i in range(self._naverages):
            avg += IQA[i,:] * refs[i]
            
        return avg/self._naverages
        
    def setup_experiment(self, num_points):
        self._num_points = num_points
        self.dig.channelInputConfig(self._main_channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
        self.dig.channelInputConfig(self._ref_channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
        
        self.dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
        
        self.dig.DAQdigitalTriggerConfig(self._main_channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
        self.dig.DAQdigitalTriggerConfig(self._ref_channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)

        self.dig.DAQconfig(self._main_channel, self._nsamples, self._naverages * num_points, self._main_delay, key.SD_TriggerModes.EXTTRIG)
        self.dig.DAQconfig(self._ref_channel, self._nsamples, self._naverages * num_points, self._ref_delay, key.SD_TriggerModes.EXTTRIG)
        
        self.set_demod(avg_periods=1, bufsize = self._nsamples * num_points)
        
    def take_experiment(self):
        signal = np.zeros((self._num_points, self._nsamples), dtype = np.complex64)
        ref = np.zeros_like(signal)
        avgs = np.zeros(self._num_points, dtype = np.complex64)
        for i in range(self._naverages):
            for j in range(self._num_points):
                try:
                    signal[j] = self.dig.DAQread(self._main_channel, self._nsamples, self._timeout)
                    ref[j] = self.dig.DAQread(self._ref_channel, self._nsamples, self._timeout)
                except ValueError, e:
                    print(str(e))
                    print('digitizer is likely not getting triggered')
                    raise ValueError
                        
            self._demodA.demodulate(signal.reshape(self._num_points * self._nsamples))
            IQA = self._demodA.IQ.reshape([self._num_points, self._nsamples / self._if_period])
    
            # Calculate reference angles
            self._demodB.demodulate(ref.reshape(self._num_points * self._nsamples))
            IQB = self._demodB.IQ.reshape([self._num_points, self._nsamples / self._if_period])
            refs = np.exp(-1j * np.angle(np.average(IQB, 1)))
            
            for j in range(self._num_points):
                avgs[j] += np.mean(IQA[j,:] * refs[j])
            
        return avgs/self._naverages
    
    
    
    def setup_demod_shots(self, N):
        self.setup_avg_shots(N)

    def take_demod_shots(self, acqtimeout=None, Iweight=None, Qweight=None):
        #TODO
        return 0
    
    ###############################################
    # Demodulation stuff
    ###############################################
    
    def set_demod(self, avg_periods=1, weight_func=1, bufsize=None):
        '''
        Sets up demodulators.
        <avg_periods> only applies to channel B (the reference), as we might
        want to use weight functions to the corrected shots.
        '''

        if bufsize is None:
            bufsize = self._nsamples * self._naverages

        # Default is no weighting function.
        self._Iweight = None
        self._Qweight = None

#        weight_func = self.load_weight_func(self.get_weight_func())
#        if type(weight_func) is np.ndarray:
#            if weight_func.dtype in (np.complex, np.complex64, np.complex128):
#                self._Iweight = np.real(weight_func)
#                self._Qweight = np.imag(weight_func)
#            else:
#                self._Iweight = weight_func
#                self._Qweight = weight_func

        self._demodA = demod.DemodulatorComplex(bufsize, self._if_period, avg_periods=1)
        self._demodB = demod.DemodulatorComplex(bufsize, self._if_period, avg_periods=avg_periods)

        # Garbage collect old demodulators
        gc.collect()