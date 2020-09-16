# -*- coding: utf-8 -*-
"""
Created on Fri Jul 03 10:31:22 2020

@author: wanglab
"""

import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
import os
import lmfit
os.chdir(r'c:\qrlab')

alz = mclient.instruments['alazar']
gaius01 = mclient.instruments['gaius01']
coolgen= mclient.instruments['cool']
ZZ = mclient.instruments['ZZ']

qubits = mclient.get_qubits()
#qubit_info = mclient.get_qubit_info('qubit1ge')
#qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
#qubit2_info = mclient.get_qubit_info('qubit2ge')
#qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')

gate_info1 = mclient.get_gate_info('sq_gate1')
gate_info2 = mclient.get_gate_info('sq_gate2')
cancel_info = mclient.get_gate_info('cancel_gate')
#zx90_info = mclient.get_gate_info('zx90_gate')
cx_info = mclient.get_gate_info('cx_gate')
ZZ_info = mclient.get_gate_info('ZZ_gate')



from scripts.single_qubit import ssbspec
from scripts.single_qubit import rabi

cool = sequencer.Constant(int(4e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

def RB_fit(Pg_cplx, xs,  label='', F_final=0.5, F_init=1.0, fig=None):    #fitting the averaged data of this run
    average_data= np.real(np.mean(Pg_cplx, axis=0))
    std = np.std(np.real(Pg_cplx), axis = 0)

    ys  = average_data
    err = std/np.sqrt(len(Pg_cplx))

    def exp_decay(params, x, data):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return (data-est)

    def exp_decay2(params, x):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return est

    params=lmfit.Parameters()
    params.add('amplitude', value=F_init-F_final, vary=True)
    params.add('ofs', value=F_final, vary=False)
    params.add('tau', value=len(xs))
    result= lmfit.minimize(exp_decay, params, args=(xs,ys))
    lmfit.report_fit(result.params)
    EPC = (1-F_final-(1-F_final)*np.exp(-1.0/result.params['tau']))
    print ("EPC: %f" %(EPC))
    label = label+"EPC: %.3f" %(EPC)

    if fig==None:
        fig, ax=plt.subplots(1)
    else:
        ax = fig.axes[0]
    ax.plot(xs, exp_decay2(result.params,xs), markersize =4)
    ax.errorbar(xs,ys,err, markersize=2, linestyle='None', capsize=2, color='black')
    ax.plot(xs,ys, 'o', markersize=3, linestyle='None', label=label)#color='magenta')
#    ax.plot(xs,np.transpose(np.real(np.mean(Pg_cplx, axis=0))), '.', markersize=3, linestyle='None')

    ax.set_ylabel('Average fidelity')
    ax.set_xlabel('Number of Cliffords')
    fig.axes[0].legend(loc=0)
    
    return fig


#    """Power Rabi -- Pi pulse calibration"""
if 0: # Calibrate pi pulse
    from scripts.single_qubit import rabi
#    for x in np.linspace(7.54741e9,7.54770e9,30):
#    for cool_time in [0.00001e3, 5e3, 10e3, 50e3, 100e3]:
#        cool = sequencer.Constant(int(cool_time),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), qubit_info.rotate(np.pi,0)])
                #            for coolamp in [0.05, 0.1, 0.3, 0.8]:
        
        #    postseq = sequencer.Join((ef_info.rotate(np.pi, 0), sequencer.Delay(20000)))
        #        for power in [-5]:
        #            cool_gaius.set_power(po wer)
        #        for cool_time in [0,2e3,10e3,20e3]:
#        tr = rabi.Rabi(qubit2_info, np.linspace(-0.55, 0.55, 71), selective=False,
#            #                   np.linspace(0.75, 0.95, 101), selective=False,
#            #                           np.linspace(-0.2, 0.2, 61), selective=True,
#                               plot_seqs=False, generate=True, repeat_pulse=1,
#                               update=True, seq=None,
#                               postseq=None, proj_func='phase')
#        data=tr.measure()
#        RObrick.do_set_frequency(x)
#        refbrick.do_set_frequency(x+50e6)
#    cool = sequencer.Constant(int(200e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(200)])
    for i in range(1):
        cool = sequencer.Constant(int(4e3),1,chan='3m1')
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150),qubit_info.rotate(np.pi,0)])
#    for i in range(1): 
#        M =np.empty(3)
#        WF_xxx.set_rf_on(0)
#        for wf_power in np.linspace(-5.35408,-5.45,1):
#            WF_xxx.set_power(wf_power)
#            for wf_freq in np.linspace(7.904615e9,7.90461e9,1):
#                WF_xxx.set_frequency(wf_freq)
        tr = rabi.Rabi(qubit2_info, np.linspace(-0.2, 0.2, 61), selective=False,
                #                   np.linspace(0.75, 0.95, 101), selective=False,
                #                           np.linspace(-0.2, 0.2, 61), selective=True,
                                   plot_seqs=False, generate=True, repeat_pulse=1,  #n=3 has a bug
                                   update=True, seq=seq,
                                   postseq=None, proj_func='phase',extra_info=qubit_info)
        data=tr.measure()
