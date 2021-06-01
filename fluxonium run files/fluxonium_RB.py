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
qubit_info = mclient.get_qubit_info('qubit1ge')
#qubit_info2 = mclient.get_qubit_info('qubit1ge_2')
#qubit2_info = mclient.get_qubit_info('qubit2ge')
#qubit2_info2 = mclient.get_qubit_info('qubit2ge_2')

#gate_info1 = mclient.get_gate_info('sq_gate1')
#gate_info2 = mclient.get_gate_info('sq_gate2')
#cancel_info = mclient.get_gate_info('cancel_gate')
##zx90_info = mclient.get_gate_info('zx90_gate')
#cx_info = mclient.get_gate_info('cx_gate')
#ZZ_info = mclient.get_gate_info('ZZ_gate')
#CZ = mclient.instruments['ZZ_gate']


from scripts.single_qubit import ssbspec
from scripts.single_qubit import rabi

cool = sequencer.Constant(int(4e3),1,chan='3m1')
seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

def RB_fit(Pg_cplx, xs,  label='', F_final=0.5, F_init=1.0, fig=None):    #fitting the averaged data of this run
    average_data= np.real(np.mean(Pg_cplx, axis=0))
    std = np.std(np.real(Pg_cplx), axis = 0)

    ys  = average_data
#    ys = np.real(Pg_cplx)
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
    ax.plot(xs,np.transpose(np.real(np.mean(Pg_cplx, axis=0))), '.', markersize=3, linestyle='None')

    ax.set_ylabel('Average fidelity')
    ax.set_xlabel('Number of Cliffords')
    fig.axes[0].legend(loc=0)
    
    return fig

def XEB_fit(Pg_cplx, xs,  label='', F_final=0.5, F_init=1.0, fig=None):    #fitting the averaged data of this run
#    average_data= np.real(np.mean(Pg_cplx, axis=0))
#    std = np.std(np.real(Pg_cplx), axis = 0)
    ys = np.real(Pg_cplx)
#    ys  = average_data
#    ys = np.real(Pg_cplx)
#    err = std/np.sqrt(len(Pg_cplx))

    def exp_decay(params, x, data):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return (data-est)

    def exp_decay2(params, x):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return est

    params=lmfit.Parameters()
    params.add('amplitude', value=F_init-F_final, vary=True)
    params.add('ofs', value=F_final, vary=True)
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
#    ax.errorbar(xs,ys,err, markersize=2, linestyle='None', capsize=2, color='black')
    ax.plot(xs,ys, 'o', markersize=3, linestyle='None', label=label)#color='magenta')
    ax.plot(xs,np.transpose(np.real(Pg_cplx)), '.', markersize=3, linestyle='None')

    ax.set_ylabel('Average fidelity')
    ax.set_xlabel('Number of Cycles')
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
    dtest = drag_test.drag_test(gate_info2, np.linspace(-1.5,-0.5, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
#    bla

if 0: # Drag test
    from scripts.single_qubit import drag_test
    dtest = drag_test.drag_test(gate_info1, np.linspace(-1, 2, 51), plot_seqs=False, generate=True, proj_func='phase', seq=seq_cool)
    data=dtest.measure()
    bla





if 0: 
    from scripts.single_qubit import Pi_train
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) #gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    p = Pi_train.Pi_train(gate_info1, np.linspace(0.070, 0.08, 61), seq=seq_cool, postseq=None, repeat_pulse=5, proj_func='phase',
                          extra_info=gate_info1
                          )
    p.measure()
    bla

if 0: 
    from scripts.single_qubit import Pi2_train
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    p = Pi2_train.Pi2_train(gate_info1, np.linspace(0.034, 0.040, 61), seq=seq_cool, postseq=None, repeat_pulse=10, proj_func='phase',
#                            extra_info=gate_info1
                            )
    p.measure()
    bla

if 0: 
    from scripts.single_qubit import Pi_train
    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)]) #gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    p = Pi_train.Pi_train(gate_info2, np.linspace(0.31, 0.3225, 61), seq=seq_cool, postseq=None, repeat_pulse=5, proj_func='phase',
                          extra_info=gate_info1
                          )
    p.measure()
    bla

if 1: 
    from scripts.single_qubit import Pi2_train
#    seq_cool = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    cool = sequencer.Constant(int(10e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    p = Pi2_train.Pi2_train(qubit_info, np.linspace(0.12, 0.14, 51), seq=None, postseq=None, repeat_pulse=10, proj_func='phase',
#                            extra_info=gate_info1
                            )
    p.measure()
    bla
    
