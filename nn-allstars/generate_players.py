"""
A module that generates a list of players that meet a certain set of criteria.

Functions:
    save_dict(d,name):
        will save a dictionary as a pickle file

    load_dict(name):
        will load a dictionary as a pickle file

    prune_weird_names(st):
        given a string, returns a copy of the string without weird characters

    get_roster_stats(team, season_end_year, data_format='PER_GAME', playoffs=False):
        will return the roster for a given season for a given team, with basic per game stats

    get_player_names(start_year, end_year, minimum_mpg = 15, minimum_g = 30, verbose = False):
        uses the get_roster_stats function to generate a list of players in specified seasons who meet certain criteria

    gen(start_year, end_year, minimum_mpg = 15, minimum_g = 30, verbose = False):
        puts it all together and generates a pickle file in the working directory with all the players

Todo:
    * maybe check if pickle file already exists, put some metadata about years so we don't replicate calls too much
    * find some way to reduce those ugly arguments in gen
    * all the Todos within functions
"""
import pandas as pd
from requests import get
import pickle

from basketball_reference_scraper.teams import get_roster
from basketball_reference_scraper.constants import TEAM_TO_TEAM_ABBR
from bs4 import BeautifulSoup

def save_dict(d,name):
    """Function to save dictionary as a pickle file in current directory, with given name.

    Args:
        d (dict): Dictionary to be saved as a pickle file.
        name (str): The name of the file to be saved.

    Returns:
        None
    """
    with open(f'{name}.p', 'wb') as fp:
        pickle.dump(d, fp, protocol=pickle.HIGHEST_PROTOCOL)

def load_dict(name):
    """Function to load a dictionary saved as a pickle file with given name.

    Args:
        name (str): The name of the file to be loaded.

    Returns:
        Dictionary loaded from a pickle file.
    """
    with open(f'{name}.p', 'rb') as fp:
        return pickle.load(fp)

def prune_weird_names(st):
    """Function to replace weird characters in names with their latin language equivalents.

    Args:
        st (str): String to replace foreign characters from.

    Returns:
        string with weird characters removed and normal letters inserted

    Todo:
        *not make this so hardcoded lol. I tried to do a bunch of stuff with encodings when reading the data but it just doesn't work.
        *track new weird names if they come into NBA. Current character lists are based on 2000-2019 seasons
    """
    st = st.replace('Ã–', 'o')
    st = st.replace('Å½', 'z')
    st = st.replace('Å¾', 'z')
    st = st.replace('Å†', 'n')
    st = st.replace('Ä£', 'g')
    st = st.replace('*', '')
    if len(st.split(' ')) > 2 and st != 'Juan Carlos Navarro':
        lst = st.split(' ')
        st = f'{lst[0]} ' + ''.join(lst[1:])
    st = st.replace('Juan Carlos Navarro', 'JuanCarlos Navarro')
    st = st.replace('Ã©', 'e')
    st = st.replace('Ã¡', 'a')
    st = st.replace('Ä‡', 'c')
    st = st.replace('Ä', 'c')
    st = st.replace('Ã¼', 'u')
    st = st.replace('ÄŸ', 'g')
    st = st.replace('Ã³', 'o')
    st = st.replace('Ã¶', 'o')
    st = st.replace('Ã¤', 'a')
    st = st.replace('Ãª', 'e')
    st = st.replace('Å™', 'r')
    st = st.replace('Ã­-', 'o')
    st = st.replace('Ã£', 'a')
    st = st.replace('Ã«', 'e')
    st = st.replace('Å¡', 's')
    st = st.replace('Å ', 's')
    st = st.replace('Å«', 'u')
    st = st.replace('Ä°', 'i')
    st = st.replace('Ã½', 'y')
    st = st.replace('ÅŸ', 's')
    st = st.replace('Ä±', 'i')
    st = st.replace('Ã§', 'c')
    st = st.replace('Ã', 'a' )
    st = st.replace('Ã­', 'i')
    st = st.replace('Ã¨', 'e')
    st = st.replace('Ä', 'a')
    st = st.replace('Å½iÅ¾iÄ‡', 'Zizic')
    return st

