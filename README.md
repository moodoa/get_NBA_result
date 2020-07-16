# Get NBA result from ESPN
![alt text](https://miro.medium.com/max/1050/1*ypslG7x_vZF28O9X-l1ZVQ.jpeg)
## Functions
### 
get_NBA_result.py
* 以 `gameid` 為參數爬取 NBA 對戰組合的戰績以及球員數據。
* 回傳值有四項，分別是 1,`標題(比分)`、2,`各節分數`、3,`A隊數據`、4,`B隊數據`。

df_to_png.py
* 將爬取下來的 `Datafrme` 轉成 `png` 圖檔，並存在本地資料夾中。

png_to_imgur
* 將圖檔上傳至 Imgur 空間，並取得網址回傳。
* 需先至 Imgur 申請 `Client ID`。

po_dcard_api
* 將爬取到的數據、圖片連結加入 payload ，並以 Dcard API 發文。
* 需先和 Dcard 人員申請 Token。

## Requirements
python 3

## Installation
`pip install -r requriements.txt`