if 0: #AllXY
    from scripts.single_qubit import allxy
    cool = sequencer.Constant(int(4e3),1,chan='3m1')

#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150), gate_info1.rotate(np.pi,0)])
#    postseq = gate_info1.rotate(np.pi,0) 
    alz.set_naverages(10000)
#    allxy_result =[]
    axy = allxy.All_XY(gate_info1 , seq=seq_cool, generate=True, proj_func='phase', postseq = None, extra_info=gate_info2)#, extra_info=gate_info1)  #seq=seq was added
    axy.measure()
#    allxy_result.append(axy.get_ys())
#    plt.plot(allxy_result)
    alz.set_naverages(2000)
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
  

if 0:  # Two-Qubit Randomized Benchmarking  
    from scripts.fluxonium import TwoQ_RB_ebru_temp
    from scripts.fluxonium  import timerabi_interleaved
    rndmben_result0 = []
    Pg_cplx0 = []
    rndmben_result1 = []
    Pg_cplx1 = []
    rndmben_result2 = []
    Pg_cplx2 = []
    
    alz.set_naverages(5000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2)
    Y_proj = gate_info1.rotate(np.pi/2, 0)
    
    for i in range(15):
#        alz.set_naverages(200)
        rndmben0 = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                      plot_seqs=False, category='all', generator='CZ',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                      singleQ_phases=[-2.56759,-1.31659], seq=seq, proj_func='phase')
        data0 = rndmben0.measure()
        rndmben_result0.append(rndmben0.get_ys())
        Pg_cplx0.append(rndmben0.Pgg)
#
        rndmben = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                      plot_seqs=False, category='all', generator='CZ', interleave='CZ',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                      singleQ_phases=[-2.56759,-1.31659], seq=seq, proj_func='phase')
        data = rndmben.measure()
        rndmben_result1.append(rndmben.get_ys())
        Pg_cplx1.append(rndmben.Pgg)

        rndmben = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                      plot_seqs=False, category='all', generator='CZ', interleave='I',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                      singleQ_phases=[-2.56759,-1.31659], seq=seq, proj_func='phase')
        data = rndmben.measure()
        rndmben_result2.append(rndmben.get_ys())
        Pg_cplx2.append(rndmben.Pgg)



#
###
        
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

    tempxs = rndmben0.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx0, xs, F_final=0.25, F_init=1-0.1)
    
    tempxs = rndmben.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx1, xs, F_final=0.25, F_init=1-0.35)
###

    tempxs = rndmben.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx2, xs, F_final=0.25, F_init=1-0.35)








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








