import re
import time
import requests
import datetime
from bs4 import BeautifulSoup

def get_game_id_daily():
    central_time = datetime.datetime.now() + datetime.timedelta(hours=-13)
    today = str(central_time.year)+'{:0>2d}'.format(central_time.month)+'{:0>2d}'.format(central_time.day)
    url = f'https://www.espn.com/nba/scoreboard/_/date/{today}'
    content = requests.get(url).content
    soup = BeautifulSoup(content,'html.parser')
    html = str(soup)
    pattern = r'http://www.espn.com/nba/game\?gameId=(\d+)'
    game_today = re.findall(pattern,html)

    return game_today


def get_stat_daily(game_today):
    while len(game_today) != 0:
        time.sleep(60)
        for game_id in game_today:
            try:
                title,game_result,team1,team2 = get_NBA_result(game_id)
        #       next move there
                game_today.remove(game_id)
            except:
                pass
    return 'finish'