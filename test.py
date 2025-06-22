import serial
Fs = 4000
a = serial.Serial('COM5', 200000, timeout=1)
d = []
import time
t = time.time()
p = 0
import numpy as np
from struct import unpack
adc_values_count_in_packet = 200
packet_format = "<BB"+"H"*adc_values_count_in_packet*2+"HIB"
packet_size = packet_format.upper().count('B') + packet_format.upper().count('H')*2 + packet_format.upper().count('I')*4
channel1_data = []
channel2_data = []
from detector import detect_targets
from matplotlib import pyplot as plt
plt.ion()
freq = 400
while(True):
    try:
        d += a.read(packet_size)
        d = d[d.index(0x69):]
        if len(d) < packet_size:
            print('half packet')
            raise ValueError
        data = d[:packet_size]
        d = d[1:]
        if data[-1] != 0x96:
            raise ValueError
        packet = unpack(packet_format, bytes(data))
        if packet[-2] != sum(packet[2:-3]):
            print('bad sum', data[1], packet[-2], sum(packet[2:-3]))
            raise ValueError
        d = d[packet_size-1:]
        if((p+1)%256 != data[1]):
            print('bad number',p,data[1])
        p = data[1]
        ch1 = np.array(packet[2:402:2])
        ch2 = np.array(packet[2+1:402:2])
        channel1_data += ch1.tolist()
        channel2_data += ch2.tolist()
        if len(channel1_data) >= Fs and len(channel2_data) >= Fs:
            channel1_data = np.array(channel1_data)
            channel2_data = np.array(channel2_data)

            targets, freqs = detect_targets(channel1_data, channel2_data, Fs, 0.017, 1)

            freqs = freqs[np.abs(targets)<=1.]
            targets = targets[np.abs(targets)<=1.]
            targets = np.arccos(targets)
            plt.cla()
            start = [0,0]
            end = [1,0]
            plt.plot([start[0], end[0]], 
                    [start[1],end[1]], 
                    'b-', linewidth=2, label='Линия')
            print(len(targets))
            for i in targets:
                # Вычисляем конечную точку луча
                end_x = start[0] + 1 * np.cos(i)
                end_y = start[1] + 1 * np.sin(i)
                
                # Рисуем луч
                plt.plot([start[0], end_x], 
                        [start[1], end_y], 
                        '--', linewidth=1.5)#, 
                        # label=f'Угол {i}rad')
                
                # Вычисляем конечную точку отраженного луча
                end_x = start[0] + 1 * np.cos(-i)
                end_y = start[1] + 1 * np.sin(-i)
                
                # Рисуем луч
                plt.plot([start[0], end_x], 
                        [start[1], end_y], 
                        '-.', linewidth=1.5)#, 
                        # label=f'Угол {i}rad')
            plt.draw()
            plt.pause(0.1)
            # c = time.time()
            # if c-t > 0:
            #     print('freq', Fs/(c-t), c-t, flush=True)
            # t=c
            channel1_data = []
            channel2_data = []
    except ValueError:
        continue
    except KeyboardInterrupt:
        break
