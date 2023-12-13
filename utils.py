import math, time, json, os
import numpy as np

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MIN_KEY = 0
MAX_KEY = 11

MIN_DB = -60
MAX_DB = 0

MIN_TEMPO = 30
MAX_TEMPO = 240

MIN_TIME_SIGNATURE = 3
MAX_TIME_SIGNATURE = 7

AUDIO_FEATURES = [
    'acousticness', 
    'danceability', 
    'energy', 
    'instrumentalness', 
    'key', 
    'liveness', 
    'loudness', 
    'mode', 
    'speechiness', 
    'tempo', 
    'time_signature', 
    'valence',
    'key_confidence',
    'mode_confidence',
    'time_signature_confidence',
]

def printsep(should_print: bool = True):
    if should_print:
        print(f'\n-----------------------------------------------------------------\n')

def timenow():
    return time.strftime("%I:%M:%S", time.localtime())

def log(should_print: bool):
    return (lambda x: print(x)) if should_print else (lambda x: x)

def collect_mfcc_features(FEATS_DIR: str, feedback: bool = True) -> dict[str, np.ndarray]:
    if feedback:
        print(f'Collecting MFCC features from {FEATS_DIR}...')
    all_feats = {}

    for i, feat_file in enumerate(os.listdir(FEATS_DIR)):
        if i % 100 == 0:
            print(f'>> Collecting song #{i}...', end='\r')

        with open(f'{FEATS_DIR}/{feat_file}') as f:
            array = json.load(f)
            array = np.ravel(array)
            
            all_feats[feat_file.strip('.json')] = array
    
    print('')
    return all_feats

def clamp(val: float, min_v: float, max_v: float) -> float:
    return max(min(val, max_v), min_v)

def ids_from_tracks(response) -> list[str]:
    return [t['uri'].strip('spotify:track:') for t in response['tracks'] if t['uri']]

def normalized_features(analysis: dict | None) -> dict[str, float] | None:
    if analysis == None:
        return None
    
    norm_features = {}

    for key, val in analysis.items():
        # print(key)
        if key not in AUDIO_FEATURES:
            continue

        if key == 'key':
            if val == -1:
                norm_features[key] = val
            else:
                norm_features[key] = (clamp(val, MIN_KEY, MAX_KEY) - MIN_KEY) / (MAX_KEY - MIN_KEY)
        elif key == 'loudness':
            norm_features[key] = (clamp(val, MIN_DB, MAX_DB) - MIN_DB) / (MAX_DB - MIN_DB)
        elif key == 'tempo':
            norm_features[key] = (clamp(val, MIN_TEMPO, MAX_TEMPO) - MIN_TEMPO) / (MAX_TEMPO - MIN_TEMPO)
        elif key == 'time_signature':
            norm_features[key] = (clamp(val, MIN_TIME_SIGNATURE, MAX_TIME_SIGNATURE) - MIN_TIME_SIGNATURE) / (MAX_TIME_SIGNATURE - MIN_TIME_SIGNATURE)
        else:
            norm_features[key] = val

    return norm_features

def feature_distance_l1(target_features: dict, test_features: dict) -> float:
    sum = 0
    
    for feat in AUDIO_FEATURES:
        if not (feat in target_features and feat in test_features):
            continue

        sum += abs(target_features[feat] - test_features[feat])
    
    return sum

def feature_distance_l2(target_features: dict, test_features: dict) -> float:
    sum = 0

    # print(target_features)
    # print(test_features)

    for feat in AUDIO_FEATURES:
        if not (feat in target_features and feat in test_features):
            continue

        sum += (target_features[feat] - test_features[feat]) ** 2
        
    return sum ** 0.5

def array_distance_l1(target_features: np.ndarray, test_features: np.ndarray) -> float:
    return np.sum(np.abs(target_features - test_features))

def array_distance_l2(target_features: np.ndarray, test_features: np.ndarray) -> float:
    return np.sqrt(np.sum(np.power(target_features - test_features, 2)))

def backtrace(path: dict, target_id: str, source_id: str):
    sol_path = []

    next = target_id
    while next != source_id:
        sol_path.append(next)
        next = path[next][1]

    return sol_path[::-1]

def to_json(o: dict | np.ndarray):
    if type(o) == dict:
        return o
    elif type(o) == np.ndarray:
        return o.tolist()

def json_features_to_np(features: dict | list) -> np.ndarray:
    feat_list = [features[feat] for feat in AUDIO_FEATURES if feat in features]
    return np.array(feat_list)