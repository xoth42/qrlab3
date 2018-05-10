import numpy as np

'''use functional form from Brian's science paper, eqS5: y = 0.5*{1+cos(|beta|^2*sin(chi*t))exp(|beta|^2*cos(chi*t -1))}'''

def func(xs, chi, nbar=1, T2 = 20e3, A = 1, xs0=0, ofs=0):
    y= np.exp(nbar*(np.cos(chi*(xs-xs0))-1))*np.cos(nbar*np.sin(chi*(xs-xs0))) + 1
    y= A*np.exp(-xs/T2)*y
    return y

def guess(xs, ys):
    yofs = min(ys)
    ys = ys - yofs
    return dict(
        A= max(ys)-min(ys),
        T2 = 20e3, 
        chi = 0.003/2,
        nbar = 4.0,
        xs0 = 350.0,
        ofs = yofs
    )