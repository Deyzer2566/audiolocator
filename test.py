import serial
Fs = 8000
a = serial.Serial('COM5', 200000, timeout=400/Fs)
d = []
import time
t = time.time()
p = 0
import numpy as np
from numpy.fft import rfft
while(True):
    try:
        d += a.read(807)
        d = d[d.index(0x69):]
        if len(d) < 1+1+800+4+1:
            print('wow')
            raise ValueError
        data = d[:1+1+800+4+1]
        d = d[1:]
        if data[-1] != 0x96:
            raise ValueError
        s = int.from_bytes(data[1+1+800:1+1+800+4], 'little')
        if s != sum(data[2:2+800]):
            raise ValueError
        d = d[807-1:]
        if((p+1)%256 != data[1]):
            print('lel',p,data[1])
        p = data[1]
        # data = data[2:800+2]
        # data = [int.from_bytes(data[i:i+2], byteorder='big') for i in range(0,len(data),2)]
        # print(np.abs(rfft(data)[int(1000/Fs*400)])/400*2)
        c = time.time()
        if c-t > 0:
            print(400/(c-t), c-t)
        t=c
    except ValueError:
        continue
