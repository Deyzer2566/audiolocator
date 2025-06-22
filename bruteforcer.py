from numpy import fft
import numpy as np
def find_phases(s1, s2, Fs, threshold):
    spec1 = fft.rfft(s1, n=Fs)
    spec2 = fft.rfft(s2, n=Fs)
    catched_freqs = np.array(np.where(np.logical_and(np.abs(spec1)/Fs*2 > threshold, np.abs(spec2)/Fs*2 > threshold))[0])
    delta_phases = np.angle(spec2)[catched_freqs] - np.angle(spec1)[catched_freqs]
    return delta_phases, catched_freqs