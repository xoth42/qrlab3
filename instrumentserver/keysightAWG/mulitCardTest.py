import keysightSD1 as key
import numpy as np



AWG_PRODUCT = "M3202A"
CHASSIS = 0
AWG1_SLOT = 5
AWG2_SLOT = 10


trigger_data = np.concatenate((np.ones(10), np.zeros(90)))
trigger = key.SD_Wave()
trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)


for slot in [AWG1_SLOT]:
    
    error = []
    awg = key.SD_AOU()
    aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, slot)
    
    # Gather Information about AWG S/N, Slot and S/N
    AWGPart = awg.getProductNameBySlot(CHASSIS, slot)
    AWGNumber = awg.getSerialNumberBySlot(CHASSIS, slot)
    print("Part =", AWGPart)
    print("S/N =", AWGNumber)
    
    error += [awg.AWGstopMultiple(15)]
    error += [awg.waveformFlush()]
    
    error += [awg.waveformLoad(trigger, 0)]

    error += [awg.AWGflush(1)]
    
    error += [awg.channelWaveShape(1, key.SD_Waveshapes.AOU_AWG)]
    
    error += [awg.AWGqueueWaveform(1, 0, key.SD_TriggerModes.AUTOTRIG, 0, 1, 0)]
    
    error += [awg.AWGqueueConfig(1,1)]

    error += [awg.AWGstartMultiple(15)]
    error += [awg.AWGtriggerMultiple(15)]

    print(error)

