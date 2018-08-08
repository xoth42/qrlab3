import keysightSD1 as key
import numpy as np

import matplotlib.pyplot as plt

testing_HVI_location = r'C:\qrlab\instrumentserver\keysightAWG\digitizer test\AWG_trigger_testing.HVI'
class CompiledHVI(object):
    def __init__(self, HVI_path_str, *args, **kwargs):
        self.hvi = key.SD_HVI()
        self.identifier = self.hvi.open(HVI_path_str)
        self.error(self.identifier)
        self.loading = key.SD_HVI.load(self.identifier)
        self.error(self.loading)
    def error(self, value):
        if value < 0:
            raise ValueError('HVI error ' + str(value))
    def start(self):
        result = key.SD_HVI.start(self.identifier)
        self.err(result)
    def pause(self):
        result = key.SD_HVI.pause(self.identifier)
        self.error(result)
    def resume(self):
        result = key.SD_HVI.resume(self.identifier)
        self.error(result)
    def stop(self):
        result = key.SD_HVI.stop(self.identifier)
        self.error(result)
        
test_instance = CompiledHVI(testing_HVI_location)
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

SECONDARY_AWG_PRODUCT = 'M3202A'
SECONDARY_CHASSIS = 0
SECONDARY_AWG_SLOT = 10

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

secondary_awg = key.SD_AOU()
opening_result = secondary_awg.openWithSlot(SECONDARY_AWG_PRODUCT,
                                            SECONDARY_CHASSIS,
                                            SECONDARY_AWG_SLOT)
check_error(opening_result)


# Make a new Gaussian with tunable parameters, so that it can be changed if
# necessary.
def Gaussian(x, sigma, mu):
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(
        -((x - mu) ** 2) / (2 * sigma) ** 2)


# sample the above function to create the actual array of values.
new_wave = [Gaussian(x, 10, 10) for x in np.linspace(-100, 100, 10000)]
new_wave = np.asarray(new_wave)
new_wave = new_wave * (1 / max(new_wave))
# dig = key.SD_AIN()
# ainID = dig.openWithSlot(DIG_PRODUCT, CHASSIS, DIG_SLOT)
#
# DIGPart = dig.getProductNameBySlot(CHASSIS, DIG_SLOT)
# DIGNumber = dig.getSerialNumberBySlot(CHASSIS,DIG_SLOT)
# DIGNumModules = dig.moduleCount()
# print("Part =", DIGPart)
# print("S/N =", DIGNumber)
# print("Number of Modules = ", DIGNumModules)

# Check AWG Connection
# if aouID < 0:
#    print("ERROR")
#    print("aouID:", aouID)
#    awg.close()
#    print()
#    print("AOU closed")


# Load waveforms to AWG
waveform_filepath = "C:\\qrlab\instrumentserver\keysightAWG\waveforms\\"
# print(waveform_filepath)


# gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)

# Change out the Gaussian in the saved file for the one above. Doesn't make
# much of a difference.
gaussian = new_wave
gaussian = np.asarray(gaussian)
pulse_length = len(gaussian)

# Make a whole series of Gaussian waves, each bigger than the last.
gaussian_waves = [gaussian * i for i in np.linspace(0.6, 1, 10)]

wait_time = 100

full_length = pulse_length + wait_time

awg.waveformFlush()
secondary_awg.waveformFlush()

# Load the seconday AWG with the trigger pulses and nothing else.

trigger = key.SD_Wave()
trigger_data = np.concatenate((np.ones(10), np.zeros(full_length - 10)))
trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
result = secondary_awg.waveformLoad(trigger, 0)
check_error(result)

secondary_awg.AWGflush(1)
secondary_awg.AWGflush(2)
secondary_awg.AWGflush(3)
secondary_awg.AWGflush(4)

secondary_awg.channelWaveShape(1, key.SD_Waveshapes.AOU_AWG)
secondary_awg.channelWaveShape(2, key.SD_Waveshapes.AOU_AWG)
secondary_awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)
secondary_awg.channelWaveShape(4, key.SD_Waveshapes.AOU_AWG)

secondary_awg.channelAmplitude(1, 1)
secondary_awg.channelAmplitude(2, 1)
secondary_awg.channelAmplitude(3, 1)
secondary_awg.channelAmplitude(4, 1)

# Setup the queue in cyclic mode
secondary_awg.AWGqueueConfig(1, 1)
secondary_awg.AWGqueueConfig(2, 1)
secondary_awg.AWGqueueConfig(3, 1)
secondary_awg.AWGqueueConfig(4, 1)

