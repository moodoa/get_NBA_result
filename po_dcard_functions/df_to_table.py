def team_statistic_to_table(dataframe):
    dataframe['Players_process'] = dataframe['Players'].apply(lambda x:x.split('/')[0].replace(' ','')[:10])
    process_df = dataframe.head(len(team1)-2)
    process_df = process_df.loc[:,['Players_process', 'MIN', 'REB', 'AST', 'STL', 'BLK', 'PTS']]
    process_df.columns = ['Players', 'MIN', 'REB', 'AST', 'STL', 'BLK', 'PTS']
    article_content = process_df.to_string(index=False)
    article_content = article_content.replace(' ',u'\u3000')
    content_list = article_content.split('\n')
    content_list.insert(1,'='*36)
    return_content = ''
    for sentence in content_list:
        for letter in sentence:
            if ord(letter) != 12288:
                return_content += chr(ord(letter)+65248)
            else:
                return_content += letter
        return_content += '\n'
    return return_content

def game_result_to_table(game_result):
    game_result = game_result.to_string(index=False)
    game_result = game_result.replace(' ',u'\u3000')
    content_list = game_result.split('\n')
    return_result = ''
    for sentence in content_list:
        for letter in sentence:
            if ord(letter) != 12288:
                return_result += chr(ord(letter)+65248)
            else:
                return_result += letter
        return_result += '\n'
    return return_result