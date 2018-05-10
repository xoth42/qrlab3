import keysightSD1 as key
import numpy as np
import matplotlib.pyplot as plt





AWG_PRODUCT = "M3202A"
CHASSIS = 0
AWG_SLOT = 4

DIG_PRODUCT = "M3102A"
CHASSIS = 0
DIG_SLOT = 3

# CREATE AND OPEN MODULES
awg = key.SD_AOU()
aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)

# Gather Information about AWG S/N, Slot and S/N
AWGPart = awg.getProductNameBySlot(CHASSIS, AWG_SLOT)
AWGNumber = awg.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
AWGNumModules = awg.moduleCount()
print("Part =", AWGPart)
print("S/N =", AWGNumber)
print("Number of Modules = ", AWGNumModules)


dig = key.SD_AIN()
ainID = dig.openWithSlot(DIG_PRODUCT, CHASSIS, DIG_SLOT)

DIGPart = dig.getProductNameBySlot(CHASSIS, DIG_SLOT)
DIGNumber = dig.getSerialNumberBySlot(CHASSIS,DIG_SLOT)
DIGNumModules = dig.moduleCount()
print("Part =", DIGPart)
print("S/N =", DIGNumber)
print("Number of Modules = ", DIGNumModules)

# Check AWG Connection
if aouID < 0:
    print("ERROR")
    print("aouID:", aouID)
    awg.close()
    print()
    print("AOU closed")




# Load waveforms to AWG
waveform_filepath = "C:\\qrlab\instrumentserver\keysightAWG\waveforms\\"
#print(waveform_filepath)


gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)
pulse_length = len(gaussian)

wait_time = 0

full_length = pulse_length + wait_time


awg.waveformFlush()

# Load the trigger
trigger = key.SD_Wave()
trigger_data = np.concatenate((np.ones(10), np.zeros(full_length-10)))
trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
awg.waveformLoad(trigger, 0)

pause = key.SD_Wave()
pause.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, np.zeros(wait_time))
awg.waveformLoad(pause, 1)

gaussian = np.concatenate((gaussian, np.zeros(wait_time)))
# Load the rabi pulses
wave = key.SD_Wave()
wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian)
awg.waveformLoad(wave, 2)
    


# Clear Channels
awg.AWGflush(1)
awg.AWGflush(2)
awg.AWGflush(3)
awg.AWGflush(4)

awg.channelWaveShape(1, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(2, key.SD_Waveshapes.AOU_AWG)
awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)

awg.channelAmplitude(1, 1)
awg.channelAmplitude(2, 1)
awg.channelAmplitude(3, 1)



# Setup the queue in cyclic mode
awg.AWGqueueConfig(1,1)
awg.AWGqueueConfig(2,1)
awg.AWGqueueConfig(3,1)

#pause at start
awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(2, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(3, 2, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)




#set up full scale, input impedance and AC/DC coupling for Digitizer channels
Voltage_Scale = 2.8 # Scale > 3 saturates the Digitizer input and folds the waveform causing unwanted wave shape
dig.channelInputConfig(1 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
dig.channelInputConfig(2 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
dig.channelInputConfig(3 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
dig.channelInputConfig(4 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)

# Check DIG Connection
if ainID < 0:
    print("ERROR")
    print("ainID:", ainID)
    print()
    print("AIN closed")

data_filepath = "C:\\qrlab\instrumentserver\keysightAWG\data\\"
print(data_filepath)

#intitialize Digitizer
dig.DAQflushMultiple(15)


##SET UP EXTERNAL DIGITAL TRIGGER
#PROGRAM Trig IN/Out as INPUT PORT - def triggerIOconfig(self, direction
dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
#EXTERNAL DIGITAL TRIGGER BEHAVIOR - def DAQdigitalTriggerConfig(self, channel, triggerSource, triggerBehavior)
dig.DAQdigitalTriggerConfig(1, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
dig.DAQdigitalTriggerConfig(2, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 
dig.DAQdigitalTriggerConfig(3, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 
dig.DAQdigitalTriggerConfig(4, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 


#CONFIGURE DAQ3 FOR CAPTURING RABI SWEEP - DAQconfig(self, nDAQ, nDAQpointsPerCycle, nCycles, prescaler, triggerMode)


num_ave = 1
num_aq = 1000
timeout = 2000
dig.DAQconfig(1, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)
dig.DAQconfig(2, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)
dig.DAQconfig(3, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)
dig.DAQconfig(4, num_aq, num_ave, 0, key.SD_TriggerModes.EXTTRIG)


#dig.DAQstart(1)
dig.DAQstartMultiple(15)
awg.AWGstartMultiple(15)
#awg.AWGtriggerMultiple(15)



samp_array = np.zeros((4, num_aq))
#READ DAQ BUFFER FOR ACQUIRED DATA
samp_array[0] = dig.DAQread(1, num_aq, timeout)
samp_array[1] = dig.DAQread(2, num_aq, timeout)
samp_array[2] = dig.DAQread(3, num_aq, timeout)
samp_array[3] = dig.DAQread(4, num_aq, timeout)


plt.plot(samp_array[0], label = 'chanel 1')
plt.plot(samp_array[1], label = 'chanel 2')
plt.plot(samp_array[2], label = 'chanel 3')
plt.plot(samp_array[3], label = 'chanel 4')

plt.legend()
plt.show()
plt.clf()

#STOP DIG
dig.DAQstopMultiple(15)
#awg.AWGstopMultiple(15)

#    





