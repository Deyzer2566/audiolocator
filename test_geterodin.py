import numpy as np
from numpy import random
from numpy import fft
#cos a * cos b = 1/2(cos(a+b)+cos(a-b))
#sin a * cos b = 1/2(sin(a+b)+sin(a-b))
#sin a * sin b = 1/2(cos(a-b)-cos(a+b))
#sin ax * sin (ax+d) = 1/2(cos(ax-ax-d)-cos(ax+ax+d)) = 1/2(cos(d)-cos(2ax+d))

# freqs = random.randint(100, 300, random.randint(2,10)).reshape(-1,1)
freqs = np.array([10.]).reshape(-1,1)
x = np.linspace(0,1,62, endpoint=False).reshape(-1,1)
s1 = np.sin(2*np.pi*(freqs@x.T)).sum(axis=0)
s2 = np.sin(2*np.pi*(freqs@x.T)+np.pi/2).sum(axis=0)
from matplotlib import pyplot as plt
# plt.phase_spectrum(s1*s2, Fs=600)
# plt.show()
# print(freqs, freqs.shape)
spec = fft.rfft(s1*s2)
# spec = spec[:len(spec)//2]
_, ax = plt.subplots(nrows=3, ncols=1)
ax[0].plot(s1, label='1')
ax[0].plot(s2, label='2')
ax[0].plot(s1-fft.irfft(spec), label='1-ifft')
ax[0].legend()

ax[1].plot(np.angle(spec)/np.pi)
ax[2].plot(np.abs(spec)/len(x)*2)
print(np.arccos(np.abs(spec[0])/len(x)*2))
# plt.show()
