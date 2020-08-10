import plotconfig

datadir = r'c:\_Data'
tempfilename = r'c:\_Data\temp.hdf5'
ins_store_fn = r'c:\_Data\ins_settings.set'
filename = 'c:\_Data\blah.hdf5'

# Use AWG bulk waveform/sequence loading if available.
# Should be faster but apparently isn't always.
awg_bulkload = False
awg_fileload = False
dot_awg_path = 'Z:\\_AWG\\123.awg'

# Force generation of these channels even if no sequence present

required_channels = (1, 2, 3, 4, 5, 6, 7, 8,9,10)


#slave_triggers = (('4m1', 475),)
# marker delay

#master_awg = 'AWG1'
#slave_awgs = ['AWG2']