def get_roster_stats(team, season_end_year, data_format='PER_GAME', playoffs=False):
    """Function to load a team's roster for a specific year, and return it with the per game stats.

    Args:
        team (str): Three letter abbreviatio nfor desired team
        season_end_year (int): year the season ended. e.g, for 2009-2010 season, input 2010.
        data_format ('PER_GAME', ?): formats for the outputted data
        playoffs (bool): whether to make the data frm the playoffs that year, or not

    Returns:
        Dataframe with the columns for ['PLAYER', 'POS', 'AGE', 'TEAM', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%',
           '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
           'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'SEASON']

    Todo:
        *Figure out what other data_formats you can have
    """
    if playoffs:
        period = 'playoffs'
    else:
        period = 'leagues'
    selector = data_format.lower()
    r = get(f'https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2F{period}%2FNBA_{season_end_year}_{selector}.html&div=div_{selector}_stats')
    df = None
    if r.status_code==200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        df2 = pd.read_html(str(table))[0]
        for index, row in df2.iterrows():
            if row['Tm']==team:
                if df is None:
                    df = pd.DataFrame(columns=list(row.index)+['SEASON'])
                row['Player'] = prune_weird_names(row['Player'])
                row['SEASON'] = f'{season_end_year-1}-{str(season_end_year)[2:]}'
                df = df.append(row)
        df.rename(columns = {'Player': 'PLAYER', 'Age': 'AGE', 'Tm': 'TEAM', 'Pos': 'POS'}, inplace=True)
        df = df.reset_index().drop(['Rk', 'index'], axis=1)
        return df

def get_player_names(start_year, end_year, minimum_mpg = 15, minimum_g = 30, verbose = False):
    """Given a range of seasons, return all the players meting the minutes per game and game requirements

    Args:
        start year (int): start of data query
        end_year (int): end of data query
            ###Note: For a range from the 2009-2010 season to the 2013-2014 season, start_year would be 2010 and end_year would be 2014
        minimum_mpg (int): minimum minutes per game for someone to be include in this list
        minimum_g (int): minimum games for someone to be include in this list
        verbose (bool): when True, print out when the function moves on to the next year

    Returns:
        Dictionary with seasons (year the season ended) as keys and a set of players who meet the requirements as values

    Todo:
        *Figure out how **kwargs work to allow users to put unlimited filters
    """
    year_players = {}
    for year in range(start_year,end_year+1,1):
        if status:
            print(f'Status: starting on {year}')
        all_players_names = set()
        already = set()
        for team in list(TEAM_TO_TEAM_ABBR.values()):
            if team in already: continue
            try:
                rs = get_roster_stats(team,year)
                roster_stats_filtered = rs.loc[(rs['MP'].astype(float) >= minimum_mpg)&(rs['G'].astype(float) >= minimum_mpg)]
                team_player_names = list(roster_stats_filtered['PLAYER'])
                team_player_names = list(map(prune_weird_names, team_player_names))
                all_players_names.update(team_player_names)
                already.add(team)
            except:
                continue
        year_players[year] = all_players_names
    return year_players

def gen(name,start_year, end_year, minimum_mpg = 15, minimum_g = 30, verbose = False):
    """Given a filename and a range of seasons, create a pickle file of a dictionary contianing all the players meting the minutes per game and game requirements

    Args:
        name (str): The name of the pickle file to be saved
        start year (int): start of data query
        end_year (int): end of data query
            ### Note: For a range from the 2009-2010 season to the 2013-2014 season, start_year would be 2010 and end_year would be 2014
        minimum_mpg (int): minimum minutes per game for someone to be include in this list
        minimum_g (int): minimum games for someone to be include in this list
        verbose (bool): when True, print out when the function moves on to the next year

    Returns:
        None

    Todo:
        * Is tehre an way to not make the arguments of this the exact same as those of the above function??
    """
    x = get_player_names(start_year, end_year, minimum_mpg = minimum_mpg, minimum_g = minimum_g, verbose = verbose)
    save_dict(x,name)
