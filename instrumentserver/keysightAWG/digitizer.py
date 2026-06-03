from instrumentserver.keysightAWG import keysightSD1 as key

AWG_PRODUCT = "M3202A"
DIG_PRODUCT = "M3102A"
CHASSIS = 1
AWG_SLOT = 7
DIG_SLOT = 8


# CREATE AND OPEN MODULES
awg = key.SD_AOU()
aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)
dig = key.SD_AIN()
digID = dig.openWithSlot(DIG_PRODUCT, CHASSIS, DIG_SLOT)


# Gather Information about AWG S/N, Slot and S/N
AWGPart = awg.getProductNameBySlot(CHASSIS, AWG_SLOT)
AWGNumber = awg.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
AWGNumModules = awg.moduleCount()
print(("Part =", AWGPart))
print(("S/N =", AWGNumber))
print(("Number of Modules = ", AWGNumModules))

DigPart = dig.getProductNameBySlot(CHASSIS, DIG_SLOT)
DigNumber = dig.getSerialNumberBySlot(CHASSIS, DIG_SLOT)
DIGNumModules = dig.moduleCount()
print(("Part =", DigPart))
print(("S/N =", DigNumber))
print(("Number of Modules = ", DIGNumModules))


# Check AWG Connection
if aouID < 0 or digID < 0:
    print("ERROR")
    print(("aouID:", aouID))
    print(("digID:", digID))
    awg.close()
    dig.close()


# Load waveforms to AWG
waveform_filepath = "C:\\qrlab-3\instrumentserver\keysightAWG\waveforms\\"
print(waveform_filepath)
gaussian = key.SD_Wave()
gaussian.newFromFile(waveform_filepath + 'Readout.csv')

trigger = key.SD_Wave()
trigger.newFromFile(waveform_filepath + 'Trigger.csv')


awg.waveformFlush()
awg.waveformLoad(gaussian, 0)
awg.waveformLoad(trigger, 1)


# Clear Channel 1
awg.AWGflush(1)
awg.AWGflush(2)

# Setup Sinusoid
#awg.channelWaveShape(1, key.SD_Waveshapes.AOU_SINUSOIDAL)
#awg.channelAmplitude(1, .0001)
#awg.channelFrequency(1, 1e8)
awg.channelWaveShape(1, key.SD_Waveshapes.AOU_DC)
awg.channelAmplitude(1, 0)


awg.channelWaveShape(2, key.SD_Waveshapes.AOU_DC)
awg.channelAmplitude(2, 0)


awg.channelPhase(1, 0.0)
awg.channelPhase(2, 0.0)
awg.channelPhaseResetMultiple(3)

# Setup Envelope
awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
awg.AWGqueueWaveform(2, 1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
for i in range(0):
    awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.AUTOTRIG, 0, 1, 0)
    awg.AWGqueueWaveform(2, 1, key.SD_TriggerModes.AUTOTRIG, 0, 1, 0)


# Modulate the sinusoid and the envelope
#awg.modulationAmplitudeConfig(1, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)
awg.AWGqueueConfig(1, 1)

#awg.modulationAmplitudeConfig(2, key.SD_ModulationTypes.AOU_MOD_AM, 1.5)
awg.AWGqueueConfig(2, 1)

#dig.DAQflush(1)
#dig.channelInputConfig(1, 1, 50, key.AIN_Coupling.AIN_COUPLING_AC)
#dig.DAQconfig(1, 100, -1, 0, key.SD_AIN_TriggerMode.RISING_EDGE)
#dig.DAQstart(1)


awg.AWGstartMultiple(3)
awg.AWGtriggerMultiple(3)



#print(dig.DAQread(1, 100))
