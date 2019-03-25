# -*- coding: utf-8 -*-
"""
it is a combination of 3 parts
1. get the color graph of the Sij - Sji by setting filename1 and 2
2. get the color graph of a file
3. get a linecut of a graph and save it to a folder
"""

import matplotlib
matplotlib.interactive(True)

import numpy as np
import matplotlib.pyplot as pl

filepath = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-2"

if 1: # get the graph of difference between two file
    # Read the array from file
#    filepath = 'C:\Users\WangLab\Documents\\11282018 cooldowm\\'
    filename2 ='%s\\s12_3_term0.0-0.2-0.002_Date_3-19_17-20-13'%(filepath)
    filename1 ='%s\\s21_3_term0.0-0.2-0.002_Date_3-19_16-54-59'%(filepath)
#    if filename1[33:]!=filename2[33:]:
#        print 'not the same port measurement'
    new_data = np.loadtxt('%s.txt'%(filename1))
    new_data2 = np.loadtxt('%s.txt'%(filename2))
    print new_data.shape
    # Note that this returned a 2D array!
    # However, going back to 3D is easy if we know the 
    # original shape of the array
    
    size = new_data.shape[1]
    new_data = new_data.reshape((4,new_data.shape[0]/4,size))
    new_data2 = new_data2.reshape((4,new_data2.shape[0]/4,size))
    
    X = new_data[0]*1000
    Y = new_data2[1]
    Z = new_data[2]
#    phase = new_data[3]
#    Z = Z * np.exp(1j*phase*np.pi/180)
    X2 = new_data2[0]*1000
    Z2 =new_data2[2] 
#    phase2 = new_data2[3]
#    Z2 = Z2 * np.exp(1j*phase2*np.pi/180)
    iso = Z-Z2
#    iso = np.abs(iso)
    
    
##'''    
#    i=0
#    ii = 20
#    passes = []
#    k=0
#    for k in range(1601):
#        for i in range(size):
#            if iso[k][i] > ii:
#                passes.append(X[0][i])
#            i = i+5
#    trupasses = np.unique(passes)
##'''
        
    x=X[0]
    y=Y[:,0]/10**9

#
#    for i in range(len(x)):
#        if x[i] < 5:
#            x[i] = x[i]*60
#        else:
#            x[i] = -2.709 * (x[i])**2 + 86.171*x[i]-63.13
            
    X, Y = np.meshgrid(x,y)
    #Y=np.transpose(Y)
    #iso = np.transpose(iso)
    
    #pl.figure()
    #freq=Y[:,0]
    #
    #for i in range(Z.shape[1]):
    #    pl.plot(freq, iso[:,i],label = 'm= %s mT'%X[i][0])
    #    pl.legend()
#    X = X[160*2:160*7]
#    Y = Y[160*2:160*7]
#    Z2 = Z2[160*2:160*7]
#    Z = Z[1::2]
#    iso = Z2-Z
    
    pl.figure()
#    pl.suptitle(filename1[67:70])
    pl.pcolormesh(X, Y, Z)
    pl.colorbar()
    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    pl.show() 
   
    pl.figure()
#    pl.suptitle(filename2[67:70])
    pl.pcolormesh(X2, Y, Z2)
    pl.colorbar()
    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    pl.show() 
    pl.figure()
    #pl.suptitle('ratio of transition and isolation')
#    pl.suptitle('dB('+filename1[67:70]+')-dB(' +filename2[67:70] +')')
    pl.pcolormesh(X, Y, iso,cmap='RdBu', vmin=0, vmax=40)
    pl.ylim([np.min(Y),np.max(Y)])
    pl.xlim([np.min(X),np.max(X)])
    pl.colorbar()
    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
#    pl.xlim(.4,.795)
#    pl.ylim(7,11)
    pl.show()


    import matplotlib.gridspec as gridspec
    # Create 2x2 sub plots
    #print('ab')
    gs = gridspec.GridSpec(2, 2)
    gs.update(wspace=0.4, hspace=0.35)
    X = abs(X)
    pl.figure()
    ax = pl.subplot(gs[0, 0])
    pl.pcolormesh(X, Y, Z)
    pl.colorbar()
