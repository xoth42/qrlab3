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
from CompiledHVI import CompiledHVI


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
        self._trigger_period=100

        self._name = name
        self._chassis = chassis
        self._slot = slot
        self._DIG_PRODUCT = DIG_PRODUCT
        
        self._hvi = None
        self.load_hvi()
        
        


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
        
        self.add_parameter('trigger_period', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=50, maxval=1600, value=self._trigger_period,
                               help='Period for the HVI trigger for measurments')
        
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
    
    def load_hvi(self):
        testing_HVI_location = r'C:\qrlab\instrumentserver\instrument_plugins\HVI\\' + str(self._trigger_period) + 'usTrigger.HVI'
        self._hvi = CompiledHVI(testing_HVI_location)
        self._hvi.stop()
        
    def start_hvi(self):
        self._hvi.start()
        
    def stop_hvi(self):
        self._hvi.stop()

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
        
    def do_get_trigger_period(self):
        return self._trigger_period
    
    def do_set_trigger_period(self, trigger_period):
        self._trigger_period = trigger_period
        self._hvi = self.load_hvi()
        

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

    def setup_avg_shot(self, ntransfers = None):
        if ntransfers is None:
            ntransfers = 1
        
        errors = []
            
        errors += [self.dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)]
        for channel in [self._main_channel, self._ref_channel]:
            errors += [self.dig.DAQtriggerExternalConfig(channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
                                    key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)]
            errors += [self.dig.DAQflush(channel)]
            errors += [self.dig.channelInputConfig(channel, VOLTAGE_SCALE, 
                                                   key.AIN_Impedance.AIN_IMPEDANCE_50, 
                                                   key.AIN_Coupling.AIN_COUPLING_DC)]
            errors += [self.dig.DAQconfig(channel, self._nsamples, self._naverages, 
                                          self._main_delay, key.SD_TriggerModes.EXTTRIG)]
            errors += [self.dig.DAQbufferPoolConfig(channel, self._nsamples * self._naverages / ntransfers, 
                                                    self._timeout)]
            self.set_demod(self._nsamples * self._naverages / ntransfers, avg_periods=1) #TODO: change avg_periods?
        
        if any(error < 0 for error in errors):
            print(errors)


    def take_avg_shot(self, acqtimeout=None):
        signal = np.zeros(self._naverages * self._nsamples, dtype = np.complex64)
        ref = np.zeros_like(signal)
        try:
            signal = self.dig.DAQbufferGet(self._main_channel)
            ref = self.dig.DAQbufferGet(self._ref_channel)
        except ValueError, e:
            print(str(e))
            print('digitizer is likely not getting triggered')
            raise ValueError
            
        if(not len(signal) == self._naverages * self._nsamples):
            print('Buffer gave some wack shit, or maybe no shit at all:')
            print(np.shape(signal), signal)
            print(np.shape(ref), ref)
            raise ValueError
#        self.dig.DAQbufferPoolRelease(self._main_channel)
#        self.dig.DAQbufferPoolRelease(self._ref_channel)
        
        self._demodA.demodulate(signal)
        IQA = self._demodA.IQ.reshape([self._naverages, self._nsamples / self._if_period])
#        IQA = self._demodA.IQ

        # Calculate reference angles
        self._demodB.demodulate(ref)
        IQB = self._demodB.IQ.reshape([self._naverages, self._nsamples / self._if_period])
