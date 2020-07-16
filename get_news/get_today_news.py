import requests
from bs4 import BeautifulSoup

def get_today_news_list():
    web = requests.get('https://nba.udn.com/nba/cate/6754/6780/newest')
    content = web.content
    soup = BeautifulSoup(content,'html.parser')
    soup = soup.find(name='div',attrs={'id':'news_list_body'})
    today_news_id = []
    for i in range(len(soup.find_all('a',href = True))):
        today_news_id.append(soup.find_all('a',href = True)[i]['href'].split('/')[-1])
    return today_news_id

def get_news(article_id):
    article_id = str(article_id)
    web = requests.get(f'https://nba.udn.com/nba/story/6780/{article_id}')
    content = web.content
    soup = BeautifulSoup(content,'html.parser')
    title = soup.h1.text
    author = soup.find(name='div',attrs={'class':'shareBar__info--author'}).text
    article_content = ''
    for p in soup.find_all(name='p'):
        article_content += (p.text+'\n')
    return title,author,article_content

today_news_ids = get_today_news_list()
for today_news_id in today_news_ids:
    try:
        title,author,article_content = get_news(today_news_id)
        print(title,author,article_content)
        print('-'*100)
    except:
        pass