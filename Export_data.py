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


def download_esports_files(file_name):
    directory = "esports-data"
    return read_gzip_and_write_to_variable(f"{directory}/{file_name}")


def download_games(year):
   start_time = time.time()
   with open("esports-data/tournaments.json", "r") as json_file:
       tournaments_data = json.load(json_file)
   with open("esports-data/mapping_data.json", "r") as json_file:
       mappings_data = json.load(json_file)

   directory = "games"
   if not os.path.exists(directory):
       os.makedirs(directory)

   mappings = {
       esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
   }

   game_counter = 0

   for tournament in tournaments_data:
       start_date = tournament.get("startDate", "")
       if start_date.startswith(str(year)):
           print(f"Processing {tournament['slug']}")
           for stage in tournament["stages"]:
               for section in stage["sections"]:
                   for match in section["matches"]:
                       for game in match["games"]:
                           if game["state"] == "completed":
                               try:
                                   platform_game_id = mappings[game["id"]]["platformGameId"]
                               except KeyError:
                                   print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                   continue

                               read_gzip_and_write_to_variable(f"{directory}/{platform_game_id}")
                               game_counter += 1

                           if game_counter % 10 == 0:
                               print(
                                   f"----- Processed {game_counter} games, current run time: \
                                   {round((time.time() - start_time)/60, 2)} minutes"
                               )


esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
leagues_df = pd.read_json(download_esports_files(esports_data_files[0]))
tournaments_df = pd.read_json(download_esports_files(esports_data_files[1]))
players_df = pd.read_json(download_esports_files(esports_data_files[2]))
teams_df = pd.read_json(download_esports_files(esports_data_files[3]))
mapping_data_df = pd.read_json(download_esports_files(esports_data_files[4]))

print(leagues_df)
#download_games(2023)