import re
import time
import requests
import datetime
from bs4 import BeautifulSoup

def get_stat_daily():
    us_dt = datetime.datetime.now().astimezone(tz_america)
    today = str(us_dt.year)+'{:0>2d}'.format(us_dt.month)+'{:0>2d}'.format(us_dt.day)
    url = f'https://www.espn.com/nba/scoreboard/_/date/{today}'
    content = requests.get(url).content
    soup = BeautifulSoup(content,'html.parser')
    html = str(soup)
    pattern = r'http://www.espn.com/nba/game\?gameId=(\d+)'
    game_today = re.findall(pattern,html)

    while len(game_today) != 0:
        time.sleep(60)
        for game_id in game_today:
            try:
                title,game_result,team1,team2 = get_NBA_result(game_id)
        #       next move there
                game_today.remove(game_id)
            except:
                pass