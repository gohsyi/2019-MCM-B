from config import config
from itertools import permutations

for bay in config.bays:
    for med in config.meds:
        maximal = None
        W = config.width[bay]
        H = config.height[bay]
        L = config.length[bay]
        w = config.width[med]
        h = config.height[med]
        l = config.length[med]
        for ww, hh, ll in permutations([w, h, l]):
            n = min((W // ww) * (H // hh) * (L // ll), config.weight[bay] // config.weight[med])
            if not maximal or maximal[0] < n:
                maximal = n, ww, hh, ll

        print(med, 'in', bay, 'maximal:', maximal[0])