if 0: # Optimizer Two-Qubit Randomized Benchmarking    
    #does not have state population corrections 
    rndnum = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],
              [0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],
              [0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    recov_index = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#        rndnum = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
#        recov_index = [0,0,0,0,0,0,0,0,0,0,0,0]
#

    rndnum[0]=[1878,6175,1883,4432]
    rndnum[1]=[9393,6620,3984,9103] 
    rndnum[2]=[1577,9189,2257,2251]
    rndnum[3]=[3196,9301,10425,6138]
    rndnum[4]=[3594,1964,1363,2463]
    rndnum[5]=[6290,7455,9365,2874]
    rndnum[6]=[4471,4065,7478,2151]
    rndnum[7]=[8479,134,6784,7324]
    rndnum[8]=[8888,7579,6462,6720]
    rndnum[9]=[1236,4586,7042,1185]
    rndnum[10]=[4873,177,1725,4727]
    rndnum[11]=[8605,10825,10989,11499]
    rndnum[12]=[9025,9688,11048,10768]
    rndnum[13]=[7240,6498,1723,2127]
    rndnum[14]=[10750,8401,8462,9414]
    rndnum[15]=[5946,11275,8343,11374]
    rndnum[16]=[4444,9030,2535,2734]
    rndnum[17]=[7256,7723,9839,10479]
    rndnum[18]=[1606,10123,7159,2055]
    rndnum[19]=[3286,6404,9883,10802]
    rndnum[20]=[4773,10300,8680,7073]
    rndnum[21]=[4503,8303,8980,9326]
    rndnum[22]=[11486,9690,6984,5306]
    rndnum[23]=[10889,4115,4855,5260]
    rndnum[24]=[1717,405,6883,1852]
    
    recov_index = [2194,6404,943,6884,10911,3320,8180,5616,3721,7614,8626,11133,
                   4695,5572,4323,5237,10654,910,11348,1861,3506,5412,2639,8557,5880]



    from scripts.fluxonium import TwoQ_RB_optimizer
    rndmben_result0 = []
    Pg_cplx0 = []
    rndmben_result1 = []
    Pg_cplx1 = []
    rndmben_result2 = []
    Pg_cplx2 = []
#    p2=[]
    drag=[]
    pi_amp=[]
#    fidelity=[]
    alz.set_naverages(4000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    X_proj = gate_info1.rotate(np.pi/2, np.pi/2)
    Y_proj = gate_info1.rotate(np.pi/2, 0)
    phase2 = -2.56
    phase1 = -1.30
    tag=[]
#    drag_range = np.linspace(-1.17,-1.42,15)

    drag_range = np.linspace(0,6,15)
    pi_amp_range = np.linspace(-0.110, -0.125,15)
    for i in range(25):
        alz.set_naverages(4000)
        rndmben0 = TwoQ_RB_optimizer.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info,pi_amp_range,drag_range, num_cal_points=3, sweep_length=len(drag_range),N_sequences=1,N_cliffords=4, 
                                      rndnum=rndnum[i], recov_index=recov_index[i], plot_seqs=False, category='all', generator='CZ', interleave = 'CZ',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=False,
                                      singleQ_phases=[phase2,phase1], seq=seq,   proj_func='phase')
        data0 = rndmben0.measure()
        rndmben_result0.append(rndmben0.avg_data)
        ys= np.mean(rndmben_result0,axis=0)
        
#        Pg_cplx0.append(rndmben0.Pgg)
    
    y2d = ys.reshape(len(ys)/4,4)
    y1s = y2d[:,0]
    y2s = y2d[:,1]
    y3s = y2d[:,2]
    y4s = y2d[:,3]    

    #3 is the number of calibration point here
    calibration_qubit1_excited = (y1s[:3] + y2s[:3] + y3s[:3] + y4s[:3])/4
    calibration_qubit2_excited = (y1s[3:6] + y2s[3:6] + y3s[3:6] + y4s[3:6])/4
    calibration_bothqubits_excited = (y1s[6:9] + y2s[6:9] + y3s[6:9] + y4s[6:9])/4
    calibration_ground = (y1s[9:12] + y2s[9:12] + y3s[9:12] + y4s[9:12])/4
    Veg = np.mean(calibration_qubit1_excited)
    Vge = np.mean(calibration_qubit2_excited)
    Vee = np.mean(calibration_bothqubits_excited)
    Vgg = np.mean(calibration_ground)
    print Veg, Vge, Vee, Vgg

    rd = y1s[12:]
    bl = y2s[12:]
    gr = y3s[12:]
    yw = y4s[12:]


    
    Pg1 = ((-rd-gr+bl+yw)/(Veg-Vgg+Vee-Vge)+1)/2
    Pg2 = ((-rd-bl+gr+yw)/(Vge-Vgg+Vee-Veg)+1)/2

    V_matrix = np.matrix([[Vgg, Vge, Veg, Vee], [Vge, Vgg, Vee, Veg], 
                          [Veg, Vee, Vgg, Vge], [Vee, Veg, Vge, Vgg]])
    y_vector = [rd, gr, bl, yw]
    P = np.dot(np.linalg.inv(V_matrix), y_vector)
    Pgg = np.transpose(P[0])
    Pgg= Pgg.A1
    plt.figure()
    plt.plot(drag_range,np.real(Pgg))

   
#    p2.append(phase2)
#    fidelity.append(rndmben0.Pgg[i])
    
#    for i in range(len(drag_range)):
#        drag.append(drag_range[i])
#        fidelity.append(rndmben0.Pgg[i])
#
#    plt.figure()
#    plt.plot(p2,np.real(fidelity), linestyle='None', marker='o')
#    plt.close()


    
#    tempxs = rndmben0.xs[48:]  #change this 
#    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
#    RB_fit(Pg_cplx0, xs, F_final=0.25, F_init=1-0.1)
#    tag.append([piamp,phase1,phase2])


if 0: # Simultaneous 1qubit gate RB
    from scripts.fluxonium import TwoQ_RB_ebru_temp
    rndmben_result1 = []
    Pgg = []
    Pg1 = []
    Pg2 = []
    alz.set_naverages(5000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])

    for i in range(15):
        rndmben = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, cx_info, cancel_info, num_cal_points=3, N_cliffords=110, 
                                      plot_seqs=False, category='single', generator='CZ',# interleave='CX',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True, seq=seq, proj_func='phase')
        data = rndmben.measure()
        rndmben_result1.append(rndmben.get_ys())
        Pgg.append(rndmben.Pgg)
        Pg1.append(rndmben.Pg1)
        Pg2.append(rndmben.Pg2)
    tempxs = rndmben.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]
    RBfig = RB_fit(Pgg, xs, F_final=0.25, F_init=1, label='Fidelity of |gg>,  total ')
    plt.title('Simultaneous 1Q randomized benchmarking',fontsize=12)
    RB_fit(Pg2, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit1, ', fig=RBfig)
    RB_fit(Pg1, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit2, ', fig=RBfig)
#    bla

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

for i in range(1):    
    if 0: #Cross-entropy Benchmarking
        from scripts.fluxonium import XEB_ebru_temp
        P1=[]
        ideal_pops1=[]
        num_seq=2
        alz.set_naverages(15000)
        cool = sequencer.Constant(int(4e3),1,chan='3m1')
        seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
        for i in range(num_seq):
    
            xeb = XEB_ebru_temp.CrossEB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cycles=70, 
                                              plot_seqs=False, use_virtual_Z=True,
                                              singleQ_phases=[-2.56759,-1.31659], seq=seq, proj_func='phase')
            data = xeb.measure()
            P1.append(np.transpose(xeb.P))
            ideal_pops1.append(xeb.ideal_pops)
            np.savetxt('P0_run1113_%d.txt'%i, np.transpose(xeb.P))
            np.savetxt('idealpops_run1113_%d.txt'%i, xeb.ideal_pops)
    

        inc_pops = [0.25, 0.25, 0.25, 0.25]

        H_inc_exp = np.zeros(xeb.N_cycles)
        for i in range(xeb.N_cycles): 
            count=0
            for j in range(num_seq):
               count += -(np.dot(inc_pops, np.log((np.array(ideal_pops1))[j][i]))) 
            H_inc_exp[i] = count

        H_exp = np.zeros(xeb.N_cycles)
        for i in range(xeb.N_cycles): 
            count=0  
            for j in range(num_seq):
                count += -(np.dot((ideal_pops1[j][i]), np.log(ideal_pops1[j][i]))) 
            H_exp[i] = count

        H_meas_exp = np.zeros(xeb.N_cycles)
        for i in range(xeb.N_cycles): 
            count=0          
            for j in range(num_seq):
                count += (np.asarray(-np.dot(np.real(P1[j][i]), np.log(ideal_pops1[j][i]))).reshape(-1)[0]) 
            H_meas_exp[i] = count
        alpha = (H_inc_exp - H_meas_exp)/(H_inc_exp - H_exp)

        tempxs = np.linspace(1,len(alpha),len(alpha))  #change this 
#        xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
        XEB_fit(alpha, tempxs, F_final=0, F_init=1)
        plt.xlabel('Number of cycles')
    
    #P0=[]
    #P1=[]
    #P2=[]
    #P3=[]
    
    #if 1:
#        P0.append(np.asarray(xeb.P0).reshape(-1)[0])
#        P1.append(np.asarray(xeb.P1).reshape(-1)[0])
#        P2.append(np.asarray(xeb.P2).reshape(-1)[0])
#        P3.append(np.asarray(xeb.P3).reshape(-1)[0])
#        plt.close('all')
#    
if 0: #Population rabi
    from scripts.fluxonium import rabi_populations 
    alz.set_naverages(4000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    tr1 = rabi_populations.Rabi(gate_info1, gate_info2, np.linspace(-0.15,0.15, 61), selective=False,
                                   plot_seqs=False, generate=True, repeat_pulse=1, cancel_info=None,
                                   update=False, seq=seq, postseq=None, proj_func='phase',
                                   )
    data=tr1.measure()    
    bla
    
if 0: #Calculate initial state populations - using 4 geophasecal measurements for each qubit 

    from scripts.single_qubit import geophasecal
    alz.set_naverages(5000)

    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    X_proj = gate_info1.rotate(-np.pi/2, np.pi/2)
    Y_proj = gate_info1.rotate(np.pi/2, 0)


    CZ_duration = 4+36 

    for postseq in [gate_info2.rotate(np.pi,0)]:    
        geoph = geophasecal.geophasecal(gate_info1, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = True, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info2
                                            )
        data=geoph.measure() 
        qubit1_1 = np.abs(geoph.fit_params['amp'].value) #To handle the standard error, I should also 
        #include geoph.fit_params['amp'].stderr
    
#    
        geoph = geophasecal.geophasecal(gate_info1, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = False, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info2
                                            )
        data=geoph.measure() 
        qubit1_2 = np.abs(geoph.fit_params['amp'].value) 
    
        
        geoph = geophasecal.geophasecal(gate_info1, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = True, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=postseq, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info2
                                            )
        data=geoph.measure() 
        qubit1_3 = np.abs(geoph.fit_params['amp'].value) 
#    
        geoph = geophasecal.geophasecal(gate_info1, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = False, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=postseq, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info2
                                            )
        data=geoph.measure() 
        qubit1_4 = np.abs(geoph.fit_params['amp'].value)


    for postseq in [gate_info1.rotate(np.pi,0)]:    
        geoph = geophasecal.geophasecal(gate_info2, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = True, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info1
                                            )
        data=geoph.measure() 
        qubit2_1 = np.abs(geoph.fit_params['amp'].value) #To handle the standard error, I should also 
        #include geoph.fit_params['amp'].stderr
    
#    
        geoph = geophasecal.geophasecal(gate_info2, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = False, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=None, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info1
                                            )
        data=geoph.measure() 
        qubit2_2 = np.abs(geoph.fit_params['amp'].value) 
    
        
        geoph = geophasecal.geophasecal(gate_info2, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = True, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=postseq, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info1
                                            )
        data=geoph.measure() 
        qubit2_3 = np.abs(geoph.fit_params['amp'].value) 
#    
        geoph = geophasecal.geophasecal(gate_info2, ZZ_info, np.linspace(-np.pi, np.pi, 101), test_info2=None, 
                                            wait_reference = False, wait_time =CZ_duration , repeat_pulse=1,
                                            seq=seq, postseq=postseq, proj_func='phase', plot_seqs=False,
                                            extra_info=gate_info1
                                            )
        data=geoph.measure() 
        qubit2_4 = np.abs(geoph.fit_params['amp'].value) 

    #K is the excited state population for qubit 1
    #e is the the excited state population for qubit 2
    
    #e will come from the set of measurement for qubit 1
    #K will come from the set of measurements for qubit 2
    

    
    e = (qubit1_3 - qubit1_4) / (qubit1_1 + qubit1_2 + qubit1_3 - qubit1_4)
    K = (qubit2_3 - qubit2_4) / (qubit2_1 + qubit2_2 + qubit2_3 - qubit2_4)
    
    
    p0 = (1-K)*(1-e)
    p1 = e*(1-K)
    p2 = K*(1-e)
    p3 = e*K
    
    print('Igg is:', p0)
    print('Ige is:', p1)
    print('Ieg is:', p2)
    print('Iee is:', p3)
    print('sum of probabilities:', p0+p1+p2+p3)
    


#Interleaving RB, XEB and single qubit measurements     
    
    
if 0: # Simultaneous 1qubit gate RB
    from scripts.fluxonium import TwoQ_RB_ebru_temp
    from scripts.fluxonium import XEB_ebru_temp

    rndmben_resultS = []
    Pgg = []
    Pg1 = []
    Pg2 = []


    rndmben_result0 = []
    Pg_cplx0 = []
    rndmben_result1 = []
    Pg_cplx1 = []
    rndmben_result2 = []
    Pg_cplx2 = []

    P1=[]
    ideal_pops1=[]


    alz.set_naverages(2000)
    cool = sequencer.Constant(int(4e3),1,chan='3m1')
    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(150)])
    num_seq=45
    for i in range(num_seq):
        alz.set_naverages(2000)


