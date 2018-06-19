# -*- coding: utf-8 -*-
#Script by Josh to investigate the correlation between both T1 and FT1
#6/18/18
import numpy as np
import os
import csv
from itertools import chain
data_location = 'C:\\Users\\wanglab\\Desktop\\t1tf1'
overnight_run = 'C:\\Users\\wanglab\\Desktop\\t1ft1\\0324-0325 overnight run\\processed_results\\100 shot data_IQ.txt'
data = []

f = open(overnight_run, 'rb')
reader = csv.reader(f)
l_f = list(reader)
data.append(l_f)
f.close()

data = np.asarray(data)
data.flatten()
data = data[0]

def noise_average(array):
    av = np.average(array)
    noise_array = array - av
    def magnitude(s):
        return np.math.sqrt((s.real)**2 + (s.imag)**2)
    magnitude = np.vectorize(magnitude)
    def square(s):
        return s**2
    square = np.vectorize(square)
    return np.average(square(magnitude(noise_array)))


results = np.core.defchararray.replace(data, '+ -' , '-')
results = np.core.defchararray.replace(results, '+  -', '-')
for _ in range(0, 10):
    results = np.core.defchararray.replace(results, " ", '')
complex = np.vectorize(complex)
results = complex(results)
g = results[:,0]
equator = results[:,1]
t1 = results[:,2]
ft1 = results[:,3]
print noise_average(equator)
print noise_average(t1)
print noise_average(ft1)



