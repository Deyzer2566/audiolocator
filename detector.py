import numpy as np
from bruteforcer import find_phases
speed = 330
def detect_targets(s1, s2, Fs, distance_between_micros):
    targets = find_phases(s1, s2, Fs, 1e-3)
    targets = targets[0]/np.pi
    targets = targets*speed/distance_between_micros
    return targets