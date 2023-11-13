#! /usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json, time, sys, os
from heapq import heappush, heappop
from utils import *

# SPOTIPY_CLIENT_ID = '0387ebd733aa4a8e97ab976f87422cf1'
# SPOTIPY_CLIENT_SECRET = '0fbdb2b2366c4d44b01a7fb28c882de0'

SPOTIPY_CLIENT_ID = 'dfa8b23916c140f5b7c7572da25c4734'
SPOTIPY_CLIENT_SECRET = 'e65a6c357d80435fb629f41677abff3f'

# if os.path.isfile('.cache'):
#     os.remove('.cache')

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

SOURCE_ID = '3RDfWxok6okDp9WtTCVPJR'
TARGET_ID = '71IzhN7H8ZkCIMotAjSHNk'

source_feats = normalized_features(sp.audio_features(tracks=[SOURCE_ID])[0])
target_feats = normalized_features(sp.audio_features(tracks=[TARGET_ID])[0])

print(f'Ideal straight-line cost: {feature_distance(source_feats, target_feats)}')
print(f'SOURCE: {SOURCE_ID} | GOAL: {TARGET_ID}')

features: dict[str, dict[str, float]] = {SOURCE_ID: source_feats}
# min-heap of (heuristic, ID)
frontier = [(-1, SOURCE_ID)]
# tracks best search path up until a given song
# dict of song: (cost to previous song, previous)
path: dict[str, tuple[float, str]] = {SOURCE_ID: (0, None)}

SEARCH_SIZE = 10
SEARCH_DEPTH = 200

print(f'Search Parameters: {SEARCH_SIZE=} | {SEARCH_DEPTH=}')
print(f'\n-----------------------------------------------\n')

search_iter = 0
search_id = ''
while search_iter < SEARCH_DEPTH and search_id != TARGET_ID:

    x = heappop(frontier)
    total_cost, search_id = x
    print(f'Iteration: {search_iter} | Song: {search_id} | Total cost: {total_cost:.4f}')

    local_source_feats = features[search_id]
    neighbors = sp.recommendations(seed_tracks=[search_id], limit=SEARCH_SIZE)

    neighbor_ids = ids_from_tracks(neighbors)
    to_request = [id for id in neighbor_ids if id not in features]
    new_features = sp.audio_features(tracks=to_request)

    for id, track_feats in zip(to_request, new_features):
        if track_feats is None:
            features[id] = None
        else:
            features[track_feats['id']] = normalized_features(track_feats)

    for id in neighbor_ids:
        feats = features[id]
        if feats == None:
            continue
        
        # update frontier
        heuristic_cost = feature_distance(target_feats, feats)
        # cost from search origin to this song, plus cost from start to search origin
        path_cost = feature_distance(local_source_feats, feats) + path[search_id][0]
        heappush(frontier, ((path_cost + heuristic_cost), id))

        # update path
        if id in path:
            path[id] = (path_cost, search_id) if path_cost < path[id][0] else path[id]
        else:
            path[id] = (path_cost, search_id)

        # sleep to avoid a timeout from the API
        time.sleep(1.2)
    
    search_iter += 1

print('--------------------------------------------------------')

found_path = search_id == TARGET_ID

if not found_path:
    print('No path found :(')
    print("Approximating search path...")

    closest_to_target = None
    closest_distance = 999999
    closest_feats = None
    
    for id, feats in features.items():
        if feats is None:
            continue

        distance = feature_distance(target_feats, feats)
        if distance < closest_distance:
            closest_distance = distance
            closest_to_target = id
            closest_feats = feats
    
    print(f"Using song {closest_to_target} as the target (distance from target: {closest_distance})...")
    solution_path = backtrace(path, closest_to_target, SOURCE_ID)

else:
    print('Found a path!')
    solution_path = backtrace(path, TARGET_ID, SOURCE_ID)

data = {
    'meta': {
        'SOURCE_ID': SOURCE_ID,
        'TARGET_ID': TARGET_ID,
        'FOUND': search_id == TARGET_ID,
        'APPROX': None if found_path else closest_to_target,
        'SEARCH_DEPTH': SEARCH_DEPTH,
        'SEARCH_SIZE': SEARCH_SIZE,
    },
    'SOURCE_FEATS': source_feats,
    'TARGET_FEATS': target_feats,
    'APPROX_FEATS': None if found_path else closest_feats,
    'PATH': solution_path,
    'ITERATIONS_REQUIRED': search_iter
}

with open(f'results/{SOURCE_ID}-{TARGET_ID}.json', 'w') as f:
    json.dump(data, f, indent=4)
