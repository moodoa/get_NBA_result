import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

def statistics_to_json(game_id):
    stat_json, away, home = {},{},{}
    content = requests.get(f'https://www.espn.com/nba/game?gameId=401161478').content
    soup = BeautifulSoup(content,'html.parser')
    z_time = soup.find(name='div',attrs={"class":"game-date-time"}).span['data-date']
    stat_json['game_time'] = z_time
    web = requests.get(f'https://www.espn.com/nba/boxscore?gameId={game_id}')
    content = web.content
    soup = BeautifulSoup(content,'html.parser')
    html = soup.find(name='div',attrs={'class':'competitors'})
    game_result = pd.read_html(str(html))[0]
    col = game_result.columns.to_list()
    col[0] = 'Team'
    game_result.columns = col
    streaks = []
    for record in soup.find_all(name='div',attrs={"class":"record"}):
        streaks.append(record.text)
    for streak_idx in range(len(streaks)):
        if ',' in streaks[streak_idx]:
            streaks[streak_idx] = streaks[streak_idx].split(',')[0]
    period = list(game_result.iloc[0].to_dict().keys())[1:]
    away_score = {}
    for idx in range(len(period)):
        away_score[period[idx]] = str(game_result.iloc[0].to_list()[1:][idx])
    home_score = {}
    for idx in range(len(period)):
        home_score[period[idx]] = str(game_result.iloc[1].to_list()[1:][idx])
    away['team'] = game_result.iloc[0].to_list()[0]
    away['score'] = away_score
    away['streak'] = streaks[0]
    home['team'] = game_result.iloc[1].to_list()[0]
    home['score'] = home_score
    home['streak'] = streaks[1]
    stat = soup.find(name='div',attrs={'id':'gamepackage-boxscore-module'})
    for abbr in soup.find_all(name='span',attrs={'class':'abbr'}):
        abbr.decompose()
    for position in stat.find_all(name='span',attrs={'class':'position'}):
        position.insert_before('/')
    def load_dataframe(idx):
        team = pd.read_html(str(stat))[idx]
        column_list = team.columns.tolist()
        column = []
        for col_a,col_b in column_list:
            column.append(col_a)
        column[0] = 'Players'
        team.columns = column
        team.fillna('',inplace=True)
        return team
    team1 = load_dataframe(0)
    team2 = load_dataframe(1)
    def df_process(df):
        df['Players'] = df['Players'].apply(lambda x:x.split('/')[0])
        df['DNP'] = df['MIN'].apply(lambda x: True if str(x)[:3]=='DNP' else False)
        starter = df.head(5)['Players'].to_list()
        df['STARTER'] = df['Players'].apply(lambda x:True if x in starter else False)
        return json.loads(df.to_json(orient='records'))
    away['players'] = df_process(team1)
    home['players'] = df_process(team2)
    stat_json['away'] = away
    stat_json['home'] = home
    return stat_json