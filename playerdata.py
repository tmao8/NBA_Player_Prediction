import pandas as pd
from pandas import json_normalize
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import teamgamelog, scoreboard


# Gets nba player's NBA.com ID using full name
def get_player_id(name: str):
    player_info = players.find_players_by_full_name(name)
    return player_info[0]["id"]


def get_player_gamelog(player_id):
    # Get player id

    # Get player game log using id
    player_log = playergamelog.PlayerGameLog(player_id=player_id)
    player_log = player_log.get_data_frames()[0]

    # Filter data to include only team against and home game
    df = pd.DataFrame(player_log[["MATCHUP", "PTS", "MIN"]])
    df["HOME"] = df["MATCHUP"].str[-5:-4] == "."
    df["MATCHUP"] = df["MATCHUP"].str[-3:]
    return df


def get_player_position(player_id):
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)

    # Make the API request
    player_info_data = player_info.get_data_frames()[0]

    # Extract player position
    position = (
        player_info_data["POSITION"][0]
        if not player_info_data["POSITION"].empty
        else "Position not available"
    )

    return position


# returns data with gamelog and position
def get_full_data(player_id):
    pos = get_player_position(player_id)
    gamelog = get_player_gamelog(player_id)
    data = gamelog
    data["POSITION"] = pos
    return data


# returns a player's average minutes in the previous 5 games
def get_last5_avg_min(player_id):
    game_log = playergamelog.PlayerGameLog(player_id=player_id)
    game_log_data = game_log.get_data_frames()[0]
    # Select the last 5 games
    last_5_games = game_log_data.head(5)
    # Calculate the average minutes
    avg_minutes_last_5 = last_5_games["MIN"].mean()
    return avg_minutes_last_5


# returns True if the player's next game is at home
def get_home(player_id):
    # Get the player's Team ID
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    player_info_data = player_info.get_data_frames()[0]
    team_id = player_info_data["TEAM_ID"][0]
    todayscores = scoreboard.Scoreboard().get_dict()
    for game in todayscores["resultSets"][0]["rowSet"]:
        if game[6] == team_id or game[7] == team_id:
            return game[6] == team_id
            break
    return False


# returns full list of NBA players this season
def get_player_list():
    allactive = players.get_active_players()
    player_list = [nbaplayer["full_name"] for nbaplayer in allactive]
    return player_list
