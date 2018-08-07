import h5py
import numpy as np
import matplotlib.pyplot as plt
def vectorize_dec(function):
    def wrapper():
        return np.vectorize(function)
    return wrapper
def project(c1, c2, c3):
    pass



file_path = r'C:\Users\Wang_Lab\Desktop\TunableTransmonJuly18.hdf5'
file = h5py.File(file_path, 'r')
if len(file.keys()) == 0:
    raise ValueError('No keys')
correlation_day = file['20180731']
good_keys = correlation_day.keys()
data_I = np.asarray([0, 0, 0])

data_II = np.asarray([0, 0, 0])
for key in good_keys:
    if 'avg' not in correlation_day[key]:
        continue
    if key[-2:] not in ['II', 'tI']:
        continue
    if key[-2:] == 'tI':
        data_I = np.vstack((data_I, correlation_day[key]['avg']))
    if key[-2:] == 'II':
        data_II = np.vstack((data_II, correlation_day[key]['avg']))

equator = data_I[:, 0]
t1 = data_I[:, 1]
g = data_I[:, 2]

g_2 = data_II[:, 0]
ft1 = data_II[:, 1]
f = data_II[:, 2]
        
