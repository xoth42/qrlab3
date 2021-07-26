import keysightSD1 as key
import numpy as np
import matplotlib.pyplot as plt





AWG_PRODUCT = "M3202A"
CHASSIS = 1
AWG_SLOT = 7

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
print(("Part =", AWGPart))
print(("S/N =", AWGNumber))
print(("Number of Modules = ", AWGNumModules))


dig = key.SD_AIN()
ainID = dig.openWithSlot(DIG_PRODUCT, CHASSIS, DIG_SLOT)

DIGPart = dig.getProductNameBySlot(CHASSIS, DIG_SLOT)
DIGNumber = dig.getSerialNumberBySlot(CHASSIS,DIG_SLOT)
DIGNumModules = dig.moduleCount()
print(("Part =", DIGPart))
print(("S/N =", DIGNumber))
print(("Number of Modules = ", DIGNumModules))

# Check AWG Connection
if aouID < 0:
    print("ERROR")
    print(("aouID:", aouID))
    awg.close()
    print()
    print("AOU closed")




# Load waveforms to AWG
waveform_filepath = "C:\\qrlab-3\instrumentserver\keysightAWG\waveforms\\"

print(waveform_filepath)


gaussian = np.loadtxt(waveform_filepath + 'Gaussian.csv', skiprows = 3)
pulse_length = len(gaussian)

wait_time = 0

num_points = 10
power = np.linspace(.1, 1, num_points)

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
for i in range(num_points):
    wave = key.SD_Wave()
    wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian*power[i])
    awg.waveformLoad(wave, i + 2)
    


# Clear Channels
awg.AWGflush(2)
awg.AWGflush(3)

# Setup Sinusoid
awg.channelWaveShape(2, key.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(2, 0)
awg.channelFrequency(2, 1e8)

awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)

awg.channelAmplitude(2, 0)
awg.channelAmplitude(3, 2)

awg.modulationAmplitudeConfig(2, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)

# Setup the queue in cyclic mode
awg.AWGqueueConfig(2,1)
awg.AWGqueueConfig(3,1)

print(('cyclic modes', awg.AWGqueueConfigRead(1), awg.AWGqueueConfigRead(1)))

#pause at start
awg.AWGqueueWaveform(2, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(3, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)


# Setup Envelopes
for i in range(num_points):
    awg.AWGqueueWaveform(2, i + 2, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
    # Setup outgoing trigger
    awg.AWGqueueWaveform(3, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)



#set up full scale, input impedance and AC/DC coupling for Digitizer channels
Voltage_Scale = 2.8 # Scale > 3 saturates the Digitizer input and folds the waveform causing unwanted wave shape
dig.channelInputConfig(1 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)

dig.channelInputConfig(2 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)

# Check DIG Connection
if ainID < 0:
    print("ERROR")
    print(("ainID:", ainID))

    awg.close()
    print()
    print("AIN closed")

data_filepath = "C:\\qrlab-3\instrumentserver\keysightAWG\data\\"
print(data_filepath)

#intitialize Digitizer

dig.DAQflush(3)
dig.DAQflush(2)


##SET UP EXTERNAL DIGITAL TRIGGER
#PROGRAM Trig IN/Out as INPUT PORT - def triggerIOconfig(self, direction
dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
#EXTERNAL DIGITAL TRIGGER BEHAVIOR - def DAQdigitalTriggerConfig(self, channel, triggerSource, triggerBehavior)

dig.DAQdigitalTriggerConfig(3, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 
#CONFIGURE DAQ3 FOR CAPTURING RABI SWEEP - DAQconfig(self, nDAQ, nDAQpointsPerCycle, nCycles, prescaler, triggerMode)


num_ave = 2000
num_aq = 5000
timeout = 2000
dig.DAQconfig(3, num_aq, num_ave * num_points, 0, key.SD_TriggerModes.EXTTRIG)


dig.DAQstart(3)
awg.AWGstartMultiple(15)



voltage_array = np.zeros((num_points, num_aq))
#READ DAQ BUFFER FOR ACQUIRED DATA
for i in range(num_ave * num_points):

    if(i % (num_ave * num_points/10) == 0): 
        print(i)
    samp_array = dig.DAQread(3, num_aq, timeout) #def DAQread(self, nDAQ, nPoints, timeOut = 0)
    voltage_array[i%num_points] += samp_array*Voltage_Scale/num_ave

#STOP DIG
dig.DAQstop(3)
dig.DAQstop(2)

plot_array = []
#PLOT THE ACQUIRED DATA
voltage_max = np.max(voltage_array)
for n in range(num_points):
    voltage_array[n] /=  voltage_max
    plot_array.extend(voltage_array[n][120:160])
    print((np.max(voltage_array[n][120:160])))
#    plt.plot(voltage_array[i])
#    plt.xlabel('Sample')
#    plt.ylabel('Voltage')
#    plt.show()
#    
plt.clf()
    
plt.plot(plot_array)
plt.xlabel('Sample')
plt.ylabel('Voltage')
plt.show()




