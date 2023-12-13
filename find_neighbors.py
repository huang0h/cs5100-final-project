import numpy as np
import json

from utils import *

neighbors = [(10, {}), (25, {}), (40, {})]
NORM = 2

if NORM == 1:
    distance_function = array_distance_l1
else:
    distance_function = array_distance_l2

print('Collecting features...')

with open('msd-data/mfcc-features.json', 'r') as f:
    all_feats = json.load(f)

print('Converting to numpy...')

for k, v in all_feats.items():
    all_feats[k] = np.array(v)

SONG_COUNT = len(all_feats)

neighbor_array = [None for _ in range(SONG_COUNT)]

print('')
print(f'Calculating neighbors... | timestamp: {timenow()}')

for n, (id, feats) in enumerate(all_feats.items()):
    if n % 10 == 0:
        print(f'>> Calculating neighbors for song #{n}/{SONG_COUNT}... | timestamp: {timenow()}', end='\r')

    for i, (other, other_feats) in enumerate(all_feats.items()):
        if other == id:
            neighbor_array[i] = (id, np.inf)
        else:
            neighbor_array[i] = (other, distance_function(feats, other_feats))
    
    neighbor_array.sort(key=lambda t: t[1])

    for count, set in neighbors:
        set[id] = [t[0] for t in neighbor_array[:count]]

for count, set in neighbors:
    print(f'Writing file for {count} neighbors...')
    with open(f'msd-data/neighbors-{count}-l={NORM}-f=mfcc.json', 'w') as f:
        json.dump(set, f, indent=2)