#                amp=tr.fit_params['amp'].value
#                K=[]
#                K.append(wf_power)
#                K.append(wf_freq)
#                K.append(amp)
#                K=np.array(K)
#                M = np.vstack((M,K))
#                time.sleep(1)
#                plt.close('all')
    
    bla   










if 0: #Check coherence
    from scripts.single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(gate_info1, np.linspace(10, 2e3, 81), detune=2e6, plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()
    t2 = T2measurement.T2Measurement(gate_info2, np.linspace(10, 2e3, 81), detune=2e6,  plot_seqs = False, generate=True,
                                     proj_func='phase', seq=seq_cool)
    t2.measure()




if 0: # Drag test
    from scripts.single_qubit import drag_test
    dtest = drag_test.drag_test(gate_info1, np.linspace(-0.5,1, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
    bla

if 0: 
    from scripts.single_qubit import Pi_train
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) #gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    p = Pi_train.Pi_train(gate_info1, np.linspace(0.0735, 0.0755, 61), seq=seq_cool, postseq=None, repeat_pulse=5, proj_func='phase',
                          extra_info=gate_info1
                          )
    p.measure()
    bla

if 0: 
    from scripts.single_qubit import Pi2_train
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    p = Pi2_train.Pi2_train(gate_info1, np.linspace(0.036, 0.038, 61), seq=seq_cool, postseq=None, repeat_pulse=10, proj_func='phase',
#                            extra_info=gate_info1
                            )
    p.measure()
    bla
    
if 0: # AllXY 
    from scripts.single_qubit import allxy
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    alz.set_naverages(10000)
    allxy_result =[]
    axy = allxy.All_XY(gate_info1, seq=seq_cool, generate=True, proj_func='phase', postseq = None)#, extra_info=gate_info1)  #seq=seq was added
    axy.measure()
    allxy_result = axy.get_ys()
    plt.plot(allxy_result)
    alz.set_naverages(5000)
    bla


#if 0: # AllXY - interleaved (regular or compensated single qubit drive)
#    from scripts.fluxonium import allxy_interleaved
#    cool = sequencer.Constant(int(8e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
#    
##    allxy_result = np.zeros((N, 42))
#    alz.set_naverages(10000)
##    seq = sequencer.Sequence([sequencer.Trigger(250), qubit_info.rotate(-np.pi/2, 0)]) #this whole line was added
#    allxy_result =[]
#    axy = allxy_interleaved.All_XY_interleaved(qubit_info, qubit2_info, qubit2_info,rel_amp=-0.45, rel_angle=0.4*np.pi, qubit2_rotation=0, qubit2_angle =np.pi, seq=seq, generate=True, proj_func='phase')  #seq=seq was added
#    axy.measure()
#    #        allxy_result[i,:] = axy.get_ys()
#    allxy_result = axy.get_ys()
#    plt.plot(allxy_result)
##    plt.figure()
###    for i in range(N):
##        plt.plot(allxy_result[i,:])
#    alz.set_naverages(8000)
#    bla



#if 0: # Randomized benchmarking
#    from scripts.fluxonium import randbench
#    rndmben_result = []
#    cool = sequencer.Constant(int(8e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), 
##                          qubit2_info.rotate(np.pi2,0)
#                          ])
#    postseq=qubit2_info.rotate(np.pi,0)
#
#    alz.set_naverages(5000)
#    for i in range(3):
#        rndmben = randbench.rndm(qubit_info, num_cal_points=3, n_gates_start=1, n_gates_stop=81, n_gates_step=3, seq=seq, postseq=None, generate=True, proj_func='phase', extra_info=qubit2_info) #seq=seq added
#        rndmben.measure()
#        rndmben_result.append(rndmben.get_ys())
#        rndmben_complex_result.append(rndmben.avg_data)
#
##        plt.close()
##        plt.figure()
##        plt.plot(rndmben.xs, rndmben.get_ys())#, linestyle=None)
##    print rndmben_result
##    bla

if 0: # Randomized benchmarking joint
    from scripts.fluxonium import randbench_jointRO
    rndmben_result = []
    Pg_cplx = []
    
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    alz.set_naverages(5000)
    for M in [[gate_info1, gate_info2], [gate_info2, gate_info1]]:
        for i in range(5):
            rndmben = randbench_jointRO.rndm(M[0], M[1], num_cal_points=3, n_gates_start=1, n_gates_stop=81, n_gates_step=3, seq=seq, postseq=None, generate=True, proj_func='phase') #seq=seq added
            rndmben.measure()
            rndmben_result.append(rndmben.get_ys())
            Pg_cplx.append(rndmben.Pg_cplx)
    
        tempxs = rndmben.xs[48:]  #change this 
        xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]
        RB_fit(Pg_cplx, xs, F_final=0.5)
        
    
