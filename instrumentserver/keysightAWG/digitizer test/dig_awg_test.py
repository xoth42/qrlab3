import keysightSD1 as key
import numpy as np
import matplotlib.pyplot as plt
from CompiledHVI import CompiledHVI

#Decorator that checks the return result from all of the keysight function, to
#make sure there isn't any errors.

#trigger_period = 200
#testing_HVI_location = r'C:\qrlab\instrumentserver\instrument_plugins\HVI\\' + '3slot' + str(trigger_period) + 'us.HVI'
#
#test_instance = CompiledHVI(testing_HVI_location)
#test_instance.assignHardware(0, 0, 7)
        
#hvi=key.SD_HVI()
#hvi.open(testing_HVI_location)
#hvi.assignHardwareWithIndexAndSlot(0,0,7)
#hvi.compile()
#hvi.load()
# The AWG will return integers after almost every operation. If that integer
# is less than zero, the function in question will have silently failed. This
#  function can catch that error and cause an explicit exception to be clear
# that something failed.
def check_error(err):
    if err < 0:
        raise ValueError('error is ' + str(err))


AWG_PRODUCT = "M3202A"
CHASSIS = 0
AWG_SLOT = 7

# The secondary AWG will produce triggers for the primary AWG and the digitizer,
# so that both will be in sync.


DIG_PRODUCT = "M3102A"
CHASSIS = 0
DIG_SLOT = 3

awg = key.SD_AOU()

aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)

# Gather Information about AWG S/N, Slot and S/N
AWGPart = awg.getProductNameBySlot(CHASSIS, AWG_SLOT)
AWGNumber = awg.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
AWGNumModules = awg.moduleCount()
print("Part =", AWGPart)
print("S/N =", AWGNumber)
print("Number of Modules = ", AWGNumModules)


# Make a new Gaussian with tunable parameters, so that it can be changed if
# necessary.
#def Gaussian(x, sigma, mu):
#    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(
#        -((x - mu) ** 2) / (2 * sigma) ** 2)


# sample the above function to create the actual array of values.
#new_wave = [Gaussian(x, 10, 10) for x in np.linspace(-100, 100, 400)]
#new_wave = np.asarray(new_wave)
#new_wave = new_wave * (1 / max(new_wave))
dig = key.SD_AIN()
ainID = dig.openWithSlot(DIG_PRODUCT, CHASSIS, DIG_SLOT)

DIGPart = dig.getProductNameBySlot(CHASSIS, DIG_SLOT)
DIGNumber = dig.getSerialNumberBySlot(CHASSIS,DIG_SLOT)
DIGNumModules = dig.moduleCount()
print("Part =", DIGPart)
print("S/N =", DIGNumber)
print("Number of Modules = ", DIGNumModules)

# Check AWG Connection
# if aouID < 0:
#    print("ERROR")
#    print("aouID:", aouID)
#    awg.close()
#    print()
#    print("AOU closed")


# Load waveforms to AWG
#waveform_filepath = "C:\\qrlab\instrumentserver\keysightAWG\waveforms\\"
# print(waveform_filepath)


# gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)

# Change out the Gaussian in the saved file for the one above. Doesn't make
# much of a difference.
#gaussian = new_wave
#gaussian = np.asarray(gaussian)
#pulse_length = len(gaussian)

# Make a whole series of Gaussian waves, each bigger than the last.
#gaussian_waves = [gaussian * i for i in np.linspace(0.4, 1, 4)]

awg.waveformFlush()

# Load the seconday AWG with the trigger pulses and nothing else.

wave1 = key.SD_Wave()
data1 = np.loadtxt('waveform1.txt')
wave1.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, data1)
awg.waveformLoad(wave1, 1)


wave2 = key.SD_Wave()
data2 = np.loadtxt('waveform2.txt')
data2[-1] = 0
wave2.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, data2)
awg.waveformLoad(wave2, 2)


trigger = key.SD_Wave()
trigger_data = np.concatenate((np.ones(100), np.zeros(int(len(data1) + len(data2))-100)))
trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
awg.waveformLoad(trigger, 0)




# Load the trigger into the secondary AWG.

#pause = key.SD_Wave()
#pause.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, np.zeros(wait_time))
##awg.waveformLoad(pause, 1)

# gaussian = np.concatenate((gaussian, np.zeros(wait_time)))
# wave = key.SD_Wave()
# wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian)



