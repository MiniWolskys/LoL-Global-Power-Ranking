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

def get_game_json(platformGameId: str): 
    return json.loads(read_gzip_and_write_to_variable(f"games/{platformGameId}"))

def get_game_length(game_json):
    game_info_df = pd.json_normalize(game_json)
    return game_info_df[game_info_df["eventType"]=="game_end"].iloc[-1]["gameTime"]/1000

def get_endgame_stats(game_json):
    game_info_df = pd.json_normalize(game_json)
    return game_info_df[game_info_df["eventType"]=="stats_update"].iloc[-1]

def get_endgame_player_stats(game_json):
    end_game_info = get_endgame_stats(game_json)
    platformGameId = end_game_info["platformGameId"]
    end_game_info = pd.DataFrame(end_game_info["participants"])[["teamID", "totalGold", "accountID", "stats"]]
    end_game_info["platformGameId"] = platformGameId
    end_game_info["gameLength"] = get_game_length(game_json)
    dataframes = []
    for line in end_game_info[["stats"]].itertuples():
        data_df = pd.DataFrame()
        for column in line.stats:
            data_df[column["name"]] = [column["value"]]
        dataframes.append(data_df)
    return pd.concat([end_game_info.drop(columns=["stats"]), pd.concat(dataframes).reset_index(drop=True)], axis=1)

# ----------------------------------------
#Functions to calculate KPIs values. Might be interested to separate them in an another file
def calc_kda(player_endgame_data):
    return (player_endgame_data["CHAMPIONS_KILLED"] + player_endgame_data["ASSISTS"]) / player_endgame_data["NUM_DEATHS"].replace(0, 1)

def calc_gold_min(player_endgame_data): 
    return player_endgame_data["totalGold"] / (player_endgame_data["gameLength"]/60)

def calc_cs_min(player_endgame_data):
    return (player_endgame_data["MINIONS_KILLED"] +
            player_endgame_data["NEUTRAL_MINIONS_KILLED"] +
            player_endgame_data["NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE"] +
            player_endgame_data["NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE"]) / (player_endgame_data["gameLength"]/60)

def calc_kill_part(player_endgame_data):
    team_stat = player_endgame_data.groupby(["teamID"]).sum()
    return (player_endgame_data["CHAMPIONS_KILLED"] + player_endgame_data["ASSISTS"])/ player_endgame_data.join(team_stat[["CHAMPIONS_KILLED"]], on="teamID", rsuffix="_team")["CHAMPIONS_KILLED_team"]

def calc_gold_perc(player_endgame_data):
    team_stat = player_endgame_data.groupby(["teamID"]).sum()
    return player_endgame_data["totalGold"] / player_endgame_data.join(team_stat[["totalGold"]], on="teamID", rsuffix="_team")["totalGold_team"]

def calc_dmg_perc(player_endgame_data):
    team_stat = player_endgame_data.groupby(["teamID"]).sum()
    return player_endgame_data["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"] / player_endgame_data.join(team_stat[["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"]], on="teamID", rsuffix="_team")["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS_team"]

def calc_dmg_per_gold(player_endgame_data):
    return player_endgame_data["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"] / player_endgame_data["totalGold"]

def calc_vision_score_per_min(player_endgame_data):
    return player_endgame_data["VISION_SCORE"] / (player_endgame_data["gameLength"]/60)

def calc_dmg_taken_perc(player_endgame_data):
    team_stat = player_endgame_data.groupby(["teamID"]).sum()
    return player_endgame_data["TOTAL_DAMAGE_TAKEN"] / player_endgame_data.join(team_stat[["TOTAL_DAMAGE_TAKEN"]], on="teamID", rsuffix="_team")["TOTAL_DAMAGE_TAKEN_team"]

def calc_dmg_taken_per_death(player_endgame_data):
    return player_endgame_data["TOTAL_DAMAGE_TAKEN"] / player_endgame_data["NUM_DEATHS"].replace(0, 1)

# -----------------------------------------

def get_game_kpis(player_endgame_data):
    kpi_df = pd.DataFrame()
    kpi_df["platformGameId"] = player_endgame_data["platformGameId"]
    kpi_df["teamID"] = player_endgame_data["teamID"]
    kpi_df["accountID"] = player_endgame_data["accountID"]

    kpi_df["KDA"] = calc_kda(player_endgame_data)
    kpi_df["Gold/min"] = calc_gold_min(player_endgame_data)
    kpi_df["cs/min"] = calc_cs_min(player_endgame_data)
    kpi_df["KP%"] = calc_kill_part(player_endgame_data)
    kpi_df["Gold%"] = calc_gold_perc(player_endgame_data)
    kpi_df["DMG%"] = calc_dmg_perc(player_endgame_data)
    kpi_df["DMG/Gold"] = calc_dmg_per_gold(player_endgame_data)
    kpi_df["Vision score/min"] = calc_vision_score_per_min(player_endgame_data)
    kpi_df["%DMG taken"] = calc_dmg_taken_perc(player_endgame_data)
    kpi_df["DMG taken/death"] = calc_dmg_taken_per_death(player_endgame_data)

    return kpi_df

"""esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]

leagues_json = download_esports_files(esports_data_files[0])
tournaments_json = download_esports_files(esports_data_files[1])
players_json = download_esports_files(esports_data_files[2])
teams_json = download_esports_files(esports_data_files[3])
mapping_data_json = download_esports_files(esports_data_files[4])

games_ids = get_games_ids(tournaments_json, mapping_data_json)"""

endgame_info_df = get_endgame_player_stats(get_game_json("ESPORTSTMNT01:3294091"))
print(get_game_kpis(endgame_info_df))