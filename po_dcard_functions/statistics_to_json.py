import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

def statistics_to_json(game_id):
    stat_json = {}
    away = {}
    home = {}
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
    away['team'] = game_result.iloc[0].to_list()[0]
    away['score'] = game_result.iloc[0].to_list()[1:]
    away['streak'] = streaks[0]
    home['team'] = game_result.iloc[1].to_list()[0]
    home['score'] = game_result.iloc[1].to_list()[1:]
    home['streak'] = streaks[1]
    stat = soup.find(name='div',attrs={'id':'gamepackage-boxscore-module'})
    for abbr in soup.find_all(name='span',attrs={'class':'abbr'}):
        abbr.decompose()
    for position in stat.find_all(name='span',attrs={'class':'position'}):
        position.insert_before('/')
    team1 = pd.read_html(str(stat))[0]
    team2 = pd.read_html(str(stat))[1]
    column_list = team1.columns.tolist()
    column = []
    for col_a,col_b in column_list:
        column.append(col_a)
    column[0] = 'Players'
    team1.columns = column
    team2.columns = column
    team1.fillna('',inplace=True)
    team2.fillna('',inplace=True)
    def df_process(df):
        df['Players'] = df['Players'].apply(lambda x:x.split('/')[0])
        df['DNP'] = df['MIN'].apply(lambda x: True if x[:3]=='DNP' else False)
        starter = df.head(5)['Players'].to_list()
        df['STARTER'] = df['Players'].apply(lambda x:True if x in starter else False)
        return json.loads(df.to_json(orient='records'))
    away['players'] = df_process(team1)
    home['players'] = df_process(team2)
    stat_json['away'] = away
    stat_json['home'] = home
    return stat_json