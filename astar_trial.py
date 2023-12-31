import json, os, math, random, shutil
from heapq import heappush, heappop

import numpy as np

from utils import *

SEARCH_SIZE = 25
SEARCH_DEPTH = 10000
NORM = 1
MFCC = False

print('Collecting neighbors...')
with open(f'msd-data/neighbors-{SEARCH_SIZE}-l={NORM}{"-f=mfcc" if MFCC else ""}.json', 'r') as f:
    neighbors = json.load(f)

print('Collecting features...')
with open(f'msd-data/{"mfcc-" if MFCC else ""}features.json', 'r') as f:
    features = json.load(f)

if MFCC:
    print('Converting to numpy...')
    for k, v in features.items():
        features[k] = np.array(v)

# set of all songs
all_songs = list(features)

RESULTS_FOLDER = f'msd-results/results-n={SEARCH_SIZE}-d={SEARCH_DEPTH}-l={NORM}{"-f=mfcc" if MFCC else ""}'

# optionally clear the results folder before running this trial
# if os.path.isdir(RESULTS_FOLDER):
    # shutil.rmtree(RESULTS_FOLDER)

# os.mkdir(f'{RESULTS_FOLDER}')

if MFCC:
    if NORM == 1:
        norm_func = array_distance_l1
    elif NORM == 2:
        norm_func = array_distance_l2
else:
    if NORM == 1:
        norm_func = feature_distance_l1
    elif NORM == 2:
        norm_func = feature_distance_l2

SHOULD_PRINT = False
log_m = log(SHOULD_PRINT)

# runs one iteration of A* search for the given source and target songs
def run_search(SOURCE_ID: str, TARGET_ID: str):
    source_feats = features[SOURCE_ID]
    target_feats = features[TARGET_ID]

    log_m(f'{bcolors.OKCYAN}{bcolors.BOLD}SOURCE: {SOURCE_ID} | GOAL: {TARGET_ID}{bcolors.ENDC}')
    log_m(f'{bcolors.OKCYAN}Ideal straight-line cost: {norm_func(source_feats, target_feats)}{bcolors.ENDC}')

    explored = set([])

    frontier = [(-1, SOURCE_ID)]
    path: dict[str, tuple[float, str]] = {SOURCE_ID: (0, None)}

    log_m(f'{bcolors.OKCYAN}Search Parameters: {SEARCH_SIZE=} | {SEARCH_DEPTH=} | {NORM=}{bcolors.ENDC}')
    printsep(SHOULD_PRINT)

    search_iter = 0
    search_id = ''

    while search_iter < SEARCH_DEPTH and search_id != TARGET_ID:
        try:
            total_cost, search_id = heappop(frontier)
        except IndexError:
            log_m(f'Search for {SOURCE_ID} to {TARGET_ID} ended early on iteration {search_iter}')
            break

        if search_id in explored:
            continue
        
        explored.add(search_id)

        log_m(f'Iteration: {search_iter} | Song: {search_id} | Total cost: {total_cost:.4f}')
        
        search_feats = features[search_id]
        neighbor_ids = neighbors[search_id]

        for id in neighbor_ids:
            feats = features[id]
            # update frontier
            heuristic_cost = norm_func(target_feats, feats)
            # cost from search origin to this song, plus cost from start to search origin
            path_cost = norm_func(search_feats, feats) + path[search_id][0]
            heappush(frontier, ((path_cost + heuristic_cost), id))

            # update path
            if id in path:
                path[id] = (path_cost, search_id) if path_cost < path[id][0] else path[id]
            else:
                path[id] = (path_cost, search_id)

        search_iter += 1
    
    printsep(SHOULD_PRINT)

    found_path = search_id == TARGET_ID

    # if no direct path could be found, approximate using the closest song to the target that we've seen
    if not found_path:     
        log_m(f'{bcolors.FAIL}{bcolors.BOLD}No path found :({bcolors.ENDC}')
        log_m("Approximating search path...")

        closest_to_target = None
        closest_distance = math.inf
        closest_feats = None
        
        for id in explored:
            if feats is None:
                continue

            distance = norm_func(target_feats, feats)
            if distance < closest_distance:
                closest_distance = distance
                closest_to_target = id
                closest_feats = feats
        
        log_m(f"Using song {closest_to_target} as the target (distance from target: {closest_distance})...")

        solution_path = backtrace(path, closest_to_target, SOURCE_ID)

    else:
        log_m(f'{bcolors.OKGREEN}{bcolors.BOLD}Found a path!{bcolors.ENDC}')
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
        'SOURCE_FEATS': to_json(source_feats),
        'TARGET_FEATS': to_json(target_feats),
        'APPROX_FEATS': None if found_path else to_json(closest_feats),
        'PATH': solution_path,
        'ITERATIONS_REQUIRED': search_iter
    }

    with open(f'{RESULTS_FOLDER}/{SOURCE_ID}-{TARGET_ID}.json', 'w') as f:
        json.dump(data, f, indent=4)

    printsep(SHOULD_PRINT)

iters = 5000
print(f'Performing {iters} searches... | timestamp: {timenow()}')
for i in range(iters): 
    if len(all_songs) < 2:
        break

    if i % 10 == 0:
        print(f'>> Searching #{i}/{iters}... | timestamp: {timenow()}', end='\r')

    src, dst = random.choices(all_songs, k=2)
    
    if src == dst:
        continue
    if os.path.isfile(f'{RESULTS_FOLDER}/{src}-{dst}.json'):
        continue

    run_search(src, dst)