import time
import numpy as np


def main(a,b):
    c = np.array([a,b])
    rng = np.random.default_rng()
    c += rng.random()  
    
    return {
        'solC':c,
        'test':2
    }