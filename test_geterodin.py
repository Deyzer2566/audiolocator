import numpy as np
from numpy import random
from numpy import fft
#cos a * cos b = 1/2(cos(a+b)+cos(a-b))
#sin a * cos b = 1/2(sin(a+b)+sin(a-b))
#sin a * sin b = 1/2(cos(a-b)-cos(a+b))
#sin (ax-l) * sin (ax-d) = 1/2(cos(ax-l-ax+d)-cos(ax-l+ax-d)) = 1/2(cos(-l+d)-cos(2ax-(d+l)))
#cos (ax-l) * cos (ax-d) = 1/2(cos(2ax-(d+l)) + cos(d-l))

#(cos ax + cos bx) * (cos (ax+d) + cos(bx+c)) = 
#cos ax * cos(ax+d) + cos ax * cos(bx+c) + cos bx * cos(ax+d) + cos bx * cos(bx+c)
#1/2(cos(d)+cos(2ax+d)+cos((a-b)x+c))+cos((a+b)x+c)+cos((b-a)x+d)+cos((b+a)x+d)+cos c + cos(2bx+c)

# freqs = random.randint(100, 300, random.randint(2,10)).reshape(-1,1)
freqs = np.array([10.,13.])
T = 2
P = int((np.ceil(freqs.max()+1))*2*2)
phase1 = np.array([1,1])
phase2 = np.array([-np.pi/6,-np.pi/6])
# lag = np.round((phase2%(2*np.pi))/(2*np.pi*freqs)*P).astype(np.int32)
# phase2 = lag.astype(np.float32)*(2*np.pi*freqs)/P
# if phase2 > np.pi:
#     phase2 = phase2 - 2*np.pi
x = np.linspace(0,T,int(T*P), endpoint=False).reshape(-1,1)
s1 = np.cos(2*np.pi*(freqs.reshape(-1,1)@x.T)+phase1.reshape(-1,1)).sum(axis=0)
s2 = np.cos(2*np.pi*(freqs.reshape(-1,1)@x.T)+phase2.reshape(-1,1)).sum(axis=0)
# for k,i in enumerate(lag):
#     s2[k,:i] = 0
from matplotlib import pyplot as plt
smesitel = s1*s2
spec = fft.rfft(smesitel, n=P)
graphs = [s1, s2, smesitel]
_, ax = plt.subplots(nrows=len(graphs), ncols=3)
for k, i in enumerate(graphs):
    ax[k,0].plot(i[:P])
    ax[k,1].plot(np.abs(fft.rfft(i, n=P))/P*2)
    ax[k,2].plot(np.angle(fft.rfft(i, n=P)))

threshold = 1e-3
catched_freqs = np.where(np.abs(spec)/P*2 > threshold)
peaks = spec[catched_freqs]
matrix = np.concatenate((np.array(catched_freqs).reshape(-1,1), np.angle(peaks).reshape(-1,1)), axis=1)
if 0 in catched_freqs[0]:
    matrix[0,1] = np.arccos(np.abs(spec[0])/P*2)
print(matrix, matrix.shape)

print('phase1', np.angle(fft.rfft(s1, n=P))[freqs.astype(np.int32)])
print('phase2', np.angle(fft.rfft(s2, n=P))[freqs.astype(np.int32)])
print('calc phase', np.angle(spec)[freqs.astype(np.int32)*2])
print('phases sum', phase1+phase2)
print('phases sub', phase1-phase2)
# plt.show()
