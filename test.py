import serial
Fs = 8000
a = serial.Serial('COM5', 200000, timeout=1)
d = []
import time
t = time.time()
p = 0
import numpy as np
from numpy.fft import rfft
from struct import unpack
adc_values_count_in_packet = 200
packet_format = "<BB"+"H"*adc_values_count_in_packet*2+"HIB"
packet_size = packet_format.upper().count('B') + packet_format.upper().count('H')*2 + packet_format.upper().count('I')*4
while(True):
    try:
        d += a.read(packet_size)
        d = d[d.index(0x69):]
        if len(d) < packet_size:
            print('wow')
            raise ValueError
        data = d[:packet_size]
        d = d[1:]
        if data[-1] != 0x96:
            raise ValueError
        packet = unpack(packet_format, bytes(data))
        if packet[-2] != sum(packet[2:-2]):
            print('was', data[1], packet[-2], sum(data[2:2+800]))
            raise ValueError
        d = d[packet_size-1:]
        if((p+1)%256 != data[1]):
            print('lel',p,data[1])
        p = data[1]
        ch1 = np.array(packet[2:-2:2])
        ch2 = np.array(packet[2+1:-2:2])
        print('###')
        print(ch1[:5], ch2[:5])
        print(p, np.array(ch1).mean(), np.array(ch2).mean())
        # print(np.abs(rfft(ch1)[int(1000/Fs*adc_values_count_in_packet)])/adc_values_count_in_packet*2,
        #     np.abs(rfft(ch2)[int(1000/Fs*adc_values_count_in_packet)])/adc_values_count_in_packet*2)
        
        c = time.time()
        if c-t > 0:
            print('freq', adc_values_count_in_packet/(c-t), c-t)
        t=c
    except ValueError:
        continue
    except KeyboardInterrupt:
        break
