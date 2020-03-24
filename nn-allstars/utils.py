"""
A module with some useful functions that are used across various different places.

Functions:
    save_dict(d,name):
        will save a dictionary as a pickle file

    load_dict(name):
        will load a dictionary as a pickle file

    prune_weird_names(st):
        given a string, returns a copy of the string without weird characters

    was_all_star(name, season):
        given a player name and a season, returns whether they were an all star

Todo:
    * Decide what could best fit in this utils category
"""
import pandas as pd
import pickle
from bs4 import BeautifulSoup
from requests import get

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

def was_all_star(name, season):
    """
    Will tell you whether a player had an all-star season in the season that ends on the year given (i.e. if you pass 2018 it will tell you whether the player was an all-star in the 2017-2018 season)

    Args:
        name (str): Name of player whos ame you want
        season (int): Season to check if the player was an all-star

    Returns:
        all-star: True if player was an all-star, False otherwise
   """
    name_code = get_player_suffix(name).replace('/players/', '')
    name_code = name_code[2:]
    last_initial = name_code[0]
    selector = 'div_all_star'
    url = f'https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fplayers%2F{last_initial}%2F{name_code}&div={selector}'
    r = get(url)
    if r.status_code==200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        try:
            df = pd.read_html(str(table))[0]
        except ValueError:
            return False
        all_star_seasons = list(str(x) for x in list(df['Season']))
        season_in_question = '{}-{}'.format(season-1,str(season)[-2:])
        if season_in_question in all_star_seasons:
            return True
        return False
    else:
        return False
