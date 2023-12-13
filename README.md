# CS 5100 Final Project Repo

This repo contains the code I used to collect data and run experiments for my CS 5100 final project.
Some files are notebooks and some are python scripts - I don't really have a reason for why this is, and I mostly
decided on the type of file arbitrarily.

These files are probably not as well-documented as they should be, so here's a short description of each file:

- `astar_trial.py`:
  - Runs a trial with the parameters set at the top of the file, performing an amount of A* searches using source and target songs randomly selected from the dataset
- `find_neighbors.py`:
  - Generates the list of N closest songs for each song in the dataset, using the distance function set at the top of the file
- `hd5_to_json.ipynb`:
  - This file was used to convert the .hd5 files obtained from the Million Song Dataset into JSON files containing features for each song
- `plot_inter_analysis.ipynb`:
  - This performs the inter-path analysis performed in my paper, analysing the characteristics of paths generated from a given trial. In the paper, only the RMS deviation of paths was discussed, but this notebook can also anlyze sinuosity of paths as well
- `plot_intra_analysis.ipynb`:
  - This performs the intra-path analysis performed in my paper, analysing the characteristics of songs within a path generated from a given trial. Specifically, it calculates the average distance to the source song and target song as the path progresses.
- `searching.py`:
  - This file was used to generate the MFCC dataset used for my experiments. It downloads the audio previews of songs using the Spotify web API, then extracting MFCCs from the audio. Songs are found by either searching for songs from the Million Song Dataset, or by doing a tree search from a given seed song by finding recommendations through the Last.fm API.
- `utils.py`:
  - A collection of utility functions used across the other files, such as logging functions and distance functions.