#Simultaneous RB
        rndmbenS = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, cx_info, cancel_info, num_cal_points=3, N_cliffords=70, 
                                      plot_seqs=False, category='single', generator='CZ',# interleave='CX',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True, seq=seq, proj_func='phase')
        data = rndmbenS.measure()
        rndmben_resultS.append(rndmbenS.get_ys())
        Pgg.append(rndmbenS.Pgg)
        Pg1.append(rndmbenS.Pg1)
        Pg2.append(rndmbenS.Pg2)

# Regular 2Q RB, non interleaved, interleaved with CZ and interleaved with identity
        rndmben0 = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                      plot_seqs=False, category='all', generator='CZ',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                      singleQ_phases=[-2.56,-1.30], seq=seq, proj_func='phase')
        data0 = rndmben0.measure()
        rndmben_result0.append(rndmben0.get_ys())
        Pg_cplx0.append(rndmben0.Pgg)
#
        rndmben1 = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                      plot_seqs=False, category='all', generator='CZ', interleave='CZ',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                      singleQ_phases=[-2.56,-1.30], seq=seq, proj_func='phase')
        data = rndmben1.measure()
        rndmben_result1.append(rndmben1.get_ys())
        Pg_cplx1.append(rndmben1.Pgg)

        rndmben2 = TwoQ_RB_ebru_temp.TwoQubit_RB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cliffords=35, 
                                      plot_seqs=False, category='all', generator='CZ', interleave='I',
                                      find_cheapest_recovery=False, use_virtual_Z=True, virtual_recovery=True, use_lookup_table=True,
                                      singleQ_phases=[-2.56,-1.30], seq=seq, proj_func='phase')
        data = rndmben2.measure()
        rndmben_result2.append(rndmben2.get_ys())
        Pg_cplx2.append(rndmben2.Pgg)


