from __future__ import absolute_import, division, print_function, unicode_literals

import pandas as pd
import numpy as np
from requests import get
import collections
import matplotlib.pyplot as plt
import pickle
from unidecode import unidecode

from basketball_reference_scraper.teams import get_roster, get_team_stats, get_opp_stats, get_team_misc
from basketball_reference_scraper.players import get_stats
from basketball_reference_scraper.constants import TEAM_TO_TEAM_ABBR
from basketball_reference_scraper.utils import get_game_suffix, get_player_suffix

from bs4 import BeautifulSoup
import tensorflow as tf
from tensorflow.keras import layers

def get_player_suffix(name):
    names = name.split(' ')[1:]
    for last_name in names:
        initial = last_name[0].lower()
        r = get(f'https://www.basketball-reference.com/players/{initial}')
        if r.status_code==200:
            soup = BeautifulSoup(r.content, 'html.parser')
            for table in soup.find_all('table', attrs={'id': 'players'}):
                for anchor in table.find_all('a'):
                    if anchor.text==name:
                        suffix = anchor.attrs['href']
                        return suffix


print(get_player_suffix('Tremaine Fowlkes'))
