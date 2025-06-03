import serial
a = serial.Serial('COM5', 115200, timeout=0.1)
i = 0
d = []
out = ""
while(True):
    try:
        d += a.read(900)
        d = d[d.index(0x13):]
        data = d[1:d.index(0x13, 1)]
        d = d[d.index(0x13,1):]
        data = [data[0]]+[data[i] if data[i-1] != 0xdd else (0x13 if data[i] == 0x15 else '0xdd') for i in range(1,len(data))]
        data = list(filter(lambda x: x != 0xdd, data))
        data = [i if i != '0xdd' else 0xdd for i in data]
        s = int.from_bytes(data[801:], 'little')
        print(len(data))
        print(data[800], sum(data[:800]), s, sum(data[:800]) == s)
        data = data[:800]
        data = [int.from_bytes(data[i:i+2], byteorder='big') for i in range(0,len(data),2)]
        print(max(data))
        out += '\n'.join(map(str, data))+'\n'
    except ValueError:
        continue
    except KeyboardInterrupt:
        with open('out.csv', 'w') as f:
            f.write(out)
        break