#wave_list = []
#wave_list.append(trigger)
#for w in gaussian_waves:
#    temp = key.SD_Wave()
#    result = temp.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, w)
#    check_error(result)
#    wave_list.append(temp)
# wave_list.insert(0, trigger)
#wave_number = len(wave_list)
#for index, w in enumerate(wave_list):
#    temp = awg.waveformLoad(w, index)
#    check_error(temp)

# Setup Channels
for i in range(1, 5):
    awg.AWGflush(i)
    awg.channelWaveShape(i, key.SD_Waveshapes.AOU_AWG)
    awg.channelAmplitude(i, 1)
    # Setup the queue in cyclic mode
    awg.AWGqueueConfig(i, 1)

# load triggers onto channels 3 and 4
awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)


awg.AWGqueueWaveform(3, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(3, 2, key.SD_TriggerModes.AUTOTRIG, 0, 1, 0)
# load data onto channels 1 and 2
#for i in [1, 2]: 
#    for k in range(1, wave_number):
#        result = awg.AWGqueueWaveform(i, k, key.SD_TriggerModes.SWHVITRIG, 0, 1,
#                                      0)
#        check_error(result)
#    awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
#    awg.AWGqueueWaveform(3, 2, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
#    awg.AWGqueueWaveform(4, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)


# set up full scale, input impedance and AC/DC coupling for Digitizer channels
VOLTAGE_SCALE = 2.8  # Scale > 3 saturates the Digitizer input and folds the waveform causing unwanted wave shape
#dig.channelInputConfig(1 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
#dig.channelInputConfig(2 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
#dig.channelInputConfig(3 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)

# Check DIG Connection
# if ainID < 0:
#    print("ERROR")
#    print("ainID:", ainID)
#    print()
#    print("AIN closed")

data_filepath = "C:\\qrlab\instrumentserver\keysightAWG\data\\"
print(data_filepath)

# intitialize Digitizer
# dig.DAQflushMultiple(15)



naverages = 1
nsamples = int(2e3)
timeout = 2000
channel = 4

##SET UP EXTERNAL DIGITAL TRIGGER
# PROGRAM Trig IN/Out as INPUT PORT - def triggerIOconfig(self, direction
        
# EXTERNAL DIGITAL TRIGGER BEHAVIOR - def DAQdigitalTriggerConfig(self, channel, triggerSource, triggerBehavior)
# dig.DAQdigitalTriggerConfig(1,
# key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
# dig.DAQdigitalTriggerConfig(2, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
# dig.DAQdigitalTriggerConfig(3, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
errors = []
errors += [dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)]
errors += [dig.DAQtriggerExternalConfig(channel, key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
                                        key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)]
errors += [dig.DAQflush(channel)]
errors += [dig.channelInputConfig(channel, VOLTAGE_SCALE, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)]
errors += [dig.DAQconfig(channel, nsamples, naverages, 0, 2)]
errors += [dig.DAQbufferPoolConfig(channel, nsamples * naverages, 100)]
print(errors)
# CONFIGURE DAQ3 FOR CAPTURING RABI SWEEP - DAQconfig(self, nDAQ, nDAQpointsPerCycle, nCycles, prescaler, triggerMode)





dig.DAQstart(channel)
#dig.DAQstartMultiple(15)

# map(check_error, results)
#test_instance.start()
awg.AWGstartMultiple(15)
awg.AWGtriggerMultiple(15)


# READ DAQ BUFFER FOR ACQUIRED DATA
# samp_array[0] = dig.DAQread(1, num_aq, timeout)
# samp_array[1] = dig.DAQread(2, num_aq, timeout)
# samp_array[2] = dig.DAQread(3, num_aq, timeout)
samp_array = dig.DAQbufferGet(channel)
samp_array = np.array(samp_array, dtype = float)
samp_array /= np.max(samp_array)

plt.plot(np.arange(0, len(samp_array)*2, 2), samp_array, label = 'chanel 1')
plt.plot(np.arange(0, len(samp_array)*2, 2), samp_array, '.')
plt.plot(np.concatenate((data1, data2)))
# plt.plot(samp_array[1], label = 'chanel 2')
# plt.plot(samp_array[2], label = 'chanel 3')
# plt.plot(samp_array[3], label = 'chanel 4')
#
# plt.legend()
# plt.show()

# STOP DIG
dig.DAQstopMultiple(15)
awg.AWGstopMultiple(15)
dig.DAQbufferPoolRelease(channel)
#