#    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    pl.ylim(8,)
    pl.show() 
    
    ax = pl.subplot(gs[0, 1])
    pl.pcolormesh(X2, Y, Z2)
    pl.colorbar()
#    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    pl.ylim(8,)
    pl.show()
    
    ax = pl.subplot(gs[1, 0])
    pl.pcolormesh(X, Y, iso,cmap='RdBu', vmin=0, vmax=40)
    pl.ylim([np.min(Y),np.max(Y)])
    pl.xlim([np.min(X),np.max(X)])
    pl.colorbar()
    pl.ylim(8,)
    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    
    ax = pl.subplot(gs[1, 1])
    pl.pcolormesh(X, Y, iso,cmap='RdBu', vmin=0, vmax=40)
    pl.ylim([np.min(Y),np.max(Y)])
    pl.xlim([np.min(X),np.max(X)])
    pl.colorbar()
    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    pl.xlim(10,35)
    pl.ylim(10.9,11.5)


if 0: #get the graph of a single file
    # Read the array from file
#    filepath = 'C:\Users\WangLab\Documents\\11282018 cooldowm\\'
    filename ='%s\\circulator_weak_coupling_S21_0.0_0.07_0.001_ave_factor_7_18-10-56'%(filepath)
    new_data = np.loadtxt('%s.txt'%(filename))
    print new_data.shape
    # Note that this returned a 2D array!
    # However, going back to 3D is easy if we know the 
    # original shape of the array
    
    size = new_data.shape[1]
    new_data = new_data.reshape((4,new_data.shape[0]/4,size))

    
    X = new_data[0]
    Y = new_data[1]
    Z = new_data[2]
    phase = new_data[3] 
    
    x=X[0]*1000
#    x=x*56
    y=Y[:,0]/10**9
    
#    for i in range(len(x)):
#        if x[i] < 250:
#            x[i] = x[i]/float(50)*60
#        else:
#            x[i] = -2.709 * (x[i]/float(50))**2 + 86.171*x[i]/float(50)-63.13
            
    X, Y = np.meshgrid(x,y)
        
    
    #Y=np.transpose(Y)

#    pl.figure()
#    freq=Y[:,0]
    #
    #for i in range(Z.shape[1]):
    #    pl.plot(freq, iso[:,i],label = 'm= %s mT'%X[i][0])
    #    pl.legend()
#    pl.figure()
##    pl.suptitle(filename[0:21])
#    pl.pcolormesh(X, Y, Z, cmap = 'viridis')
#    pl.ylim([np.min(Y),np.max(Y)])
#    pl.xlim([np.min(X),np.max(X)])
#    pl.colorbar()
#    pl.xlabel('Magnetic Field(T)')
#    pl.ylabel('Frequency (GHZ)')
##    pl.xlim(.4,.795)
##    pl.ylim(7,11)
    pl.show()     
    pl.figure()
#    pl.suptitle(filename[67:70])
    pl.pcolormesh(X, Y, Z)
    pl.colorbar()
    pl.xlabel('Magnetic Field(mT)')
    pl.ylabel('Frequency (GHZ)')
    pl.show() 


#    pl.figure()
#    pl.suptitle('phsae')
#    pl.pcolormesh(X, Y, phase, cmap = 'viridis')
#    pl.ylim([np.min(Y),np.max(Y)])
#    pl.xlim([np.min(X),np.max(X)])
#    pl.colorbar()
#    pl.xlabel('Magnetic Field(T)')
#    pl.ylabel('Frequency (GHZ)')
##    pl.xlim(.4,.795)
##    pl.ylim(7,11)
#    pl.show()

