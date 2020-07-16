def po_article_api(title,content,tag1,tag2):
    headers = {'Authorization': 'Bearer '+access_token}
    payload = {
        "anonymous": False,
        "withNickname": False,
        "thumbnailIndices": [
            0
        ],
        "title": title,
        "topics": [
            tag1,
            tag2
        ],
        "content": content,
        "layout": "classic"
    }

    po_article = requests.post('https://www.dcard.tw/v2/forums/basketball/posts',headers=headers,json=payload)