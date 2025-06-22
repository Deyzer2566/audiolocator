import numpy as np
from bruteforcer import find_phases
speed = 330
def detect_targets(s1, s2, Fs, distance_between_micros, amplitude_threshold):
    deltas, freqs = find_phases(s1, s2, Fs, amplitude_threshold)
    if 0 in freqs:
        deltas = deltas[1:]
        freqs = freqs[1:]
    targets = deltas/(2*np.pi*freqs)
    targets = targets*speed/distance_between_micros
    return targets, freqs