#    X = np.transpose(X)
#    Y = np.transpose(Y)    
#    Z = np.transpose(Z)
#    phase = np.transpose(phase)
#    n= 100
#    X = X[0:n]
#    Y = Y[0:n]
#    Z = Z[0:n]
#    phase = phase[0:n]
#    X = np.transpose(X)
#    Y = np.transpose(Y)    
#    Z = np.transpose(Z)
#    phase = np.transpose(phase)
#    to_save = [X, Y, Z, phase]
#    filename ='%s\\circulator_S13_0.0_0.1_0.001_ave_factor_11_21-50-58'%(filepath)
#    with file(filename,'w') as outfile:
#
#        outfile.write('# Array\n')
#
#     # Iterating through a ndimensional array produces slices along
#     # the last axis. This is equivalent to data[i,:,:] in this case
#       for data_slice in to_save:
#
#        # The formatting string indicates that I'm writing out
#        # the values in left-justified columns 7 characters in width
#        # with 2 decimal places.  
#           np.savetxt(outfile, data_slice, fmt='%-7.7f')
#
#        # Writing out a break to indicate different slices...
#            outfile.write('# New slice\n')

    
    
    
    
if 0: #a specific trace is needed    
#    filename ='circulator_fridge_S21_field_0.023_0.027_0.001_ave_factor_999-0728'
#    filepath = 'C:\Users\WangLab\Documents\\11282018 cooldowm\\'
    filename ='%s\\circulator_S12_port3_terminated_0_4_0.01_12-12-2018'%(filepath)
    #filename ='circulator_fridge_S13_field_0.0_0.8_0.005_ave_factor_10-0729'
    new_data = np.loadtxt('%s.txt'%(filename))
    print new_data.shape
    # Note that this returned a 2D array!
    # However, going back to 3D is easy if we know the 
    # original shape of the array
    
    size = new_data.shape[1]
    new_data = new_data.reshape((4,new_data.shape[0]/4,size))

    
    X = new_data[0] #b-field / current / voltage
    Y = new_data[1] #frequency
    Z = new_data[2] #s-param db
    phase = new_data[3] 
#    X=-X
    m = 1 #the magnetic field you want
    i=0
    for i in range(size):
        if np.abs(X[0][i]) < np.abs(m):
            i = i + 1
        else:
            break
     
    Z = np.transpose(Z)
    Y = np.transpose(Y)
    phase = np.transpose(phase)
    z = Z[i]
    phase = phase[i]
    freq = Y[0]
    pl.figure()
#    pl.suptitle(filename[:14]+filename[33:])
    pl.plot(freq, z,label='S12'%(X[0][i]*1000))
    pl.plot(freq, phase/5,label='B=phase/5'%(X[0][i]*1000))
#    pl.xlim(8.5,9.5)
    pl.xlabel('frequency(GHZ)')
    pl.ylabel('dB')
    pl.show()
    pl.legend()
    #pl.figure()
    #y= np.exp(z/20)
    #pl.plot(freq,y)

#    z = z[:,None].T
#    freq = freq[:,None].T
#    phase = phase[:,None].T
#    trace = np.concatenate([freq, z, phase]).T
#    np.savetxt(r'C:\Users\Wang Lab\OneDrive\figures\%smT.txt' %(m), trace , delimiter=",") 



'''For Isolation of single trace'''
if 0: # get a single trace for the difference between two files
    # Read the array from file
#    filepath = 'C:\Users\WangLab\Documents\\11282018 cooldowm\\'
    filename1 ='%s\\circulator_S21_0.0_-0.1_-0.001_ave_factor_6_14-35-34'%(filepath)
    filename2 ='%s\\circulator_S21_0.0_0.1_0.001_ave_factor_6_14-35-34'%(filepath)
