from scipy.signal import savgol_filter
from scipy.integrate import simps
import random

AWG1 = instruments.create('AWG1', 'Tektronix_AWG5014C', address='TCPIP0::172.30.56.25::inst0::INSTR', clock=1e9, refsrc='EXT', reffreq=10e6)

sn = instruments.create('sn',
        "SignalHoundSM200A",
        speed='auto',
        center=1e8,
        span=1e4,
        vbw=300,
        rbw=300,
        ref=10,
        spur=False)
a, b = sn.sweep()
import matplotlib.pyplot as plt


time_choice = [i for i in range(0, 16)]
data = []
size = 20
wave = 'sine4'   
chan = '4'
points = 2
data = [[] for _ in range(0, size)]
choices = []


def dB_to_power(x):
    return 10**(x/10.0)
def moving_window(x, window_length):
    for i in range(window_length, len(x) - window_length):
        x[i] = numpy.average(x[i - window_length:i + window_length])
    return x
for k in range(0, size):
    
    print 'SIGNAL OFF'
    AWG1.all_off()
    time.sleep(2)       
    avg_power = []
    for _ in range(0, 5):
        freq, log_powers = sn.sweep()
   #     powers = [power[i] + abs(min(power)) for i in power]
        avg_power.append(log_powers)
    avg_power = numpy.asarray(avg_power)
    avg_waveform = avg_power.mean(axis = 0)
    baseline_in_W = map(dB_to_power, avg_waveform)
    integrated_averaged_baseline = simps(baseline_in_W)
    print 'ON SIGNAL ' + str(k)
    wait_time = random.choice(time_choice)
    time.sleep(wait_time)
    choices.append(wait_time)
    AWG1.all_on()
    
    print "BEGINNING"
    
    fig_prefix = "C:\\Users\\wanglab\\Desktop\\AWG_tests\\"
    new_direc = fig_prefix + 'run_' + str(k)
    os.mkdir(new_direc)
    for i in range(0, points):
        sweep_waveforms = []
        for _ in range(0, 100):
            a, b = sn.sweep()
            sweep_waveforms.append(b)
        waveform = numpy.mean(sweep_waveforms, axis = 0)
      #  raised_b = [b[i] + abs(min(b)) for i in b]
        actual_power = map(dB_to_power, waveform)      
        integrated_power = simps(actual_power)
        plt.plot(a, waveform)
        plt.grid()
        plt.title('AWG run sine plot # ' + str(i))
        corrected_power = abs(integrated_power) - abs(integrated_averaged_baseline)
        plt.legend([str(corrected_power)])
        plt.savefig(new_direc + '\\' + str(i) + '_' + str(time.time()) + '.png', format = 'png' )
        plt.close()

        data[k].append(corrected_power)
        time.sleep(0.5)
import csv
with open(fig_prefix + 'data.csv', 'wb') as myfile:
    wr = csv.writer(myfile)
    wr.writerows(data)
def nice_plot(data, wave, chan):
    for i in range(0, len(data)):
        plt.figure()
        plt.scatter(range(0, len(data[i])), data[i])
        plt.xlabel('t (~s)')
        plt.ylabel('dBm')
        plt.grid()
        plt.title('Run ' +str(wave) +   ' points: ' + str(points) + ' plot ' + str(i) + ' on channel ' + str(chan))
        analysis_direc = 'C:\\Users\\wanglab\\Desktop\\AWG_analysis\\'
        plt.savefig(analysis_direc + str(i) + '.png', format = 'png')
        plt.close()
        plt.figure()
        plt.hist(data[i], bins = 'auto')
        plt.title('Histogram of run: ' + str(i) + ' on wave ' + str(wave) + ' with chan ' + str(chan))
        plt.grid()
        plt.savefig(analysis_direc + '_hist_' + str(i))
    
       # plt.show()

nice_plot(data, wave, chan)
plt.figure()
for i in sweep_waveforms:
    plt.plot(i)
    
plt.plot(waveform, 'k*')
#plt.plot(waveform_, 'b*')
plt.grid()
plt.show()

#plt.close('all')
import csv
#import numpy as np
#f_4 = open('C:\\Users\\wanglab\\Desktop\\results\\chan_3_\\AWG_tests\\data.csv', 'rb')
#reader_4 = csv.reader(f_4)
#data_4_large = list(reader_4)
#data_4 = np.asarray(data_4_large, dtype = np.float)
#
#
#f_3 = open('C:\\Users\\wanglab\\Desktop\\results\\channel_3_A\\AWG_tests\\data.csv', 'rb')
#reader_3 = csv.reader(f_3)
#data_3_large = list(reader_3)
#data_3 = np.asarray(data_3_large, dtype= np.float)
#def linear(x, a, b):
#    return a*x + b
#from scipy.optimize import curve_fit
#params, cov = curve_fit(linear, range(0, len(data_4[4])), list(data_4[4]))
#def linear(x, a, b):
#    return a*x + b
#from scipy.optimize import curve_fit
#def find_start_position(data):
#    params, cov = curve_fit(linear, range(0, len(data)), data)
#    return params[1]
#intercepts = map(find_start_position, data)

size = 20
wave = 'sine4'
chan = '4'
points = 2
import numpy as np
import csv
f = open(r'C:\Users\wanglab\Desktop\AWG_tests\data.csv', 'rb')
r = csv.reader(f)
g = list(r)
data = np.asarray(g, dtype=np.float)



import matplotlib.pyplot as plt
intercepts = [i[0] for i in data]
plt.close('all')
plt.figure()
plt.plot(intercepts, 'bo')
plt.title('Randomized off times amplitude starting points for ' + wave + ' on channel ' + chan)
plt.grid()
plt.plot(choices, 'r*')
plt.show()
plt.close('all')


figure, axis1 = plt.subplots()
axis1.plot(intercepts, 'bo')
axis1.set_ylabel('amplitudes', color='b')
axis1.tick_params('y', colors = 'b')
ax2 = axis1.twinx()
ax2.plot(choices, 'r*')
ax2.set_ylabel('off times', color = 'r')
ax2.tick_params('y', colors = 'r')
figure.tight_layout()
plt.grid()
plt.show()
              
              

#
#