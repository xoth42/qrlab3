import plotconfig

datadir = r'c:\_Data'
tempfilename = r'c:\_data\temp.h5'
ins_store_fn = r'c:\_data\ins_settings.set'
filename = 'c:/_data/150109 Cooldown/blah.hdf5'

# Use AWG bulk waveform/sequence loading if available.
# Should be faster but apparently isn't always.
awg_bulkload = False
awg_fileload = False
dot_awg_path = 'Z:\\_AWG\\ECS\\123.awg'

# Force generation of these channels even if no sequence present
required_channels = (1, 2, 3, 4)

slave_triggers = (('4m1', 475),)
# marker delay

master_awg = 'AWG1'
slave_awgs = ['AWG2']


