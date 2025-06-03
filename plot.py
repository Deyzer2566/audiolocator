from matplotlib import pyplot as plt
with open('out.csv') as f:
    s = f.read()
s = s.split()
s = list(map(int,s))
print(max(s))
_, ax = plt.subplots(2, 1)
ax[0].plot(s)
ax[1].specgram(s, Fs=3968)
plt.show()