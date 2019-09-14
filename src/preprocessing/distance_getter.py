# DISCLAIMER: Hackathon spaghetti code, use at your own risk.
# Script for generating full distance matrix using the Open Source Routing Machine
# https://wiki.openstreetmap.org/wiki/Open_Source_Routing_Machine

from scipy.sparse import dok_matrix
import pandas as pd
import numpy as np
import requests

df = pd.read_csv("stanoviste.csv")
lat, long = df['lat'], df['long']
n_rows = lat.shape[0]

BATCH_SIZE = 100
no_batches = np.ceil(len(lat) / BATCH_SIZE)
no_batches = int(no_batches)

API_ENDPOINT = "http://172.16.20.100:5000/table/v1/driving/"


def get_batch_query(src_batch, tar_batch):
    # === SOURCE COORDINATES ===
    src_down = src_batch * BATCH_SIZE
    src_up = (src_batch + 1) * BATCH_SIZE
    src_up = min(src_up, n_rows)

    src_lats = lat[src_down:src_up]
    src_longs = long[src_down:src_up]

    query = API_ENDPOINT
    for i, j in zip(src_lats, src_longs):
        query = f"{query}{i},{j};"

    # === TARGET COORDINATES ===
    tar_down = tar_batch * BATCH_SIZE
    tar_up = (tar_batch + 1) * BATCH_SIZE
    tar_up = min(tar_up, n_rows)

    tar_lats = lat[tar_down:tar_up]
    tar_longs = long[tar_down:tar_up]

    for i, j in zip(tar_lats, tar_longs):
        query = f"{query}{i},{j};"

    src_range = list(range(src_down, src_up))
    tar_range = list(range(tar_down, tar_up))

    # Delete last semicolon and proceed
    query = f"{query[:-1]}?sources="
    for i in range(len(src_range)):
        query = f"{query}{i};"

    # Delete last semicolon and proceed
    query = f"{query[:-1]}&destinations="
    for i in range(len(src_range), len(src_range) + len(tar_range)):
        query = f"{query}{i};"

    print(f"Created query src {src_down}:{src_up} tar {tar_down}:{tar_up}")
    return src_range, tar_range, query[:-1]


distance_matrix = dok_matrix((n_rows, n_rows), float)
for src_batch in range(no_batches):
    for tar_batch in range(no_batches):
        src_range, tar_range, query = get_batch_query(src_batch, tar_batch)
        response = requests.get(query)

        try:
            durations = response.json()["durations"]
        except:
            print(response.json())
            exit(1)

        for i, sb in enumerate(src_range):
            for j, tb in enumerate(tar_range):
                distance_matrix[sb, tb] = durations[i][j]


distance_matrix = distance_matrix.toarray()
with open("distance_matrix.txt", "w") as ofile:
    for row in distance_matrix:
        for x in row:
            ofile.write(f"{x:.2f}\t")
        ofile.write("\n")
