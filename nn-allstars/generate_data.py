import pandas as pd
import numpy as np
import generate_players
import utils
import tabloo

from requests import get
from basketball_reference_scraper.players import get_stats
from basketball_reference_scraper.utils import get_player_suffix

from bs4 import BeautifulSoup
# import tensorflow as tf
# from tensorflow.keras import layers

def get_game_logs(name, start_date, end_date, playoffs=False, num_games = None):
    """
    Will get the raw gamelogs for a given player in the given date ranges

    Args:
        name (str): Name of player whose games you want
        start_date (str): Inclusive start date of game logs in format 'YYYY-MM-DD'
        end_date (str): Inclusive end date of game logs in format 'YYYY-MM-DD'
        playoffs (bool): Whetehr or not to include playoff games

    Returns:
        returns a dataframe with a record of games between the dates, including categories ['Rk', 'G', 'DATE', 'AGE', 'TEAM', 'HOME/AWAY', 'OPPONENT', 'RESULT', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GAME_SCORE', '+/-']
   """
    suffix = get_player_suffix(name).replace('/', '%2F').replace('.html', '')
    start_date_str = start_date
    end_date_str = end_date
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    years = list(range(start_date.year, end_date.year+2))
    if playoffs:
        selector = 'div_pgl_basic_playoffs'
    else:
        selector = 'div_pgl_basic'
    final_df = None
    for year in years:
        url = f'https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url={suffix}%2Fgamelog%2F{year}&div={selector}'
        r = get(url)
        if r.status_code==200:
            soup = BeautifulSoup(r.content, 'html.parser')
            table = soup.find('table')
            try:
                df = pd.read_html(str(table))[0]
            except ValueError:
                continue
            df.rename(columns = {'Date': 'DATE', 'Age': 'AGE', 'Tm': 'TEAM', 'Unnamed: 5': 'HOME/AWAY', 'Opp': 'OPPONENT','Unnamed: 7': 'RESULT', 'GmSc': 'GAME_SCORE'}, inplace=True)
            df['HOME/AWAY'] = df['HOME/AWAY'].apply(lambda x: 'AWAY' if x=='@' else 'HOME')
            df = df[df['Rk']!='Rk']
            try:
                df = df.drop(['Unnamed: 30'], axis=1)
            except:
                pass
            df = df.loc[(df['DATE'] >= start_date_str) & (df['DATE'] <= end_date_str)]
            active_df = pd.DataFrame(columns = list(df.columns))
            for index, row in df.iterrows():
                if len(row['GS'])>1:
                    empty_game = pd.DataFrame([[row['Rk'], row['G'], row['DATE'], row['AGE'], row['TEAM'], row['HOME/AWAY'], row['OPPONENT'], row['RESULT'], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
                    empty_game.columns = list(df.columns)
                    active_df = active_df.append(empty_game)
                    continue
                active_df = active_df.append(row)
            if final_df is None:
                final_df = pd.DataFrame(columns=list(active_df.columns))
            final_df = final_df.append(active_df)
    if num_games != None:
        final_df = final_df[(final_df['Rk'].astype(int) <= num_games)]
    return final_df

def get_pre_allstar_data(name, season):
    """
    Will get the gamelogs from the start of the season until the 30th game. Also cleans these gamelogs to give them all numeric values, removes certain categories that might not be useful in ML, and turns string fields into number fields.

    Args:
        name (str): Name of player whos ame you want
        season (int): Season to get the gamelogs from, from the first game of the season up to the 10th of January, inclusive.

    Returns:
        dataframe of games before Jan 10th, including categories ['AGE', 'HOME', 'RESULT', 'MP', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', '+/-', '2P', '2PA', '2P%', 'MOV']
    """
    def min_sec_to_frac_mins(st):
        if st == 0: return 0
        lst = st.split(':')
        return round(int(lst[0]) + int(lst[1])/60,3)
    def yr_day_to_frac_yrs(st):
        lst = st.split('-')
        return round(int(lst[0]) + int(lst[1])/365,3)

    start_date = '-'.join((str(season-1),'08', '01'))
    end_date = '-'.join((str(season),'02', '20'))
    df = get_game_logs(name, start_date, end_date, num_games = 30)
    df.rename(columns={'HOME/AWAY': "HOME", "Rk" : 'NUM_GAME'}, inplace = True)
    df = df.astype({"FG": int,"FGA": int, "3P": int, "3PA": int, "FG%": float, "3P%": float, "FT": int, "FTA": int, "FT%": float, "ORB": int, "AST": int, "STL": int, "BLK": int, "TOV": int, "PF": int, "+/-": int, 'NUM_GAME': int})
    df['2P'] = df['FG'] - df['3P']
    df['2PA'] = df['FGA'] - df['3PA']
    df['2P%'] = np.where(np.array(df['2PA'] == 0), 0, round(df['2P']/df['2PA'],3))
    df['3P%'] = np.where(np.isnan(df['3P%']), 0, df['3P%'])
    df['FT%'] = np.where(np.isnan(df['FT%']), 0, df['FT%'])
    df2 = df['RESULT'].str.split(" ",expand=True)
    df2.columns = ['RESULT','MOV']
    df = df2.combine_first(df)
    cols_to_del = ['DATE', 'TEAM', 'OPPONENT', 'GAME_SCORE', 'FG', 'FGA', 'FG%', 'TRB', 'PTS', 'NUM_GAME', 'G']
    for col in cols_to_del:
        del df[col]
    df.reset_index(drop=True, inplace=True)
    df['HOME'].replace(('HOME', 'AWAY'), (1,0), inplace=True)
    df['RESULT'].replace(('W', 'L'), (1,0), inplace=True)
    df['MP'] = df['MP'].apply(min_sec_to_frac_mins)
    df['AGE'] = df['AGE'].apply(yr_day_to_frac_yrs)
    df['MOV'] = df['MOV'].apply(lambda x : int(x[1:-1]))
    return df

def gen_d(start_year, end_year, mpg = 15, g = 30, v = False):
    #lets start by naming the file appropriately
    if start_year == end_year:
        name = f'{start_year}_mpg{mpg}_g{g}'
    else:
        name = f'{start_year}-{end_year}_mpg{mpg}_g{g}'
    try:
        #load the player names
        d = utils.load_dict(name)
    except:
        #if it doesn't exist, generate player names, then load
        generate_players.gen(name,start_year, end_year, minimum_mpg = mpg, minimum_g = g, verbose = v)
        d = utils.load_dict(name)
    #generate labeled player_seasons
    all_players_data = pd.DataFrame()
    for season in d.keys():
        for index, player in enumerate(d[season]):
            if index == 1: break
            print(f'starting on player # {index}, {player}')
            try:
                df = get_pre_allstar_data(player, season)
            except:
                print(f'{player} had an error collecting data')
                continue
            player_data = np.array(df).flatten()
            if len(player_data) != 690: #23 categories x 30 games
                print(f'{player} had wrong size data')
                continue
            if utils.was_all_star(player, season):
                all_players_data = all_players_data.append(pd.Series(np.append(player_data, 1)), ignore_index = True)
            else:
                all_players_data = all_players_data.append(pd.Series(np.append(player_data, 0)), ignore_index = True)
    all_players_data.columns = [*all_players_data.columns[:-1], 'target']
    return all_players_data

print(gen_d(2012,2012,v=True))

# d = load_dict('year_players')
#
# already_checked = set()
# for year,player_set in d.items():
#     print(f'{year}')
#     for player in player_set:
#         if player in already_checked: continue
#         already_checked.add(player)
#         try:
#             get_player_suffix(player).replace('/', '%2F').replace('.html', '')
#         except Exception as e:
#             print(player)
#             print(e)
# full_dic = load_dict('year_players')
# df = generate_data_from_dict(full_dic)
# df.to_csv('full_dataset.csv')
