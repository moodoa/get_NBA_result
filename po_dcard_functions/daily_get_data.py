import re
import time
import datetime
###TODO:
# functional
# datetime : different between Taiwan time and USA time  

d = datetime.datetime.now()
today = str(d.year)+d.strftime('%m')+d.strftime('%d')
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
    #             next move there
            game_today.remove(game_id)
        except:
            pass