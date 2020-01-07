# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 12:27:21 2019

@author: Wang_Lab
"""

rofreq = 10.935e9
freq_range = 2.5e6
dig.set_naverages(10000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-5, 10, 1),
                                         np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                         qubit_pulse=False, seq=None)
ro.measure()
pl.close()
max_freq = ro.fit_params[2]
print max_freq
readout_info.rfsource1.set_frequency(ro.fit_params[2])
readout_info.rfsource2.set_frequency(ro.fit_params[2]+50e6)   

freadout.append(max_freq)




from single_qubit import rabi
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
dig.set_naverages(10000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
tr = rabi.Rabi(qubit_info, 
    #                       np.linspace(-0.2, -0.20, 81), selective=False,
                           np.linspace(-0.6, 0.6, 81), selective=False,
    #                       np.linspace(-0.26, -0.18, 101), selective=False,
    #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                           plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                           update=True, #extra_info=ef_info,
                           proj_func='phase')
tr.measure_keysight()
pl.title('S31 with qubit1 field = %s'%(float(field0)))
rabiamp1.append(tr.fit_params['amp'].value)
rabiamp1_err.append(tr.fit_params['amp'].stderr)
pl.close()

dig.set_naverages(80000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
tr = rabi.Rabi(qubit2_info, 
    #                       np.linspace(-0.2, -0.20, 81), selective=False,
                           np.linspace(-0.7, 0.7, 81), selective=False,
    #                       np.linspace(-0.26, -0.18, 101), selective=False,
    #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                           plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                           update=True, fix_period = qubit2ge.get_pi_amp()*2, #extra_info=ef_info,
                           proj_func='phase')
tr.measure_keysight()
pl.title('S31 with qubit2 field = %s'%(float(field0)))    
rabiamp2.append(tr.fit_params['amp'].value)
rabiamp2_err.append(tr.fit_params['amp'].stderr)
pl.close()


dig.set_naverages(10000)
#    SC_qubit.set_rf_on(False)
#    qubitbrick.set_rf_on(True)
tr = rabi.Rabi(qubit_info, 
    #                       np.linspace(-0.2, -0.20, 81), selective=False,
                           np.linspace(-0.6, 0.6, 81), selective=False,
    #                       np.linspace(-0.26, -0.18, 101), selective=False,
    #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                           plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                           update=True, #extra_info=ef_info,
                           proj_func='phase')
tr.measure_keysight()
pl.title('S31 with qubit1 field = %s'%(float(field0)))
rabiamp3.append(tr.fit_params['amp'].value)
rabiamp3_err.append(tr.fit_params['amp'].stderr)
pl.close()
rofreq = 10.935e9
freq_range = 2.5e6
dig.set_naverages(10000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
ro = rocavspectroscopy_keysight.ROCavSpectroscopy_keysight(qubit_info, np.linspace(-5, 10, 1),
                                         np.linspace(rofreq-freq_range, rofreq+freq_range, 101),
                                         qubit_pulse=False, seq=None)
ro.measure()
pl.close()
max_freq = ro.fit_params[2]
print max_freq
readout_info.rfsource1.set_frequency(ro.fit_params[2])
readout_info.rfsource2.set_frequency(ro.fit_params[2]+50e6)   

freadout.append(max_freq)




from single_qubit import rabi
#    seq = sequencer.Join([sequencer.Trigger(250), cool, sequencer.Delay(500)])
dig.set_naverages(10000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
tr = rabi.Rabi(qubit_info, 
    #                       np.linspace(-0.2, -0.20, 81), selective=False,
                           np.linspace(-0.6, 0.6, 81), selective=False,
    #                       np.linspace(-0.26, -0.18, 101), selective=False,
    #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                           plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                           update=True, #extra_info=ef_info,
                           proj_func='phase')
tr.measure_keysight()
pl.title('S31 with qubit1 field = %s'%(float(field0)))
rabiamp1.append(tr.fit_params['amp'].value)
rabiamp1_err.append(tr.fit_params['amp'].stderr)
pl.close()

dig.set_naverages(80000)
#    SC_qubit.set_rf_on(True)
#    qubitbrick.set_rf_on(True)
tr = rabi.Rabi(qubit2_info, 
    #                       np.linspace(-0.2, -0.20, 81), selective=False,
                           np.linspace(-0.7, 0.7, 81), selective=False,
    #                       np.linspace(-0.26, -0.18, 101), selective=False,
    #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                           plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                           update=True, fix_period = qubit2ge.get_pi_amp()*2, #extra_info=ef_info,
                           proj_func='phase')
tr.measure_keysight()
pl.title('S31 with qubit2 field = %s'%(float(field0)))    
rabiamp2.append(tr.fit_params['amp'].value)
rabiamp2_err.append(tr.fit_params['amp'].stderr)
pl.close()


dig.set_naverages(10000)
#    SC_qubit.set_rf_on(False)
#    qubitbrick.set_rf_on(True)
tr = rabi.Rabi(qubit_info, 
    #                       np.linspace(-0.2, -0.20, 81), selective=False,
                           np.linspace(-0.6, 0.6, 81), selective=False,
    #                       np.linspace(-0.26, -0.18, 101), selective=False,
    #                       np.linspace(-0.47,-0.41, 81), selective=False,                   
                           plot_seqs=False, generate=True, repeat_pulse=1, seq=None,
                           update=True, #extra_info=ef_info,
                           proj_func='phase')
tr.measure_keysight()
pl.title('S31 with qubit1 field = %s'%(float(field0)))
rabiamp3.append(tr.fit_params['amp'].value)
rabiamp3_err.append(tr.fit_params['amp'].stderr)
pl.close()