# XEB
        alz.set_naverages(6000)
        xeb = XEB_ebru_temp.CrossEB(gate_info2, gate_info1, ZZ_info, cancel_info, num_cal_points=3, N_cycles=70, 
                                              plot_seqs=False, use_virtual_Z=True,
                                              singleQ_phases=[-2.56,-1.30], seq=seq, proj_func='phase')
        data = xeb.measure()
        P1.append(np.transpose(xeb.P))
        ideal_pops1.append(xeb.ideal_pops)
        np.savetxt('P0_run_haonan01_%d.txt'%i, np.transpose(xeb.P))
        np.savetxt('idealpops_run_haonan01_%d.txt'%i, xeb.ideal_pops)









    tempxs = rndmbenS.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]
    RBfig = RB_fit(Pgg, xs, F_final=0.25, F_init=1, label='Fidelity of |gg>,  total ')
    plt.title('Simultaneous 1Q randomized benchmarking',fontsize=12)
    RB_fit(Pg2, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit1, ', fig=RBfig)
    RB_fit(Pg1, xs, F_final=0.50, F_init=1, label='Fidelity of |g> for Qubit2, ', fig=RBfig)
#

    tempxs = rndmben0.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx0, xs, F_final=0.25, F_init=1-0.1)
    
    tempxs = rndmben1.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx1, xs, F_final=0.25, F_init=1-0.2)
