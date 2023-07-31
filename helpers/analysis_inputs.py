# Imports & Settings
import pandas as pd
from helpers.load_data import load_games, load_ballparks, load_teams, load_weather
from helpers.baseball_functions import batting_average, on_base_percentage, slugging_percentage

def weather_analysis_input():
    # Load Data
    games = load_games(start_year=2020, end_year=2022)
    ballparks = load_ballparks()
    teams = load_teams()
    weather = load_weather()

    # Format games data
    games_cols = ["date", "year", "month", "day_of_month", "v_name", "h_name", "day_night", "park_id", "t_at_bats", "t_hits", "t_score", "t_total_bases", "t_bases_reached", "t_plate_appearances"]
    games = games[games_cols].copy() # select only relevant columns
    games = games.loc[games["day_night"] == "D"].copy() # select only day games for max temp alignment

    # Format & merge team names
    cols_dict = { # visiting team
        "TEAM": "v_name", 
        "full_name": "v_full_name",
    }
    v_teams = teams[list(cols_dict.keys())].copy()
    v_teams.rename(columns=cols_dict, inplace=True)

    cols_dict = { # home team
        "TEAM": "h_name", 
        "full_name": "h_full_name",
    }
    h_teams = teams[list(cols_dict.keys())].copy()
    h_teams.rename(columns=cols_dict, inplace=True)

    df = games.merge(v_teams, how="left", left_on="v_name", right_on="v_name")
    df = df.merge(h_teams, how="left", left_on="h_name", right_on="h_name").copy()

    # Format & merge ballparks
    cols_dict = {
        "PARKID": "park_id", 
        "StadiumDome": "stadium_dome",
        "Name": "ballpark_name", 
        "lat": "ballpark_lat", 
        "lng": "ballpark_lng"
    }
    ballparks = ballparks[list(cols_dict.keys())].copy()
    ballparks.rename(columns=cols_dict, inplace=True)

    df = df.merge(ballparks, how="left", left_on="park_id", right_on="park_id").copy()

    # Merge weather
    df = df.merge(weather, how="left", left_on=["park_id", "date"], right_on=["park_id", "date"]).copy() 

    # Add ballpark baselines
    grouped = df.groupby('park_id')
    runs = grouped["t_score"].mean().to_frame(name="bl_runs")
    avg = grouped.apply(lambda row: batting_average(row['t_hits'], row['t_at_bats'])).to_frame(name="bl_avg")
    obp = grouped.apply(lambda row: on_base_percentage(row['t_bases_reached'], row['t_plate_appearances'])).to_frame(name="bl_obp")
    slg = grouped.apply(lambda row: slugging_percentage(row['t_total_bases'], row['t_at_bats'])).to_frame(name="bl_slg")

    foo = pd.DataFrame(runs)
    for x in [avg, obp, slg]:
        foo = foo.join(x)
    
    df = df.merge(foo, how="left", left_on="park_id", right_on="park_id").copy()

    # Add game-specific calcs
    df['gs_avg'] = round(df['t_hits'] / df['t_at_bats'], 3)
    df['gs_obp'] = round(df['t_bases_reached'] / df['t_plate_appearances'], 3)
    df['gs_slg'] = round(df['t_total_bases'] / df['t_at_bats'], 3)

    # Add game-specific diffs from baseline
    df['diff_runs'] = df["t_score"] - df["bl_runs"]
    for x in ['avg', 'obp', 'slg']:
        df[f"diff_{x}"] = df[f"gs_{x}"] - df[f"bl_{x}"]
    
    # Filter out indoor parks
    df = df.loc[df["stadium_dome"] == False].copy()

    return df