# Load the trigger into the secondary AWG.

for i in [1, 2, 3, 4]:
    result = secondary_awg.AWGqueueWaveform(i, 0, key.SD_TriggerModes.SWHVITRIG,
                                            0, 1, 0)
    check_error(result)
pause = key.SD_Wave()
pause.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, np.zeros(wait_time))
##awg.waveformLoad(pause, 1)

# gaussian = np.concatenate((gaussian, np.zeros(wait_time)))
# wave = key.SD_Wave()
# wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian)


wave_list = []
for w in gaussian_waves:
    temp = key.SD_Wave()
    result = temp.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, w)
    check_error(result)
    wave_list.append(trigger)
    # wave_list.append(pause)
    wave_list.append(temp)
# awg.waveformLoad(wave, 2)
# wave_list.insert(0, trigger)
wave_number = 0
for index, w in enumerate(wave_list):
    temp = awg.waveformLoad(w, index)
    check_error(temp)
    wave_number += 1

# Clear Channels
awg.AWGflush(1)
awg.AWGflush(2)
awg.AWGflush(3)
awg.AWGflush(4)


awg.channelWaveShape(1, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(2, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(4, key.SD_Waveshapes.AOU_AWG)

awg.channelAmplitude(1, 1)
awg.channelAmplitude(2, 1)
awg.channelAmplitude(3, 1)
awg.channelAmplitude(4, 1)

# Setup the queue in cyclic mode
awg.AWGqueueConfig(1, 1)
awg.AWGqueueConfig(2, 1)
awg.AWGqueueConfig(3, 1)
awg.AWGqueueConfig(4, 1)

# pause at start
for i in [1, 2, 3, 4]:
    for k in range(0, wave_number):
        result = awg.AWGqueueWaveform(i, k, key.SD_TriggerModes.SWHVITRIG, 0, 1,
                                      0)
        check_error(result)
#    awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
#    awg.AWGqueueWaveform(3, 2, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
#    awg.AWGqueueWaveform(4, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)


# set up full scale, input impedance and AC/DC coupling for Digitizer channels
Voltage_Scale = 2.8  # Scale > 3 saturates the Digitizer input and folds the waveform causing unwanted wave shape
# dig.channelInputConfig(1 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
# dig.channelInputConfig(2 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
# dig.channelInputConfig(3 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
# dig.channelInputConfig(4 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)

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


##SET UP EXTERNAL DIGITAL TRIGGER
# PROGRAM Trig IN/Out as INPUT PORT - def triggerIOconfig(self, direction
# dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
# EXTERNAL DIGITAL TRIGGER BEHAVIOR - def DAQdigitalTriggerConfig(self, channel, triggerSource, triggerBehavior)
# dig.DAQdigitalTriggerConfig(1,
# key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
# dig.DAQdigitalTriggerConfig(2, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
# dig.DAQdigitalTriggerConfig(3, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
# dig.DAQdigitalTriggerConfig(4, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)


# CONFIGURE DAQ3 FOR CAPTURING RABI SWEEP - DAQconfig(self, nDAQ, nDAQpointsPerCycle, nCycles, prescaler, triggerMode)


num_ave = 1
num_aq = 1000
timeout = 2000
# dig.DAQconfig(1, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)
# dig.DAQconfig(2, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)
# dig.DAQconfig(3, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)
# dig.DAQconfig(4, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)


# dig.DAQstart(1)
# dig.DAQstartMultiple(15)

# map(check_error, results)
awg.AWGstartMultiple(15)
secondary_awg.AWGstartMultiple(15)
# awg.AWGtriggerMultiple(15)


samp_array = np.zeros((4, num_aq))
plt.figure()
plt.plot(new_wave, 'bo')
# READ DAQ BUFFER FOR ACQUIRED DATA
# samp_array[0] = dig.DAQread(1, num_aq, timeout)
# samp_array[1] = dig.DAQread(2, num_aq, timeout)
# samp_array[2] = dig.DAQread(3, num_aq, timeout)
# samp_array[3] = dig.DAQread(4, num_aq, timeout)


# plt.plot(samp_array[0], label = 'chanel 1')
# plt.plot(samp_array[1], label = 'chanel 2')
# plt.plot(samp_array[2], label = 'chanel 3')
# plt.plot(samp_array[3], label = 'chanel 4')
#
# plt.legend()
# plt.show()

# STOP DIG
# dig.DAQstopMultiple(15)
# awg.AWGstopMultiple(15)

#
