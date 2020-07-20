# Get NBA statistics from ESPN & <br/>Get news from NBA.UDN
![alt text](https://miro.medium.com/max/1050/1*ypslG7x_vZF28O9X-l1ZVQ.jpeg)

## po_dcard_functions
#### get_NBA_result.py
* 以 `gameid` 為參數爬取 NBA 對戰組合的戰績以及球員數據。
* 回傳值有四項，分別是 1,`標題(比分)`、2,`各節分數`、3,`A隊數據`、4,`B隊數據`。
* `po_dcard`、`daily_post` 這兩個 function 為使用 selenium 的方式 PO 文，若無 Dacrd Token 可使用此方式。

#### df_to_png.py
* 將爬取下來的 `Datafrme` 轉成 `png` 圖檔，並存在本地資料夾中。

#### png_to_imgur.py
* 將圖檔上傳至 Imgur 空間，並取得網址回傳。
* 需先至 Imgur 申請 `Client ID`。

#### df_to_table.py
* 將 `get_NBA_result` 所得到的數據 (Dataframe) 轉換成方便在 Dcard 上閱讀的排版。
* `team_statistic_to_table` 處理隊伍數據，Columns 縮減為 `Players`, `MIN`, `REB`, `AST`, `STL`, `BLK`, `PTS` 七項，轉換成全形排版後輸出。
* `game_result_to_table` 處理每節得分，轉換成全形排版後輸出。

#### po_dcard_api.py
* 將爬取到的數據、圖片連結加入 payload ，並以 Dcard API 發文。
* 需先和 Dcard 人員申請 Token。

## get_news_functions
#### get_today_news.py
* `get_today_news_list` 此 function 爬取每日頭條新聞的編號。
* `get_news` 此 function 解析文章，並回傳文章標題、作者與內文。

## Requirements
python 3

## Usage
`1.po_dcard_functions`

```
`1.get data:`
title,game_result,team1,team2 = get_NBA_result(401161524)

`2.content processing:`
content = ''
content += (game_result_to_table(game_result)+'\n'+'\n')
for write_in in (team1,team2):
    content += (team_stat_to_table(write_in)+'\n'+'\n')

`3.post on dcard:`
po_article_api('your_forum',title,content,'your_tag1','your_tag2')

```

`2.get_news_functions`

```
1.get news list:
today_news_ids = get_today_news_list()

2.get news from list
for today_news_id in today_news_ids:
    try:
        title,author,article_content = get_news(today_news_id)
        print(title,author,article_content)
        print('-'*100)
    except:
        pass

```
## Installation
`pip install -r requriements.txt`

