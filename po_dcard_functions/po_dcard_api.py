def po_article_api(forum,title,content,tag1,tag2):
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

    po_article = requests.post(f'https://www.dcard.tw/v2/forums/{forum}/posts',headers=headers,json=payload)

    result = json.loads(po_article.content)
    try:
        article_id = str(result['id'])
        return f'https://www.dcard.tw/f/f/p/{article_id}'
    except:
        return result['message']
