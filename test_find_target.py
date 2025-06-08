from bruteforcer import find_phases
import numpy as np

speed = 330

def distance(p1, p2):
    return np.sqrt(((p1-p2)**2).sum())

mic1 = np.array([0,0])
mic2 = np.array([0,1])
target = np.array([10,-3])
dist = distance((mic1+mic2)/2, target)

target_freqs = np.array([10, 13])
Fs = (target_freqs.max()+1)*2
x = np.linspace(0,2,Fs*2, endpoint=False)
t = dist/speed
phase1 = t - np.floor(t)
s1 = np.sin(2*np.pi*(target_freqs.reshape(-1,1)@x.reshape(1,-1)) + phase1*2*np.pi).sum(axis=0)
t = distance(mic2, target)/speed
phase2 = t-np.floor(t)
s2 = np.sin(2*np.pi*(target_freqs.reshape(-1,1)@x.reshape(-1,1).T) + phase2*2*np.pi).sum(axis=0)
targets = find_phases(s1, s2, Fs, 1e-3)
targets = targets[0]/np.pi
targets = targets*speed/distance(mic1,mic2)
print('calc',np.arccos(targets))
print('true',np.arccos(-(distance(mic1, target)**2 - distance(mic1,mic2)**2 - distance(mic2,target)**2)/distance(mic1,mic2)/distance(mic2,target)/2))
