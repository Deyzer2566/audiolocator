from bruteforcer import find_phases
import numpy as np

speed = 330

def distance(p1, p2):
    return np.sqrt(((p1-p2)**2).sum())

mic1 = np.array([0,0])
mic2 = np.array([0,0.015])
target = np.array([0.20,0])# координаты в сантиметрах
dist = distance((mic1+mic2)/2, target)

target_freqs = np.array([10, 13])
Fs = (target_freqs.max()+1)*2
x = np.linspace(0,2,Fs*2, endpoint=False)
t1 = distance(mic1, target)/speed
s1 = np.sin(2*np.pi*(target_freqs.reshape(-1,1)@(x+t1).reshape(1,-1))).sum(axis=0)
t2 = distance(mic2, target)/speed
s2 = np.sin(2*np.pi*(target_freqs.reshape(-1,1)@(x+t2).reshape(1,-1))).sum(axis=0)
from detector import detect_targets
print('calc',np.arccos(detect_targets(s1,s2,Fs,distance(mic1,mic2),0.1)[0])/np.pi*180)
print('true',np.arccos(-(distance(mic1, target)**2 - distance(mic1,mic2)**2 - distance(mic2,target)**2)/distance(mic1,mic2)/distance(mic2,target)/2)/np.pi*180)
