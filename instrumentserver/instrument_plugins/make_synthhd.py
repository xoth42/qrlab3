from windfreak import SynthHD

if 0: #initialization
    synth = SynthHD('COM3')
    #synth.init()

# Set channel 0 power and frequency
#ch = synth[0]

#print(ch.power)



#synth[0].power =0.
#synth[0].frequency = 1000.
# Enable channel 0 output
'''print(synth[0].pa_enable)
synth[0].pa_enable=True
synth[0].pll_enable=True
synth[0].rf_enable=True'''
#print(synth[0].power)
#x.rf_enable(False)
#print(synth[0].frequency_range)
#synth.reference_mode = 'external'
#synth.reference_frequency = 10000000
synth[0].enable=True
#synth[0].pll_enable=False
print(synth.reference_mode)
print(synth.reference_frequency)


#synth.init()