###

    tempxs = rndmben2.xs[12:]  #change this 
    xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    RB_fit(Pg_cplx2, xs, F_final=0.25, F_init=1-0.2)



    inc_pops = [0.25, 0.25, 0.25, 0.25]

    H_inc_exp = np.zeros(xeb.N_cycles)
    for i in range(xeb.N_cycles): 
        count=0
        for j in range(num_seq):
           count += -(np.dot(inc_pops, np.log((np.array(ideal_pops1))[j][i]))) 
        H_inc_exp[i] = count

    H_exp = np.zeros(xeb.N_cycles)
    for i in range(xeb.N_cycles): 
        count=0  
        for j in range(num_seq):
            count += -(np.dot((ideal_pops1[j][i]), np.log(ideal_pops1[j][i]))) 
        H_exp[i] = count

    H_meas_exp = np.zeros(xeb.N_cycles)
    for i in range(xeb.N_cycles): 
        count=0          
        for j in range(num_seq):
            count += (np.asarray(-np.dot(np.real(P1_corrected[j][i]), np.log(ideal_pops1[j][i]))).reshape(-1)[0]) 
#            count += (-np.dot(np.transpose(P1_corrected[j][i]).A1, np.log(ideal_pops1[j][i]))) 

        H_meas_exp[i] = count
    alpha = (H_inc_exp - H_meas_exp)/(H_inc_exp - H_exp)

    tempxs = np.linspace(1,len(alpha),len(alpha))  #change this 
#        xs = tempxs.reshape(len(tempxs)/4,4).transpose()[0]  #Each gate is actually 2 Cliffords, one on each qubit
    XEB_fit(alpha, tempxs, F_final=0, F_init=1)
    plt.xlabel('Number of cycles')



    bla

    