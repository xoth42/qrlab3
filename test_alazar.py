import matplotlib.pyplot as plt
import numpy as np
import time
from lib.math import demod


def moving_average(a, n=20) :
    ret = np.cumsum(a)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

## Setup alazar according to settings in GUI


import mclient
alz = mclient.instruments['alazar']
#mclient.instruments.reload('alazar')
#alz = mclient.instruments['alazar']
#alz.set_ch1_range('100mV')
#alz.set_ch2_range('100mV')
#alz.set_nsamples(4800)
#alz.set_naverages(2000)
#alz.set_ch1_coupling('AC')
#alz.set_ch2_coupling('AC')
#alz.set_clock_source('EXT10M')
#alz.set_sample_rate('1GEXT10')
#alz.set_engJ_trig_src('EXT')
#alz.set_engJ_trig_lvl(128+5)
#alz.set_real_signals(False)
#alz.setup_channels()
#alz.setup_trigger()


if 1:
        start_time = time.time()
        alz.setup_shots(1)
        end_time = time.time()
        buf = alz.take_raw_shots()
        plt.figure()
        nsamp = alz.get_nsamples()
        plt.plot(buf[:nsamp], label='A')
        plt.plot(buf[nsamp:2*nsamp], label='B')
#        plt.plot(buf)
        plt.suptitle('Raw single shot')
        plt.legend()
        plt.xlabel('Time [ns]')
        plt.show()
#        print alz.get_ch1_range()

    
#alz.set_naverages(5)

''' This script was to test direct output of AWG channel '''
if 0:
    for i in range(1):
        amplitude=[]
        I=[]
        Q=[]
        for k in range(200):
            alz.setup_avg_shot(1000)
            buf = alz.take_avg_shot(timeout=50000)
    #        alz.setup_shots(1)
    #        buf = alz.take_demod_shots()
    #        buf2 = moving_average(buf)
            amplitude.append(np.sum(np.abs(buf)))
            I.append(np.sum(np.real(buf)))
            Q.append(np.sum(np.imag(buf)))
            time.sleep(0.5)
            print "k=", k, ", amplitude=", amplitude[-1], "\n"
            plt.figure(i+1)
            plt.clf()
            plt.subplot(311)
            plt.plot(amplitude)
            plt.subplot(312)
            plt.plot(I)
            plt.subplot(313)
            plt.plot(Q)
            
if 0:        
        alz.setup_shots(1)
        buf = alz.take_demod_shots()
#        buf2 = moving_average(buf)
        amp = np.abs(buf)
        plt.figure()
        plt.suptitle('Demodulated single shot')
    
        plt.subplot(211)
        plt.plot(np.real(buf[0]), label='Iraw')
        plt.plot(np.imag(buf[0]), label='Qraw ')
        plt.plot(np.abs(buf[0]),label='amplitude')
#        plt.plot(np.real(buf2), label='IMA')
#        plt.plot(np.imag(buf2), label='QMA ')

        plt.xlabel('IF period #')
        plt.legend()
    
        plt.subplot(212)
        plt.plot(np.real(buf[0]), np.imag(buf[0]), label='IQraw')
#        plt.plot(np.real(buf2), np.imag(buf2), label='IQMA')
        plt.xlabel('I')
        plt.ylabel('Q')
        plt.legend()
        plt.show()
        

if 0:
        alz.setup_avg_shot(5000)
        buf = alz.take_avg_shot(timeout=50000)
    
        print('plotting')
        plt.figure()
        plt.suptitle('Average demodulated shot')
    
        plt.subplot(211)
        plt.plot(np.real(buf))
        plt.plot(np.imag(buf))
        plt.plot(np.abs(buf))
        plt.xlabel('IF period #')
    
        plt.subplot(212)
        plt.plot(np.real(buf), np.imag(buf))
        plt.xlabel('I')
        plt.ylabel('Q')
        plt.show()
        
#        plt.figure()
#        plt.plot(np.angle(buf, deg=True))
        
if 0:
      for i in range(1):  
        N = 1000
        alz.setup_shots(N)
        nsamp = alz.get_nsamples()
        buf = alz.take_raw_shots()
        demodA = demod.DemodulatorComplex(nsamp*N, 20, avg_periods=1)
        demodA.demodulate(buf[:N*nsamp])
        IQA = demodA.IQ.reshape([N, nsamp/20])
        signal = np.average(IQA, 1)
        phase = np.angle(signal, deg=True)
    
        demodB = demod.DemodulatorComplex(nsamp*N, 20, avg_periods=1)
        demodB.demodulate(buf[N*nsamp:])
        IQB = demodB.IQ.reshape([N, nsamp/20])
        signalB = np.average(IQB, 1)
        phaseB = np.angle(signalB, deg=True)
        
        print(np.average(phase), np.average(phaseB), np.average(phase-phaseB))
    
        plt.figure()
        
        plt.subplot(311)       
        plt.plot(np.abs(signal), label='amp')
        plt.plot(np.abs(signalB), label='ampB')
        plt.legend()
        
        plt.subplot(312)
        plt.plot(phase, label='phase')
        plt.plot(phaseB, label='phaseB')
        plt.legend()
        
        plt.subplot(313)
        plt.plot(phase - phaseB, label='phase delta')
#        plt.plot(buf)
        plt.suptitle('Raw single shots')
        plt.legend()
        plt.xlabel('Shots')
        plt.show()
        
        
if 0:
        n = 500
        N = 1000 
        avg_phaseA = np.zeros(n)
        avg_phaseB = np.zeros(n)
        start_time = time.time()
        print(start_time)
        for i in range(n):
            current_time = time.time()
            print(i, current_time - start_time)
            alz.setup_shots(N)
            nsamp = alz.get_nsamples()
            buf = alz.take_raw_shots()
            demodA = demod.DemodulatorComplex(nsamp*N, 20, avg_periods=1)
            demodA.demodulate(buf[:N*nsamp])
            IQA = demodA.IQ.reshape([N, nsamp/20])
            signal = np.average(IQA, 1)
            phase = np.angle(signal, deg=True)
        
            demodB = demod.DemodulatorComplex(nsamp*N, 20, avg_periods=1)
            demodB.demodulate(buf[N*nsamp:])
            IQB = demodB.IQ.reshape([N, nsamp/20])
            signalB = np.average(IQB, 1)
            phaseB = np.angle(signalB, deg=True)
            
            print(np.average(phase), np.average(phaseB), np.average(phase-phaseB))
            
            avg_phaseA[i] = np.average(phase)
            avg_phaseB[i] = np.average(phaseB)
        
        plt.figure()
        
        plt.subplot(311)       
        plt.plot(avg_phaseA, label='average phase A')
        plt.legend()
#        plt.plot(np.abs(signal), label='amp')
#        plt.plot(np.abs(signalB), label='ampB')
        
        plt.subplot(312)
        plt.plot(avg_phaseB, label='average phase B')
        plt.legend()
#        plt.plot(phase, label='phase')
#        plt.plot(phaseB, label='phaseB')
#        plt.plot(buf)
        plt.subplot(313)
        plt.plot(avg_phaseA - avg_phaseB, label='phase delta')
        plt.suptitle('Raw averaged shots')
        plt.legend()
        plt.xlabel('Shots (x' + str(N) + ')')
        plt.show()
