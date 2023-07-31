# settings & imports
import pandas as pd
import logging
from helpers.baseball_functions import total_bases

logger = logging.getLogger(__name__)
loglevel = logging.INFO
logger.setLevel(loglevel)

# functions
def load_games(start_year, end_year):
    ""
    # NOTE: Input data sourced from https://www.retrosheet.org/gamelogs/index.html
    # load sample game logs data
    games_2010_2016 = pd.read_csv("/Users/jakemfeldman/sports_analytics/neo/helpers/games/mlb-game-logs-2010-2016.csv")
    games_dtypes = games_2010_2016.dtypes
    games_columns = games_2010_2016.columns

    # concatenate all single-season game logs into one DataFrame
    games =pd.DataFrame(columns=games_columns)
    games = games.astype(dtype=games_dtypes)

    for year in range(start_year, end_year+1):
        season_games = pd.read_csv(f"/Users/jakemfeldman/sports_analytics/neo/helpers/games/gl{year}.txt", 
                                   header=None, 
                                   names=games_columns, 
                                   )
        games = pd.concat([games, season_games], axis=0).copy()
    games.reset_index(drop=True, inplace=True)
    games['date'] = pd.to_datetime(games['date'], format='%Y%m%d')

    # add date parts
    games['year'] = games['date'].dt.year
    games['month'] = games['date'].dt.month
    games['day_of_month'] = games['date'].dt.day

    # plate appearances & total bases
    for i in ("v", "h"):
        games[f"{i}_plate_appearances"] = games[[f"{i}_at_bats", f"{i}_sacrifice_hits", f"{i}_sacrifice_flies", f"{i}_hit_by_pitch", f"{i}_walks", f"{i}_intentional_walks"]].sum(axis=1)
        games[f"{i}_bases_reached"] = games[[f"{i}_hits", f"{i}_hit_by_pitch", f"{i}_walks", f"{i}_intentional_walks"]].sum(axis=1)
        games[f"{i}_total_bases"] = games.apply(lambda row: total_bases(row[f"{i}_hits"], row[f"{i}_doubles"], row[f"{i}_triples"], row[f"{i}_homeruns"]), axis=1)

    # totals
    for x in ("score", "at_bats", "hits", "homeruns", "plate_appearances", "bases_reached", "total_bases"):
        games[f"t_{x}"] = games[[f"v_{x}", f"h_{x}"]].sum(axis=1)

    return games

def load_ballparks():
    ""
    # stadiums = pd.read_json(path_or_buf="/Users/jakemfeldman/sports_analytics/neo/helpers/ballparks/stadium_locations.json")
    ballparks_0 = pd.read_csv("/Users/jakemfeldman/sports_analytics/neo/helpers/ballparks/StadiumData2.csv")
    ballparks_1 = pd.read_csv("/Users/jakemfeldman/sports_analytics/neo/helpers/ballparks/ballparks.csv")

    # align stadium names & merge
    parks_dict = {
        "Busch Stadium III": "Busch Stadium", 
        "Globe Life Field in Arlington": "Globe Life Park in Arlington",
        "Great American Ballpark": "Great American Ball Park",
        "Guaranteed Rate Field;U.S. Cellular Field": "Guaranteed Rate Field",
        "Oakland-Alameda County Coliseum": "Oakland–Alameda County Coliseum",
        "PETCO Park": "Petco Park", 
        "Suntrust Park": "SunTrust Park", 
        "Yankee Stadium II": "Yankee Stadium",
        }
    ballparks_1.replace({"NAME": parks_dict}, inplace=True)
    ballparks = ballparks_0.merge(ballparks_1, how='left', left_on='Name', right_on='NAME')

    return ballparks

def load_teams():
    ""
    teams = pd.read_csv("/Users/jakemfeldman/sports_analytics/neo/helpers/teams/teams.csv")
    teams['full_name'] = teams['CITY'] + " " + teams['NICKNAME']

    return teams

def load_weather():
    ""
    # NOTE: Input data sourced from https://open-meteo.com/
    # generate list of outdoor-only ballparks
    ballparks = load_ballparks()
    outdoor_clause = ((~ballparks["StadiumDome"]) & (ballparks["PARKID"] != "LOS02"))
    outdoor_parks = ballparks.loc[outdoor_clause]['PARKID']

    # create DataFrame of weather data for all outdoor parks (2020-2022)
    weather = pd.DataFrame()
    for park in outdoor_parks:
        foo = pd.read_csv(f"/Users/jakemfeldman/sports_analytics/neo/helpers/weather/{park}.csv", skiprows=2)
        foo['park_id'] = park
        weather = pd.concat([weather, foo], axis=0).copy()
    weather.reset_index(drop=True, inplace=True)
    weather['time'] = pd.to_datetime(weather['time'], format='%Y-%m-%d')

    # rename columns
    cols_dict = {
        "time": "date", 
        "park_id": "park_id",
        "temperature_2m_max (°F)": "max_temp_f",
    }
    weather = weather[list(cols_dict.keys())].copy()
    weather.rename(columns=cols_dict, inplace=True)

    return weather



if __name__ == "__main__":
    logger.info("Data checks:")
    games = load_games(2000, 2022)
    logger.info(f"There are {games.shape[0]} game records from 2000-2022")