#    if filename1[33:]!=filename2[33:]:
#        print 'not the same port measurement'
    new_data = np.loadtxt('%s.txt'%(filename1))
    new_data2 = np.loadtxt('%s.txt'%(filename2))
    print(new_data.shape)

    
    size = new_data.shape[1]
    new_data = new_data.reshape((4,new_data.shape[0]//4,size))
    new_data2 = new_data2.reshape((4,new_data2.shape[0]//4,size))
    
    X = new_data[0]
    Y = new_data2[1]
    Z = new_data[2]
    phase = new_data[3]
    Z2 =new_data2[2] 
    iso = Z-Z2
    
    m = 0.021 #the magnetic field you want
    i=0
    for i in range(size):
        if np.abs(X[0][i]) < np.abs(m):
            i = i + 1
        else:
            break
        
    iso = np.transpose(iso)
    Y = np.transpose(Y)
    Z = np.transpose(Z)
    Z2 = np.transpose(Z2)
    phase = np.transpose(phase)
    iso = iso[i]
    z= Z[i]
    z2 = Z2[i]
    phase = phase[i] 
    x=X[0]
    y=Y[:,0]
    freq = Y[0]

    pl.figure()
#    pl.suptitle(filename[:14]+filename[33:])
    pl.plot(freq, z)
    pl.plot(freq, z2)
    pl.figure()
    pl.plot(freq, iso,label='m=%s mT'%X[0][i])
    pl.xlabel('frequency(GHZ)')
    pl.ylabel('dB')
    pl.show()
    pl.legend()

    iso = iso[:,None].T
    freq = freq[:,None].T
    phase = phase[:,None].T
    trace = np.concatenate([freq, iso, phase]).T
    #np.savetxt(r'C:\Users\Wang_Lab\Documents\yingying\FMR\circulator fridge\%s_%smT.txt' %(filename,m), trace , delimiter=",") 
    
    
    
if 1: # get loss between two file
    # Read the array from file
#    filepath = 'C:\Users\WangLab\Documents\\11282018 cooldowm\\'
    filename1 ='%s\\s21_3_term0.0-0.2-0.002_Date_3-19_16-54-59'%(filepath)
    filename2 ='%s\\s11_3_term0.0-0.2-0.002_Date_3-19_16-13-21'%(filepath)
#    if filename1[33:]!=filename2[33:]:
#        print 'not the same port measurement'
    new_data = np.loadtxt('%s.txt'%(filename1))
    new_data2 = np.loadtxt('%s.txt'%(filename2))
    print new_data.shape
    # Note that this returned a 2D array!
    # However, going back to 3D is easy if we know the 
    # original shape of the array
    
    size = new_data.shape[1]
    new_data = new_data.reshape((4,new_data.shape[0]/4,size))
    new_data2 = new_data2.reshape((4,new_data2.shape[0]/4,size))
    
    X = new_data[0]
    X = X*529.37
    Y = new_data2[1]
    Z = new_data[2] #S22
    phase = new_data[3]
    Z2 =new_data2[2] #S12
#    loss = 1-np.power(10,(Z)/10.0) - np.power(10,(Z2 + 29.6)/10.0)
#
#    filename3 = 'C:\Users\WangLab\Documents\yingying\circulator\loss\\f_f adpter with two elbows\\S12 no cal'

#    new_data3 = np.loadtxt('%s.txt'%(filename3),delimiter =',')
#    new_data3 = np.transpose(new_data3)
    
#    Z0 = new_data3[1]  #f-f adpter

#    X0,Z0 = np.meshgrid(X[0],Z0)

    loss = 1-np.power(10,(Z)/10.0) - np.power(10,(Z2)/10.0)
    
    
#'''    
#    i=0
#    ii = 20
#    passes = []
#    k=0
#    for k in range(1601):
#        for i in range(size):
#            if iso[k][i] > ii:
#                passes.append(X[0][i])
#            i = i+5
#    trupasses = np.unique(passes)
#'''
#        
#    x=X[0]
#    y=Y[:,0]

#
#    for i in range(len(x)):
#        if x[i] < 250:
#            x[i] = x[i]*60
#        else:
#            x[i] = -2.709 * (x[i])**2 + 86.171*x[i]-63.13
            
#    X, Y = np.meshgrid(x,y)
    #Y=np.transpose(Y)
    #iso = np.transpose(iso)
    
    #pl.figure()
    #freq=Y[:,0]
    #
    #for i in range(Z.shape[1]):
    #    pl.plot(freq, iso[:,i],label = 'm= %s mT'%X[i][0])
    #    pl.legend()

    pl.figure()
    pl.suptitle('dB('+filename1[18:21]+')')

    pl.pcolormesh(X, Y, Z)
    pl.ylim([np.min(Y),np.max(Y)])
    pl.xlim([np.min(X),np.max(X)])
    pl.colorbar()
    pl.xlabel('Magnetic Field')
    pl.ylabel('Frequency (GHZ)')
#    pl.xlim(.4,.795)
#    pl.ylim(7,11)
    pl.show()
    
    
    pl.figure()
    pl.suptitle('dB('+filename2[18:21]+')')

    pl.pcolormesh(X, Y, Z2)
    pl.ylim([np.min(Y),np.max(Y)])
    pl.xlim([np.min(X),np.max(X)])
    pl.colorbar()
    pl.xlabel('Magnetic Field')
    pl.ylabel('Frequency (GHZ)')
#    pl.xlim(.4,.795)
#    pl.ylim(7,11)
    pl.show()


    pl.figure()
    #pl.suptitle('ratio of transition and isolation')
#    pl.suptitle('dB('+filename1[18:21]+')-dB(' +filename2[18:21] +')')

    pl.pcolormesh(X, Y, loss,cmap='RdBu', vmin=-0.05, vmax=0.05)
    pl.ylim([np.min(Y),np.max(Y)])
    pl.xlim([np.min(X),np.max(X)])
    pl.colorbar()
    pl.xlabel('Magnetic Field')
    pl.ylabel('Frequency (GHZ)')
#    pl.xlim(.4,.795)
#    pl.ylim(7,11)
    pl.show()
    
    
    m = 0.44 #the magnetic field you want
    i=0
    for i in range(size):
        if X[0][i] < m:
            i = i + 1
        else:
            break
        
#    Z = np.transpose(Z)[i]
#    Z2 = np.transpose(Z2)[i]
#    Z0 = np.transpose(Z0)[i]
#    loss = np.transpose(loss)[i]
#    Y = np.transpose(Y)
##    phase = np.transpose(phase)
##    loss = loss[i]
##    phase = phase[i] 
#
#    freq = Y[0]

#    pl.figure()
##    pl.suptitle(filename[:14]+filename[33:])
#    pl.plot(freq, loss,label='%s V\n loss'%X[0][i])
#    pl.plot(freq, np.power(10,(Z)/10.0),label='S22')
#    pl.plot(freq, 1 - np.power(10,(Z2-Z0)/10.0),label='1 - S12')
##    pl.plot(freq, loss,label='m=%s V\n loss')
#    pl.xlabel('frequency(GHZ)')
#    pl.xlim(10,11)
#    pl.ylim(0,0.05)
#    pl.ylabel('loss')
#    pl.show()
#    pl.legend()
#    

  
#    pl.figure()
##    pl.suptitle(filename[:14]+filename[33:])
#    pl.plot(freq, Z2,label='%s V\n S12 for circulator'%X[0][i])
#    pl.plot(freq, Z0,label='S12 for adptor')
##    pl.legend()
##    pl.plot(freq, Z2 - Z0,label='S12')
##    pl.plot(freq, loss,label='m=%s V\n loss')
#    pl.xlabel('frequency(GHZ)')
##    pl.xlim(10,11)
#    pl.ylim(-36,-34)
#    pl.ylabel('dB')
#    ax2 = pl.twinx()
#    ax2.plot(freq, Z2-Z0, 'r',label = 'S12')
##    ax2.set_ylabel( color='r')
#    ax2.tick_params('y',colors='r')
#    pl.ylim(-2,0)
#    pl.xlim(10,11)
##    pl.show()
#    pl.legend()