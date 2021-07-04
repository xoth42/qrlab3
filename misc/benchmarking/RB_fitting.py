import numpy as np
import matplotlib.pyplot as pl
import lmfit

def fit_exp(params, x, data):
    return data - (params['a'] + params['b'] * np.exp(-1 * x / params['c']))

def exponential(params, x):
    return params['a'] + params['b'] * np.exp(-1 * x / params['c'])

data = np.loadtxt('raw_data.txt')
ave = np.mean(data, axis = 0)
std = np.std(data, axis = 0)/np.sqrt(int(np.shape(data)[0]))

x_data = np.arange(1, 151, 3)

params = lmfit.Parameters()
params.add('a', value=np.min(ave))
params.add('b', value=np.max(ave))
params.add('c', value=x_data[-1])

result = lmfit.minimize(fit_exp, params, args=(x_data, ave))

print((result.params['a'].value))
print((result.params['c'].value))
a = result.params['a'].value

ave -= a

ave /= np.max(ave)

fit = np.polyfit(x_data, np.log(ave), 1, w=1/std)
fit_fn = np.poly1d(fit)
print(fit_fn)
print(fit_fn[1])
# fit_fn is now a function which takes in x and returns an estimate for y

text = 'Error per gate = %.03f '%(fit_fn[1]*(-1))



pl.clf()
ax = pl.gca()
#ax.set_yscale('log')
ax.set_ylabel('ln(Fidelity)')
ax.set_xlabel('Gate Pairs')
pl.errorbar(x_data, np.log(ave), yerr = std)
pl.plot(x_data, fit_fn(x_data), '--k', label=text)
pl.legend(text)


pl.savefig("plot.png")
pl.show()

