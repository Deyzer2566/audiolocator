import serial
a = serial.Serial('COM5', 200000, timeout=400/(1000000/(239.5+12.5)))
d = []
from matplotlib import pyplot as plt
plt.ion()
plot_data = []
import time
t = time.time()
p = 0
import numpy as np
from numpy.fft import rfft
_, ax = plt.subplots(nrows=1, ncols=2)
while(True):
    try:
        d += a.read(807)
        d = d[d.index(0x69):]
        if len(d) < 1+1+800+4+1:
            raise ValueError
        data = d[:1+1+800+4+1]
        d = d[1:]
        if data[-1] != 0x96:
            raise ValueError
        s = int.from_bytes(data[1+1+800:1+1+800+4], 'little')
        if s != sum(data[2:2+800]):
            raise ValueError
        if((p+1)%256 != data[1]):
            print('lel',p,data[1])
        p = data[1]
        data = data[2:800+2]
        data = [int.from_bytes(data[i:i+2], byteorder='big') for i in range(0,len(data),2)]
        plot_data += data
        if len(plot_data) > 400*3:
            c = time.time()
            # print(len(plot_data)/(c-t))
            t = c
            plt.pause(0.01)
            for i in ax:
                i.cla()
            plot_data = np.array(plot_data).astype(np.float32)/4096*3.3
            ax[0].plot(plot_data)
            ax[1].plot(np.abs(rfft(plot_data)[1:])/len(plot_data)*2)
            plt.draw()
            plot_data = []
    except ValueError:
        continue
