import tables, json, os, sys

from utils import *

def song_features(file: tables.File) -> dict:
    cols = file.root.analysis.songs.cols
    feats = {
        'danceability': cols.danceability[0],
        'energy': cols.energy[0],
        'key': cols.key[0],
        'key_confidence': cols.key_confidence[0],
        'mode': cols.mode[0],
        'mode_confidence': cols.mode_confidence[0],
        'loudness': cols.loudness[0],
        'tempo': cols.tempo[0],
        'time_signature': cols.time_signature[0],
        'time_signature_confidence': cols.time_signature_confidence[0]
    }

    feats = normalized_features(feats)

    for k, v in feats.items():
        feats[k] = float(v)

    return feats

# def write_feats(path: str, id: str):
#     table = tables.open_file(path)
#     feats = song_features(table)
#     table.close()

    # with open(f'features/{id}.json', 'w') as f:
    #     json.dump(feats, f, indent=2)

count = 0

all_feats = {}

for g1 in os.listdir('MillionSongSubset'):
    for g2 in os.listdir(f'MillionSongSubset/{g1}'):
        for g3 in os.listdir(f'MillionSongSubset/{g1}/{g2}'):
            for file in os.listdir(f'MillionSongSubset/{g1}/{g2}/{g3}'):
                if count % 250 == 0:
                    print(f'Writing file #{count}...')

                table = tables.open_file(f'MillionSongSubset/{g1}/{g2}/{g3}/{file}')
                feats = song_features(table)
                table.close()
            
                all_feats[file.strip('.hd5')] = feats
                
                count += 1

with open('features.json', 'w') as f:
    json.dump(all_feats, f, indent=2)