if 0: # Randomized benchmarking joint interleaved two qubits
    from scripts.fluxonium import randbench_jointRO_interleaved
    rndmben_result = []
    Pg_cplx = []

    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    alz.set_naverages(5000)
    for M in [[gate_info1, gate_info2], [gate_info2, gate_info1]]:
        for i in range(3):
            rndmben = randbench_jointRO_interleaved.Interleaved_1QRB(M[0], M[1], num_cal_points=3, n_gates_start=1, n_gates_stop=25, n_gates_step=1, seq=seq, postseq=None, generate=True, proj_func='phase') #seq=seq added
            rndmben.measure()
            rndmben_result.append(rndmben.get_ys())
            Pg_cplx.append(rndmben.Pg_cplx)
        tempxs = rndmben.xs[48:]  #change this 
        xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0] *2 #Each gate is actually 2 Cliffords, one on each qubit
        RB_fit(Pg_cplx, xs, F_final=0.25)
  

if 1: # Two-Qubit Randomized Benchmarking  
    from scripts.fluxonium import TwoQ_RB 
    from scripts.fluxonium  import timerabi_interleaved
    rndmben_result0 = []
    Pg_cplx0 = []
    rndmben_result1 = []
    Pg_cplx1 = []
    
#    alz.set_naverages(8000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2)
    Y_proj = gate_info1.rotate(np.pi/2, 0)

    for i in range(10):
        alz.set_naverages(5000)
        rndmben0 = TwoQ_RB.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=7, 
                                      plot_seqs=False, category='all', generator='CZ',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True,
                                      singleQ_phases=[-2.627,-1.372+np.pi], seq=seq, proj_func='phase')
        data0 = rndmben0.measure()
        rndmben_result0.append(rndmben0.get_ys())
        Pg_cplx0.append(rndmben0.Pgg)
##
#        rndmben = TwoQ_RB.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=7, 
#                                      plot_seqs=False, category='all', generator='CZ', interleave='CZ',
#                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, 
#                                      singleQ_phases=[-2.627,-1.372+np.pi], seq=seq, proj_func='phase')
#        data = rndmben.measure()
#        rndmben_result1.append(rndmben.get_ys())
#        Pg_cplx1.append(rndmben.Pgg)
        
#        if i%2 == 0:
#            alz.set_naverages(2000)       
#            tr = timerabi_interleaved.TimeRabi_interleaved(cx_info, gate_info2, np.linspace(0, 600, 101), 
#                        amp=0.0766, phase=0, rel_amp=4.433, rel_phase=0.993, sigma=6, read_on_e=True, cancel_info=cancel_info, 
#                        update=False, seq=seq, postseq=X_proj, proj_func='phase', plot_seqs=False, extra_info=gate_info1)
#            data = tr.measure()            
#        if i%4 == 0:
#            tr = timerabi_interleaved.TimeRabi_interleaved(cx_info, gate_info2, np.linspace(0, 600, 101), 
#                        amp=0.0766, phase=0, rel_amp=4.433, rel_phase=0.993, sigma=6, read_on_e=True, cancel_info=cancel_info, 
#                        update=False, seq=seq, postseq=Y_proj, proj_func='phase', plot_seqs=False, extra_info=gate_info1)
#            data = tr.measure()            


    tempxs = rndmben0.xs[48:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx0, xs, F_final=0.25, F_init=1-0.1)
    plt.figure()
#    tempxs = rndmben.xs[48:]  #change this 
#    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
#    RB_fit(Pg_cplx1, xs, F_final=0.25, F_init=1-0.35)

    
#    tempxs = rndmben0.xs[48:]  #change this 
#    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]
#    RB_fit(RBdata, xs, F_final=0.25, F_init=1-0.09)
#    plt.title('2-qubit randomized benchmarking')

