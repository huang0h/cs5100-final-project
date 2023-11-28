import json, os, sys, time, math, random
from heapq import heappush, heappop

from utils import *

SEARCH_SIZE = 25
SEARCH_DEPTH = 1000
NORM = 1

with open(f'msd-data/neighbors-{SEARCH_SIZE}.json', 'r') as f:
    neighbors = json.load(f)

with open('msd-data/features.json', 'r') as f:
    features = json.load(f)

# set of all songs
all_songs = list(features)
# random.shuffle(all_songs)

RESULTS_FOLDER = f'msd-results/results-n={SEARCH_SIZE}-d={SEARCH_DEPTH}-l={NORM}'
os.mkdir(f'{RESULTS_FOLDER}')

if NORM == 1:
    norm_func = feature_distance_l1
elif NORM == 2:
    norm_func = feature_distance_l2

def run_search(SOURCE_ID: str, TARGET_ID: str, feedback: bool = True):
    source_feats = normalized_features(features[SOURCE_ID])
    target_feats = normalized_features(features[TARGET_ID])

    if feedback:
        print(f'{bcolors.OKCYAN}{bcolors.BOLD}SOURCE: {SOURCE_ID} | GOAL: {TARGET_ID}{bcolors.ENDC}')
        print(f'{bcolors.OKCYAN}Ideal straight-line cost: {norm_func(source_feats, target_feats)}{bcolors.ENDC}')

    explored = set([])

    frontier = [(-1, SOURCE_ID)]
    path: dict[str, tuple[float, str]] = {SOURCE_ID: (0, None)}

    if feedback:
        print(f'{bcolors.OKCYAN}Search Parameters: {SEARCH_SIZE=} | {SEARCH_DEPTH=} | {NORM=}{bcolors.ENDC}')
        printsep()

    search_iter = 0
    search_id = ''

    while search_iter < SEARCH_DEPTH and search_id != TARGET_ID:
        total_cost, search_id = heappop(frontier)

        if feedback:
            print(f'Iteration: {search_iter} | Song: {search_id} | Total cost: {total_cost:.4f}')

        explored.add(search_id)
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
    
    if feedback:
        printsep()

    found_path = search_id == TARGET_ID

    if not found_path:
        if feedback:
            print(f'{bcolors.FAIL}{bcolors.BOLD}No path found :({bcolors.ENDC}')
            print("Approximating search path...")

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
        
        if feedback:
            print(f"Using song {closest_to_target} as the target (distance from target: {closest_distance})...")

        solution_path = backtrace(path, closest_to_target, SOURCE_ID)

    else:
        if feedback:
            print(f'{bcolors.OKGREEN}{bcolors.BOLD}Found a path!{bcolors.ENDC}')
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

    with open(f'{RESULTS_FOLDER}/{SOURCE_ID}-{TARGET_ID}.json', 'w') as f:
        json.dump(data, f, indent=4)

    if feedback:
        printsep()

for i in range(3000):
    if len(all_songs) < 2:
        break

    if i % 250 == 0:
        print(f'Searching song #{i}...')

    src, dst = random.choices(all_songs, k=2)
    if os.path.isfile(f'{RESULTS_FOLDER}/{src}-{dst}.json'):
        continue

    if src == dst:
        continue

    run_search(src, dst, feedback=False)