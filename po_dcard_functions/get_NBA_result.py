import requests
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver



def get_NBA_result(game_id):
    web = requests.get(f'https://www.espn.com/nba/boxscore?gameId={game_id}')
    content = web.content
    soup = BeautifulSoup(content,'html.parser')
    #     get result(score)
    html = soup.find(name='div',attrs={'class':'competitors'})
    game_result = pd.read_html(str(html))[0]
    col = game_result.columns.to_list()
    col[0] = 'Team'
    game_result.columns = col
    #     get article title
    title = '[BOX] '+game_result['Team'][0]+' '+str(game_result['T'][0])+' : '+str(game_result['T'][1])+' '+game_result['Team'][1]
    #     get stat(players stat)
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
    for column in team1.columns[1:]:
        for value in team1[column].values:
            if str(value)[0].isalpha() and str(value).lower() != 'nan':
                team1[column].replace({value: 0}, inplace=True)
        for value in team2[column].values:
            if str(value)[0].isalpha() and str(value).lower() != 'nan':
                team2[column].replace({value: 0}, inplace=True)

    team1.fillna(' ',inplace=True)
    team2.fillna(' ',inplace=True)
    
    return title,game_result,team1,team2



def get_NBA_result_with_conditions(game_id):
    web = requests.get(f'https://www.espn.com/nba/boxscore?gameId={game_id}')
    content = web.content
    soup = BeautifulSoup(content,'html.parser')
    #     get result(score)
    html = soup.find(name='div',attrs={'class':'competitors'})
    game_result = pd.read_html(str(html))[0]
    col = game_result.columns.to_list()
    col[0] = 'Team'
    game_result.columns = col
    #     get article title
    title = '[BOX] '+game_result['Team'][0]+' '+str(game_result['T'][0])+' : '+str(game_result['T'][1])+' '+game_result['Team'][1]
    #     get stat(players stat)
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

    team1.fillna(' ',inplace=True)
    team2.fillna(' ',inplace=True)
    
    return title,game_result,team1,team2



def po_dcard(account, password, title, content, tags):
    driver = webdriver.Chrome()
    driver.get('https://www.dcard.tw/f')
    login = driver.find_element_by_xpath('//*[@id="__next"]/div[1]/div/div[2]/a/span') 
    login.click()
    time.sleep(1)
    email = driver.find_element_by_xpath('//*[@id="__next"]/main/div/div/div/div[2]/div[1]/div[2]/div[3]/form/div[1]/label/div[2]/input')\
    .send_keys(account)
    password = driver.find_element_by_xpath('//*[@id="__next"]/main/div/div/div/div[2]/div[1]/div[2]/div[3]/form/div[2]/label/div[2]/input')\
    .send_keys(password)
    login_btn = driver.find_element_by_xpath('//*[@id="__next"]/main/div/div/div/div[2]/div[1]/div[2]/div[3]/form/button')\
    .click()
    time.sleep(7)
    po_btn = driver.find_element_by_xpath('//*[@id="__next"]/div[1]/div/div[2]/a[1]').click()
    time.sleep(.5)
    choose_forums = driver.find_element_by_xpath('//*[@id="__next"]/main/form/div[2]/div[1]/div/div').click()
    time.sleep(.5)
    forum1 = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div/div').click()
    time.sleep(.5)
    identify = driver.find_element_by_xpath('//*[@id="__next"]/main/form/div[3]/div/div/div/div/div').click()
    time.sleep(.5)
    identify1 = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div[2]/div/button[3]/span[1]/div/div[2]/div').click()
    time.sleep(.5)
    title_bar = driver.find_element_by_xpath('//*[@id="__next"]/main/form/div[3]/textarea').send_keys(title)
    time.sleep(.5)
    content_area = driver.find_element_by_xpath('//*[@id="__next"]/main/form/div[4]/div/div/div/div[2]/div').send_keys(content)
    time.sleep(.5)
    next_step = driver.find_element_by_xpath('//*[@id="__next"]/main/form/div[5]/div/button').click()
    time.sleep(.5)
    tag_bar = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/div/div[1]/label/div/input')
    time.sleep(.5)
    for tag in tags:
        tag_bar.send_keys(tag)
        time.sleep(.5)
        tag_bar.send_keys(Keys.ENTER)
    time.sleep(.5)
    post = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/footer/div[2]/div[2]/button').click()
    return 'ok'



def daily_post(gameid_start, games_today):
        for gameid in range(gameid_start,gameid_start+games_today):
            try:
                title,game_result,team1,team2 = get_NBA_result(gameid)
                content = str(game_result)+str(team1)+str(team2)+'(DCARD發文限制：文章內得要有十五個中文字以上。)'
                po_dcard('account','password',str(title),content,['tag1','tag2'])
            except:
                time.sleep(10)
                continue