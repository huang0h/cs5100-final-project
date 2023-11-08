#! /usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json, time, sys
from heapq import heappush, heappop
from utils import *

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

SOURCE_ID = '4um6CPDIxnNWSEbj3LJQhQ'
TARGET_ID = '0TiZDNPU2t4STNJW4Qdj22'

source_feats = normalized_features(sp.audio_features(tracks=[SOURCE_ID])[0])
target_feats = normalized_features(sp.audio_features(tracks=[TARGET_ID])[0])

print(f'Ideal straight-line cost: {feature_distance(source_feats, target_feats)}')
print(f'GOAL:')

# explored_songs = {SOURCE_ID}
features: dict[str, str] = {SOURCE_ID: source_feats}
# min-heap of (heuristic, ID)
frontier = [(-1, SOURCE_ID)]
# tracks best search path up until a given song
# dict of song: (cost to previous song, previous)
path: dict[str, tuple[float, str]] = {SOURCE_ID: (0, None)}

SEARCH_SIZE = 10
SEARCH_DEPTH = 100

search_iter = 0
search_id = ''
while search_iter < SEARCH_DEPTH and search_id != TARGET_ID:

    x = heappop(frontier)
    print(x)
    _, search_id = x

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

        # if id in explored_songs:
        #     feats = explored_songs[id]
        # else:
        #     feats = normalized_features(sp.audio_features(tracks=[id])[0])
        #     if feats == None:
        #         # print(f'Failed to process song: {id}')
        #         continue

        feats = features[id]
        if feats == None:
            continue

        # explored_songs[id] = feats
        # explored_songs.add(id)
        
        # udpate frontier
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
        time.sleep(0.25)
        search_iter += 1

if search_id != TARGET_ID:
    print('No path found :(')
else:
    print('Found a path!')
    solution_path = backtrace(path, TARGET_ID, SOURCE_ID)