#    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0] 
#    RB_fit(IRBdata, xs, F_final=0.25, F_init=1-0.115)
#    plt.title('2-qubit CX-interleaved randomized benchmarking')
    
#    rndmben_result1_old = rndmben_result1[:]
#    rndmben_result0_old = rndmben_result0[:]
#    Pg_cplx1_old = Pg_cplx1[:]
#    Pg_cplx0_old = Pg_cplx0[:]













if 0: # Simultaneous 1qubit gate RB
    from scripts.fluxonium import TwoQ_RB 
    rndmben_result1 = []
    Pgg = []
    Pg1 = []
    Pg2 = []
    alz.set_naverages(8000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    for i in range(5):
        rndmben = TwoQ_RB.TwoQubit_RB(gate_info2, gate_info1, cx_info, cancel_info, num_cal_points=3, N_cliffords=30, 
                                      plot_seqs=False, category='single', generator='CZ',# interleave='CX',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, seq=seq, proj_func='phase')
        data = rndmben.measure()
        rndmben_result1.append(rndmben.get_ys())
        Pgg.append(rndmben.Pgg)
        Pg1.append(rndmben.Pg1)
        Pg2.append(rndmben.Pg2)
    tempxs = rndmben.xs[48:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]
    RBfig = RB_fit(Pgg, xs, F_final=0.25, F_init=1, label='Fidelity of |gg>,  total ')
    plt.title('Simultaneous 1Q randomized benchmarking',fontsize=12)
    RB_fit(Pg2, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit1, ', fig=RBfig)
    RB_fit(Pg1, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit2, ', fig=RBfig)


if 0: # Interleaved two-Qubit Randomized Benchmarking 
    from scripts.fluxonium import TwoQ_RB 
    rndmben_result = []
    Pg_cplx = []
    alz.set_naverages(8000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    for i in range(5):
        rndmben = TwoQ_RB.TwoQubit_RB(gate_info2, gate_info1, cx_info, cancel_info, num_cal_points=3, N_cliffords=40, 
                                      plot_seqs=False, category='single', generator='CX', interleave='I',
                                      find_cheapest_recovery=False, seq=seq, proj_func='phase')
        data = rndmben.measure()
        rndmben_result.append(rndmben.get_ys())
        Pg_cplx.append(rndmben.Pg_cplx)
    tempxs = rndmben.xs[48:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]+1 #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx, xs, F_final=0.25, F_init=1)
    plt.title('Simultaneous 1Q-gates randomized benchmarking')
    
'''
if 0: # Two-Qubit Randomized Benchmarking with the echo scheme
    from scripts.fluxonium import TwoQ_RB_echo
    rndmben_result2 = []
    Pg_cplx2 = []
    alz.set_naverages(8000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    for i in range(5):
        rndmben = TwoQ_RB_echo.TwoQubit_RB(gate_info2, gate_info1, zx90_info, num_cal_points=3, N_cliffords=30, 
                                      plot_seqs=False, category='single', generator = 'ZX90', #interleave='I',
                                      find_cheapest_recovery=False, seq=seq, proj_func='phase')
        data = rndmben.measure()
        rndmben_result2.append(rndmben.get_ys())
        Pg_cplx2.append(rndmben.Pg_cplx)
    tempxs = rndmben.xs[48:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]+1 #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx2, xs, F_final=0.25, F_init=1) #For interleaved RB, accounting for 1Q recovery error 2.1%
    
#if 0: # Two-Qubit Randomized Benchmarking
#    from scripts.fluxonium import TwoQ_RB_interleaved
#    rndmben_result2 = []
#    Pg_cplx2 = []
#    alz.set_naverages(8000)
#    cool = sequencer.Constant(int(4e3),1,chan='3m1')
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
#
#    for i in range(3):
#        rndmben = TwoQ_RB_interleaved.TwoQubit_RB(gate_info2, gate_info1, cnot_info, cancel_info, num_cal_points=3, N_cliffords=8, 
#                                      plot_seqs=False, category='all', generator = 'ZX90',
#                                      find_cheapest_recovery=False, seq=seq, proj_func='phase')
#        data = rndmben.measure()
#        rndmben_result2.append(rndmben.get_ys())
#        Pg_cplx2.append(rndmben.Pg_cplx)
#    tempxs = rndmben.xs[48:]  #change this 
#    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]+1 #Each gate is actually 2 Cliffords, one on each qubit
#    RB_fit(Pg_cplx2, xs, F_final=0.25)
'''