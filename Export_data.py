import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO

import pandas as pd

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"

def read_gzip_and_write_to_variable(file_name):
    local_file_name = file_name.replace(":", "_")
    response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
    if response.status_code == 200:
        try:
            gzip_bytes = BytesIO(response.content)
            with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
                json_text = gzipped_file.read().decode("utf-8")
        except Exception as e:
            print("Error:", e)
    else:
        print(f"Failed to download {file_name}")
    return json_text


def download_esports_files(file_name: str):
    directory = "esports-data"
    return read_gzip_and_write_to_variable(f"{directory}/{file_name}")


def get_games_ids(tournaments_json: str, mapping_data_json: str):
    tournaments_data = json.loads(tournaments_json)
    mappings_data = json.loads(mapping_data_json)
    mappings = {esports_game["esportsGameId"]: esports_game for esports_game in mappings_data}

    esportgame_ids = []
    for tournament in tournaments_data:
        for stage in tournament["stages"]:
            for section in stage["sections"]:
                for match in section["matches"]:
                    for game in match["games"]:
                        if game["state"] == "completed":
                            try:
                                esportgame_ids.append([tournament["id"], stage["name"], section["name"], match["id"], game["id"], mappings[game["id"]]["platformGameId"]])
                            except KeyError:
                                continue
    return esportgame_ids

def get_endgame_info(platformGameId: str):
    directory = "games"
    game_info_json = json.loads(read_gzip_and_write_to_variable(f"{directory}/{platformGameId}"))
    game_info_df = pd.json_normalize(game_info_json)
    end_game_info = pd.DataFrame(game_info_df[game_info_df["eventType"]=="stats_update"].iloc[-1]["participants"])
    end_game_info = end_game_info[["accountID", "stats"]]
    dataframes = []
    for line in end_game_info.itertuples():
        data_df = pd.DataFrame()
        data_df["platformGameId"] = [platformGameId]
        data_df["accountID"] = [line.accountID]
        for column in line.stats:
            data_df[column["name"]] = [column["value"]]
        dataframes.append(data_df)
    return pd.concat(dataframes).reset_index(drop=True)

esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]

leagues_json = download_esports_files(esports_data_files[0])
tournaments_json = download_esports_files(esports_data_files[1])
players_json = download_esports_files(esports_data_files[2])
teams_json = download_esports_files(esports_data_files[3])
mapping_data_json = download_esports_files(esports_data_files[4])

games_ids = get_games_ids(tournaments_json, mapping_data_json)
endgame_info_df = get_endgame_info(games_ids[0][-1])
print(endgame_info_df)