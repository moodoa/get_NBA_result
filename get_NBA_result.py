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
    for i in soup.find_all(name='span',attrs={'class':'abbr'}):
        i.decompose()
    for i in stat.find_all(name='span',attrs={'class':'position'}):
        i.insert_before('/')

    team1 = pd.read_html(str(stat))[0]
    team2 = pd.read_html(str(stat))[1]
    col = team1.columns.tolist()
    column = []
    for i,j in col:
        column.append(i)
    column[0] = 'Players'
    team1.columns = column
    team2.columns = column
    for c in team1.columns[1:]:
        for i in team1[c].values:
            if len(str(i))>=10:
                team1[c].replace({i: 0}, inplace=True)
        for i in team2[c].values:
            if len(str(i))>=10:
                team2[c].replace({i: 0}, inplace=True)

    team1.fillna(' ',inplace=True)
    team2.fillna(' ',inplace=True)
    
    return title,game_result,team1,team2