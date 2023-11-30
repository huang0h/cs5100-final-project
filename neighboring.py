import numpy as np
import heapq, json, os, sys

from utils import *

NEIGHBOR_COUNT = 25

with open('msd-data/features.json', 'r') as f:
    all_feats = json.load(f)

SONG_COUNT = len(all_feats)

# https://medium.com/@datasc.yash/using-spotifys-web-api-to-extract-high-level-features-and-download-song-previews-38b0b1728a8f
# get scheming :)

all_neighbors = {}
neighbor_array = [None for _ in range(SONG_COUNT)]

for n, (id, feats) in enumerate(all_feats.items()):
    if n % 250 == 0:
        print(f'Calculating neighbors for song #{n}...')

    for i, (other, other_feats) in enumerate(all_feats.items()):
        if other == id:
            neighbor_array[i] = (id, np.inf)
        else:
            neighbor_array[i] = (other, feature_distance_l2(feats, other_feats))
    
    neighbor_array.sort(key=lambda t: t[1])
    
    all_neighbors[id] = [t[0] for t in neighbor_array[:NEIGHBOR_COUNT]]

with open(f'msd-data/neighbors-{NEIGHBOR_COUNT}.json', 'w') as f:
    json.dump(all_neighbors, f, indent=2)