#        IQB = self._demodB.IQ
        refs = np.exp(-1j * np.angle(np.average(IQB, 1)))
        avg = 0
        for i in range(self._naverages):
            avg += IQA[i,:] * refs[i]
            
        return avg/self._naverages
        
    def setup_experiment(self, num_points, ntransfers = None):
        if ntransfers is None:
            if self._naverages % 10 == 0:
                self._ntransfers = self._naverages/10
            else:
                self._ntransfers = self._naverages
        else:
            self._ntransfers = ntransfers
            
        errors = []    
        
        self._npoints = num_points
        samples_per_transfer = self._naverages *  self._npoints * self._nsamples / self._ntransfers

        errors += [self.dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)]
        for channel in [self._main_channel, self._ref_channel]:
            errors += [self.dig.DAQtriggerExternalConfig(channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
                                    key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)]
            errors += [self.dig.DAQflush(channel)]
            errors += [self.dig.channelInputConfig(channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)]
            errors += [self.dig.DAQconfig(channel, self._nsamples, self._naverages * self._npoints, self._main_delay, key.SD_TriggerModes.EXTTRIG)]
            errors += [self.dig.DAQbufferPoolConfig(channel, samples_per_transfer, self._timeout)]
            self.set_demod(samples_per_transfer, avg_periods= 1) #TODO: change avg_periods?
        
        if any(error < 0 for error in errors):
            print(errors)
        
    def take_experiment(self):
        samples_per_transfer = self._naverages *  self._npoints * self._nsamples / self._ntransfers
        acq_per_transfer = self._naverages *  self._npoints / self._ntransfers
        signal = np.zeros(samples_per_transfer, dtype = np.complex64)
        ref = np.zeros_like(signal)
        avgs = np.zeros(self._npoints, dtype = np.complex64)
        
        for i in range(self._ntransfers):
            if i % np.max([self._ntransfers / 10, 1]) == 0:
                logging.info('Acquiring %d/%d', i, self._ntransfers)
                self.emit('capture-progress', i)
            try:
                signal = self.dig.DAQbufferGet(self._main_channel)
                ref = self.dig.DAQbufferGet(self._ref_channel)
            except ValueError, e:
                print(str(e))
                print('digitizer is likely not getting triggered')
                raise ValueError
                        
            self._demodA.demodulate(signal)
            self._demodB.demodulate(ref)
            
            IQA = self._demodA.IQ.reshape([acq_per_transfer, self._nsamples / self._if_period])
            IQB = self._demodB.IQ.reshape([acq_per_transfer, self._nsamples / self._if_period])
            refs = np.exp(-1j * np.angle(np.average(IQB, 1)))
        
            for j in range(acq_per_transfer):
                avgs[(i * acq_per_transfer + j) / self._naverages] += np.mean(IQA[j,:] * refs[j])
        return avgs/self._naverages
    
    def test_dig(self, nsamples, npoints, naverages, ntransfers, captureDelay = 0, digScale = 2):
        digChannels = [1, 2, 3, 4] 
        errors = []
        errors += [self.dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)]
    
        for i in range(len(digChannels)):   
           errors += [self.dig.DAQtriggerExternalConfig(digChannels[i], key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
                                                key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)]
           errors += [self.dig.DAQflush(digChannels[i])]
           errors += [self.dig.channelInputConfig(digChannels[i], digScale, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)]
           errors += [self.dig.DAQconfig(digChannels[i], nsamples, npoints * naverages, captureDelay, key.SD_TriggerModes.EXTTRIG)]
           errors += [self.dig.DAQbufferPoolConfig(digChannels[i], nsamples * npoints * naverages / ntransfers, 100)]
        print(errors)
        
        assert(naverages % ntransfers == 0)
        self.dig.DAQstartMultiple(3)
    #    hvi.start()
        
        # Add code to either trigger digitizer or wait for first few cycles
        sums = np.zeros((npoints, nsamples), dtype = np.float64)
        sums_ref = np.zeros_like(sums, dtype = np.float64)
           
    #    return data
        averages_per_transfer = naverages / ntransfers
        temp = np.zeros(nsamples*npoints * averages_per_transfer, dtype = np.float64)
        temp_ref = np.zeros_like(temp)
        for transfer in range(ntransfers):
            try:
                if transfer % (ntransfers/10) == 0: 
                    print(str(transfer) + r'/' + str(ntransfers) + ' transfers done')
    
                    gc.collect()
            except:
                pass# modulo shit ain't workin. its ok
            temp = self.dig.DAQbufferGet(self._main_channel)
            temp_ref  = self.dig.DAQbufferGet(self._ref_channel)
            if type(temp) is float and temp < 0:
                print('error thrown with code ', temp)

            samples_per_average = nsamples * npoints
            for i in range(averages_per_transfer):
                for j in range(npoints):
                    sums[j] += temp[i * samples_per_average + j * nsamples : i * samples_per_average + (j+1) * nsamples]
                    sums_ref[j] += temp_ref[i * samples_per_average + j * nsamples : i * samples_per_average + (j+1) * nsamples]
          
        
        for i in range(len(digChannels)):
            self.dig.DAQbufferPoolRelease(digChannels[i])
       
        return sums / naverages, sums_ref / naverages
    
    def setup_demod_shots(self, N):
        self.setup_avg_shots(N)

    def take_demod_shots(self, acqtimeout=None, Iweight=None, Qweight=None):
        #TODO
        return 0
    
    def release_buf(self):
        self.dig.DAQbufferPoolRelease(self._main_channel)
        self.dig.DAQbufferPoolRelease(self._ref_channel)
    
    ###############################################
    # Demodulation stuff
    ###############################################
    
    def set_demod(self, bufsize, avg_periods=1, weight_func=1):
        '''
        Sets up demodulators.
        <avg_periods> only applies to channel B (the reference), as we might
        want to use weight functions to the corrected shots.
        '''

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